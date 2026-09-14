const byId = (id) => document.getElementById(id);
let currentMode = null;

const number = (value, digits = 1) => value === null || value === undefined
  ? "—"
  : Number(value).toFixed(digits);

async function request(path, options) {
  const response = await fetch(path, options);
  if (!response.ok) throw new Error(await response.text());
  return response.json();
}

function jsonPost(body) {
  return { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(body) };
}

function setBadge(element, text, className) {
  element.textContent = text;
  element.className = `badge ${className}`;
}

function renderDevice(name, latest) {
  const on = Boolean(latest?.[name]);
  const state = byId(`${name}State`);
  state.textContent = on ? "ON" : "OFF";
  state.className = `device-state ${on ? "on" : "off"}`;
  byId(`${name}Runtime`).textContent = `Runtime ${number((latest?.[`${name}_runtime_seconds`] || 0) / 60, 1)} min`;
}

function renderStatus(status) {
  const latest = status.latest;
  setBadge(byId("mqttStatus"), status.mqtt_connected ? "MQTT connected" : "MQTT offline", status.mqtt_connected ? "live" : "warning");
  setBadge(byId("dataStatus"), latest ? "Telemetry available" : "Waiting for telemetry", latest ? "live" : "neutral");
  if (!latest) return;

  currentMode = latest.mode;
  byId("occupancy").textContent = latest.occupancy ? "OCCUPIED" : "UNOCCUPIED";
  byId("temperature").textContent = `${number(latest.temperature_c, 1)} °C`;
  byId("lux").textContent = `${number(latest.lux, 0)} lux`;
  byId("lastUpdated").textContent = `Last observation ${new Date(latest.timestamp).toLocaleString()}`;
  ["light", "fan", "cooling"].forEach((name) => renderDevice(name, latest));
  document.querySelectorAll("[data-mode]").forEach((button) => button.classList.toggle("active", button.dataset.mode === currentMode));
  document.querySelectorAll("[data-device]").forEach((button) => { button.disabled = currentMode !== "MANUAL"; });
}

function renderEnergy(energy) {
  byId("smartEnergy").textContent = `${number(energy.smart.total_wh, 2)} Wh`;
  byId("conventionalEnergy").textContent = `${number(energy.conventional.total_wh, 2)} Wh`;
  byId("saving").textContent = `${number(energy.estimated_saving_pct, 1)}%`;
  byId("savingWh").textContent = `${number(energy.estimated_saving_wh, 2)} Wh difference`;
  drawEnergyChart(energy.smart.total_wh, energy.conventional.total_wh);
}

function drawEnergyChart(smart, conventional) {
  const canvas = byId("energyChart");
  const ctx = canvas.getContext("2d");
  const width = canvas.width;
  const height = canvas.height;
  const maximum = Math.max(smart, conventional, 1);
  ctx.clearRect(0, 0, width, height);
  ctx.strokeStyle = "#d8dee7";
  ctx.beginPath(); ctx.moveTo(75, 245); ctx.lineTo(width - 35, 245); ctx.stroke();
  [["SMART", smart, "#1f5b83", 255], ["CONVENTIONAL", conventional, "#75849a", 610]].forEach(([label, value, color, x]) => {
    const barHeight = Number(value) / maximum * 175;
    ctx.fillStyle = color;
    ctx.fillRect(x, 245 - barHeight, 150, barHeight);
    ctx.fillStyle = "#172033";
    ctx.font = "600 18px Segoe UI";
    ctx.textAlign = "center";
    ctx.fillText(`${Number(value).toFixed(2)} Wh`, x + 75, 225 - barHeight);
    ctx.font = "600 15px Segoe UI";
    ctx.fillText(label, x + 75, 275);
  });
}

function renderHistory(rows) {
  const body = byId("historyBody");
  if (!rows.length) {
    body.innerHTML = '<tr><td colspan="9">No measurements available.</td></tr>';
    return;
  }
  body.replaceChildren(...rows.slice(-12).reverse().map((row) => {
    const tr = document.createElement("tr");
    const values = [
      new Date(row.timestamp).toLocaleTimeString(), row.mode,
      row.occupancy ? "Occupied" : "Unoccupied", `${number(row.temperature_c, 1)} °C`,
      number(row.lux, 0), row.light ? "ON" : "OFF", row.fan ? "ON" : "OFF",
      row.cooling ? "ON" : "OFF", `${number(row.estimated_energy_wh, 3)} Wh`,
    ];
    values.forEach((value) => { const td = document.createElement("td"); td.textContent = value; tr.append(td); });
    return tr;
  }));
}

async function refresh() {
  try {
    const [status, history, energy] = await Promise.all([
      request("/api/status"), request("/api/history?limit=100"), request("/api/energy"),
    ]);
    renderStatus(status); renderHistory(history); renderEnergy(energy);
  } catch (error) {
    setBadge(byId("dataStatus"), "Backend unavailable", "warning");
  }
}

document.addEventListener("click", async (event) => {
  const modeButton = event.target.closest("[data-mode]");
  const deviceButton = event.target.closest("[data-device]");
  try {
    if (modeButton) {
      const result = await request("/api/mode", jsonPost({ mode: modeButton.dataset.mode }));
      byId("commandMessage").textContent = result.accepted ? "Mode command sent." : "Broker offline: mode command was not delivered.";
    }
    if (deviceButton) {
      const result = await request("/api/control", jsonPost({
        device: deviceButton.dataset.device,
        state: deviceButton.dataset.state === "true",
      }));
      byId("commandMessage").textContent = result.accepted ? "Manual command sent." : "Broker offline: manual command was not delivered.";
    }
  } catch (error) {
    byId("commandMessage").textContent = "Command failed.";
  }
});

refresh();
window.setInterval(refresh, 2000);
