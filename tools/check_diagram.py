"""Check diagrams and exercise the actual WASM graphics with a minimal API host.

Run: uv run --with wasmtime==44.0.0 python tools/check_diagram.py
This does not replace a Wokwi electrical/interactive simulation.
"""
import json
from pathlib import Path
import struct
import tomllib
import zlib

import wasmtime

ROOT = Path(__file__).resolve().parents[1]
CHIPS = ROOT / "apps/firmware/chips"


def check_diagrams():
    source = ROOT / "apps/firmware/diagram.json"
    assert source.read_bytes() == (ROOT / "diagram.json").read_bytes(), "Diagram copies differ"
    diagram = json.loads(source.read_text())
    parts = {p["id"]: p for p in diagram["parts"]}
    assert len(parts) == len(diagram["parts"]), "Duplicate part ID"
    pins = {
        "wokwi-dht22": {"VCC", "GND", "SDA"},
        "wokwi-pir-motion-sensor": {"VCC", "GND", "OUT"},
        "wokwi-photoresistor-sensor": {"VCC", "GND", "AO", "DO"},
        "wokwi-relay-module": {"VCC", "GND", "IN", "COM", "NO", "NC"},
        "chip-appliance": set(json.loads((CHIPS / "appliance.chip.json").read_text())["pins"]),
        "board-esp32-devkit-c-v4": {"3V3", "5V.1", "GND.1", "GND.2", "13", "15", "34", "21", "22", "23"},
    }
    edges = {frozenset(c[:2]) for c in diagram["connections"]}
    for a, b, *_ in diagram["connections"]:
        for endpoint in (a, b):
            name, pin = endpoint.split(":")
            assert name in parts, endpoint
            assert pin in pins[parts[name]["type"]], endpoint
    for name, gpio, kind in [("Light", 21, 0), ("Fan", 22, 1), ("Cooling", 23, 2)]:
        assert frozenset((f"esp32:{gpio}", f"relay{name}:IN")) in edges
        assert frozenset((f"relay{name}:NO", f"load{name}:SW")) in edges
        assert int(parts[f"load{name}"]["attrs"]["kind"]) == kind
    assert not any("projector" in p.lower() for p in parts)
    assert not any(p["type"] == "wokwi-led" for p in parts.values())
    firmware_paths = []
    for config in [ROOT / "wokwi.toml", ROOT / "apps/firmware/wokwi.toml"]:
        data = tomllib.loads(config.read_text())
        binary = config.parent / data["chip"][0]["binary"]
        assert binary.resolve() == (CHIPS / "appliance.chip.wasm").resolve()
        assert binary.exists() and binary.with_suffix(".json").exists()
        configured = tuple((config.parent / data["wokwi"][field]).resolve()
                           for field in ("firmware", "elf"))
        expected = tuple((ROOT / "apps/firmware/.pio/build/esp32dev" / filename).resolve()
                         for filename in ("firmware.bin", "firmware.elf"))
        assert configured == expected, "Configuration points to the wrong firmware build"
        firmware_paths.extend(configured)
    print(f"PASS: identical diagrams, {len(parts)} parts, valid connections and consistent build paths")
    if not all(path.is_file() for path in firmware_paths):
        print("NOTE: ESP32 build artifacts are absent; run pio run -d apps/firmware before simulation")


def write_png(path, rgba):
    def chunk(tag, data):
        return struct.pack(">I", len(data)) + tag + data + struct.pack(">I", zlib.crc32(tag + data))
    rows = b"".join(b"\0" + rgba[y*960:(y+1)*960] for y in range(160))
    path.write_bytes(b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", 240, 160, 8, 6, 0, 0, 0))
                     + chunk(b"IDAT", zlib.compress(rows)) + chunk(b"IEND", b""))


def check_visual(kind, name):
    engine = wasmtime.Engine()
    module = wasmtime.Module.from_file(engine, str(CHIPS / "appliance.chip.wasm"))
    store = wasmtime.Store(engine)
    linker = wasmtime.Linker(engine)
    state = {"on": 0, "frame": None, "frames": {}, "modes": {}, "watch": None, "timer": None}

    def memory(caller):
        return caller.get("memory") or imported_memory

    def read_string(caller, ptr):
        buf = memory(caller).read(caller, ptr, ptr+80)
        return bytes(buf).split(b"\0")[0].decode()

    def pin_init(caller, ptr, mode):
        pin = read_string(caller, ptr)
        state["modes"][pin] = mode
        return 1 if pin == "SW" else 2

    def watch(caller, pin, ptr):
        state["watch"] = struct.unpack("<III", memory(caller).read(caller, ptr, ptr+12))
        return 1

    def timer(caller, ptr):
        state["timer"] = struct.unpack("<II", memory(caller).read(caller, ptr, ptr+8))
        return 1

    def framebuffer(caller, w, h):
        memory(caller).write(caller, struct.pack("<I", 240), w)
        memory(caller).write(caller, struct.pack("<I", 160), h)
        handle = len(state["frames"]) + 1
        state["frames"][handle] = None
        return handle

    def buffer_write(caller, buf, offset, ptr, length):
        assert offset == 0 and length == 240*160*4
        state["frame"] = bytes(memory(caller).read(caller, ptr, ptr+length))
        state["frames"][buf] = state["frame"]

    callbacks = {
        "pinInit": pin_init, "pinRead": lambda caller, pin: state["on"],
        "pinWatch": watch, "attrInit": lambda caller, ptr, default: 1,
        "attrRead": lambda caller, attr: kind,
        "framebufferInit": framebuffer, "bufferWrite": buffer_write,
        "timerInit": timer, "timerStart": lambda caller, *args: None,
    }
    imported_memory = None
    for imp in module.imports:
        if isinstance(imp.type, wasmtime.MemoryType):
            assert imp.type.limits.min <= 64, "Custom chip exceeds Wokwi's 64-page memory limit"
            imported_memory = wasmtime.Memory(store, imp.type)
            linker.define(store, imp.module, imp.name, imported_memory)
        else:
            assert imp.name in callbacks, f"Unexpected import {imp.module}.{imp.name}"
            linker.define(store, imp.module, imp.name,
                          wasmtime.Func(store, imp.type, callbacks[imp.name], access_caller=True))
    instance = linker.instantiate(store, module)
    exports = instance.exports(store)
    exports["chipInit"](store)
    assert state["modes"]["SW"] == 3, "Open relay must use INPUT_PULLDOWN"
    off = state["frame"]
    assert off is not None
    table = exports["__indirect_function_table"]
    userdata, edge, callback = state["watch"]
    assert edge == 3, "Must observe both relay transitions"
    state["on"] = 1
    table.get(store, callback)(store, userdata, 1, 1)
    on = state["frame"]
    assert on != off, "Relay HIGH must change visual"
    timerdata, timercallback = state["timer"]
    table.get(store, timercallback)(store, timerdata)
    assert (state["frame"] != on) == (kind != 0), "Only fan/cooling should animate"
    state["on"] = 0
    table.get(store, callback)(store, userdata, 1, 0)
    assert state["frame"] == off, "Open relay must restore OFF graphic"
    table.get(store, timercallback)(store, timerdata)
    assert state["frame"] == off, "OFF animation must stop"
    # Wokwi may initialize all three appliances inside one WASM instance.
    # A single global struct passes isolated tests but changes the wrong display.
    exports["chipInit"](store)
    second_userdata = state["watch"][0]
    exports["chipInit"](store)
    third_userdata = state["watch"][0]
    assert len({userdata, second_userdata, third_userdata}) == 3, "Appliances share mutable state"
    table.get(store, callback)(store, userdata, 1, 1)
    assert state["frames"][1] == on, "First relay must update its own display"
    assert state["frames"][2] == off and state["frames"][3] == off, "Other appliances must stay OFF"
    table.get(store, callback)(store, userdata, 1, 0)
    preview = ROOT / "docs/assets/appliances"
    preview.mkdir(parents=True, exist_ok=True)
    write_png(preview / f"{name}-off.png", off)
    write_png(preview / f"{name}-on.png", on)
    print(f"PASS: {name} relay transitions, animation, OFF state and three-instance isolation")


if __name__ == "__main__":
    check_diagrams()
    for kind, name in enumerate(["light", "fan", "cooling"]):
        check_visual(kind, name)
