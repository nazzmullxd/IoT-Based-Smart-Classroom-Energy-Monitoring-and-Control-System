import { api, jsonRequest } from "./api-client.js";
import { drawHistoryChart } from "./history-chart.js";


const deviceNames = ["ac", "fan", "lights", "projector"];
const byId = (id) => document.getElementById(id);
const formatNumber = (value, digits = 1) => Number(value || 0).toFixed(digits);


function addDetail(list, label, value) {
  const term = document.createElement("dt");
  term.textContent = label;
  const description = document.createElement("dd");
  description.textContent = value;
  list.append(term, description);
}


function createDeviceCard(name, data) {
  const card = document.createElement("article");
  card.className = "device";

  const header = document.createElement("header");
  const title = document.createElement("h3");
  title.textContent = name;
  const state = document.createElement("span");
  state.className = `state ${(data.state || "off").toLowerCase()}`;
  state.textContent = data.state || "OFF";
  header.append(title, state);

  const details = document.createElement("dl");
  addDetail(details, "Override", data.override || "AUTO");
  addDetail(details, "Runtime", `${formatNumber((data.runtimeSeconds || 0) / 60)} min`);
  addDetail(details, "Estimated", `${formatNumber(data.estimatedEnergyWh, 2)} Wh`);

  const controls = document.createElement("div");
  controls.className = "controls";
  for (const value of ["AUTO", "FORCE_ON", "FORCE_OFF"]) {
    const button = document.createElement("button");
    button.type = "button";
    button.dataset.device = name;
    button.dataset.override = value;
    button.textContent = value.replace("FORCE_", "");
    controls.append(button);
  }

  card.append(header, details, controls);
  return card;
}


function render(data) {
  if (!data) return;

  const connection = byId("connection");
  connection.textContent = `Live · ${data.network?.mqtt ? "MQTT connected" : "local telemetry"}`;
  connection.className = "pill";
  byId("temperature").textContent = data.temperatureC == null ? "—" : formatNumber(data.temperatureC);
  byId("humidity").textContent = data.humidityPct == null ? "—" : formatNumber(data.humidityPct);
  byId("lux").textContent = formatNumber(data.illuminanceLux, 0);
  byId("occupancy").textContent = data.occupied ? "OCCUPIED" : "EMPTY";
  byId("sensorStatus").textContent = data.sensorError ? "Sensor warning" : "Sensors nominal";

  const devices = byId("devices");
  devices.replaceChildren(
    ...deviceNames.map((name) => createDeviceCard(name, data.devices?.[name] || {})),
  );
}


async function control(device, value) {
  await api(`/api/control/${device}`, jsonRequest("POST", { value }));
  await loadEvents();
}


async function loadEnergy() {
  const energy = await api("/api/energy");
  byId("autoEnergy").textContent = `${formatNumber(energy.automatedWh, 2)} Wh`;
  byId("baseEnergy").textContent = `${formatNumber(energy.conventionalWh, 2)} Wh`;
  byId("savedEnergy").textContent = `${formatNumber(energy.savedWh, 2)} Wh`;
  byId("ratio").textContent = `${formatNumber(energy.savingRatioPct)}%`;
}


async function loadEvents() {
  const rows = await api("/api/events?limit=30");
  const container = byId("events");
  if (rows.length === 0) {
    container.textContent = "No events yet";
    return;
  }

  container.replaceChildren(...rows.map((row) => {
    const event = document.createElement("div");
    event.className = "event";
    const message = document.createElement("strong");
    message.textContent = row.message;
    const metadata = document.createElement("small");
    metadata.textContent = `${row.type} · ${new Date(row.timestamp).toLocaleTimeString()}`;
    event.append(message, metadata);
    return event;
  }));
}


async function refresh() {
  try {
    const [status, history] = await Promise.all([
      api("/api/status"),
      api("/api/telemetry/history?limit=80"),
    ]);
    render(status.latest);
    drawHistoryChart(byId("chart"), history);
    await Promise.all([loadEnergy(), loadEvents()]);
  } catch (error) {
    console.warn(error);
  }
}


document.addEventListener("click", async (event) => {
  const controlButton = event.target.closest("[data-device][data-override]");
  if (controlButton) {
    await control(controlButton.dataset.device, controlButton.dataset.override);
  }
});

document.querySelectorAll("[data-mode]").forEach((button) => {
  button.addEventListener("click", () => api(
    "/api/mode",
    jsonRequest("POST", { mode: button.dataset.mode }),
  ));
});

byId("reset").addEventListener("click", () => api(
  "/api/reset",
  jsonRequest("POST", { target: "ALL" }),
));

refresh();
setInterval(refresh, 5000);

const eventSource = new EventSource("/api/stream");
eventSource.onmessage = (event) => {
  render(JSON.parse(event.data));
  loadEnergy();
};
