# Start-to-Finish Smart Classroom Implementation Prompt

Copy the prompt below into a new coding-agent session opened at the repository root.

---

## Prompt

You are the lead engineer responsible for completing this Smart Classroom project from its current working baseline to a polished, tested, presentation-ready Release 1.

Work autonomously from start to finish. Do not stop after proposing a plan or creating mockups. Inspect the existing implementation, implement the remaining work, run tests after each meaningful phase, fix regressions, update documentation, and continue until the Definition of Done is satisfied or a genuine external blocker prevents further progress.

### Repository and current baseline

The repository is already organized as a small monorepo:

```text
apps/firmware/     ESP32 PlatformIO firmware and Wokwi files
apps/server/       FastAPI Python package and tests
apps/dashboard/    build-free HTML/CSS/JavaScript dashboard
data/              local SQLite runtime data
infra/             Docker Compose and Mosquitto configuration
docs/              requirements, architecture, design, and validation
scenarios/         demonstration scenarios
```

The structural reorganization is complete. Do not move everything again and do not recreate the old root-level `backend/`, `src/`, `include/`, `test/`, or `mosquitto/` layout.

At the start of this task, the known validation baseline is:

- Server tests: 22 passing.
- ESP32 PlatformIO build: passing.
- The existing dashboard and REST endpoints are functional but still represent the old prototype UI/contract.
- The repository may not have Git metadata. Do not assume rollback through Git is available.

Before making changes, run the baseline commands again and record any difference:

```powershell
uv sync --project apps/server --extra dev
uv run --project apps/server --extra dev pytest -q
uvx platformio run -d apps/firmware
uv run --project apps/server python -m json.tool apps/firmware/diagram.json > $null
```

### Read these sources completely before implementation

Read in this order:

1. `README.md`
2. `docs/requirements.md`
3. `docs/product-design-plan.md`
4. `docs/implementation-blueprint.md`
5. `docs/architecture.md`
6. `docs/test-plan.md`
7. `docs/traceability.md`
8. `docs/energy-experiment.md`
9. Relevant code under `apps/firmware`, `apps/server`, and `apps/dashboard`

The visual reference is:

`docs/assets/dashboard-overview-concept.png`

Use it for hierarchy, spacing, visual tone, and layout. Do not copy inaccurate data from a mockup. The PIR provides boolean/recent-motion occupancy, not a people count.

### Mission

Complete Release 1 across firmware, MQTT, backend, database, real-time communication, dashboard, tests, and documentation.

The result must remain:

- local-first and easy to demonstrate;
- dependency-light;
- safe when networking fails;
- honest that energy is estimated rather than metered;
- understandable to a university reviewer;
- maintainable by another engineer.

### Non-negotiable engineering constraints

1. The ESP32 remains the control and safety authority. Do not move basic automation, hysteresis, delayed shutdown, occupancy handling, or projector cool-down into the server.
2. Local device automation must continue when Wi-Fi, MQTT, the backend, or the dashboard is unavailable.
3. Preserve validated existing behavior unless a requirement explicitly changes it.
4. Do not claim command success when MQTT only accepted a publish. Implement device acknowledgements or telemetry-confirmed completion.
5. Do not claim measured energy. Every energy view/export must say it is estimated from nominal watts × runtime.
6. Do not add unrelated features such as scheduling, billing, machine learning, campus maps, or mobile apps.
7. Keep SQLite, FastAPI, Mosquitto, SSE, and build-free JavaScript for Release 1.
8. Keep secrets out of source. Bind the unauthenticated demo to localhost by default and document its security boundary.
9. Preserve user data. Use migrations for schema changes and never delete/reset the live database merely to make tests pass.
10. Use UTC for stored timestamps and the configured classroom timezone for display.

### Required implementation sequence

#### Phase 1 — characterize and stabilize the current behavior

- Inspect all source and test files.
- Add characterization tests before changing behavior that is not already covered.
- Fix stale imports, dead paths, inconsistent device naming, and documentation references caused by earlier structure changes.
- Format Python, C++, HTML, CSS, and JavaScript consistently.
- Keep `main.cpp` and FastAPI `main.py` limited to application composition/lifecycle.
- Ensure generated directories, databases, secrets, and compiled artifacts remain ignored.

Exit criteria:

- Existing server tests pass.
- Firmware builds.
- The current dashboard loads from `apps/dashboard`.
- Docker Compose paths and local commands are valid.

#### Phase 2 — versioned data and MQTT contracts

Implement and document versioned envelopes for telemetry, commands, acknowledgements, and availability. Follow the contracts in `docs/product-design-plan.md` unless the actual firmware payload size requires a documented adjustment.

Telemetry must include or derive:

- `schemaVersion`
- unique `messageId`, or `(deviceId, bootId, sequence)`
- `deviceId`
- `bootId`
- monotonic `sequence`
- `uptimeMs`
- sensor data
- operating mode
- device state/override/runtime/energy/reason
- network/sensor condition
- backend `receivedAt`

Commands must contain a unique `commandId`, target classroom/device, type, value, and request time.

The ESP32 must publish acknowledgements with:

- matching `commandId`
- `RECEIVED`, `APPLIED`, or `REJECTED`
- actual state and override where applicable
- a concise reason

The server derives `TIMED_OUT` when no terminal acknowledgement/confirmed state arrives within the configured limit.

Use structured topics such as:

```text
smartclassroom/v1/classrooms/{classroomId}/telemetry
smartclassroom/v1/classrooms/{classroomId}/commands
smartclassroom/v1/classrooms/{classroomId}/acknowledgements
smartclassroom/v1/classrooms/{classroomId}/availability
```

Add compatibility only when necessary for a safe migration. Document every topic and payload example in `docs/mqtt-contracts.md`.

Exit criteria:

- Malformed or unknown commands are rejected safely.
- Duplicate telemetry does not create duplicate records.
- Out-of-order samples do not replace the live snapshot.
- Publish, acknowledgement, rejection, and timeout behaviors have automated tests.
- Firmware still operates locally with the broker stopped.

#### Phase 3 — backend application layers and persistence

Finish the package boundaries already started under `apps/server/src/smart_classroom_api`:

```text
api/              HTTP-only request/response handling
domain/           enums, models, freshness, and energy calculations
services/         telemetry, commands, experiments, event hub
infrastructure/   SQLite repositories/migrations and MQTT adapter
```

Requirements:

- `create_app()` supports injected settings, temporary repositories, and a fake MQTT adapter.
- Routes contain no SQL and no direct Paho calls.
- Repositories are the only modules that execute SQL.
- Domain modules import neither FastAPI, sqlite3, nor Paho.
- Replace import-time/global runtime state with lifespan-managed application state.
- Add numbered, idempotent database migrations.
- Enable SQLite foreign keys and WAL mode where appropriate.
- Make telemetry insertion, child device samples, and derived events one transaction.
- Record device events only when state/override/reason changes; do not label every sample as a state change.
- Store the complete command lifecycle.
- Use explicit experiment-run windows/baselines rather than comparing unrelated latest cumulative counters.
- Add structured logs with request ID, classroom/device ID, and command ID.
- Separate liveness from readiness/component health.

Implement the planned schema for:

- `classrooms`
- `telemetry`
- `device_samples`
- `commands`
- `events`
- `experiment_runs`
- `schema_migrations`

Safely migrate the existing database if it exists. Tests must use temporary databases.

Exit criteria:

- A new database initializes automatically.
- An existing database migrates without losing telemetry or actions.
- Services and repositories have focused unit/integration tests.
- No route module owns shared mutable globals.

#### Phase 4 — REST API v1 and typed SSE

Implement `/api/v1` endpoints described in `docs/product-design-plan.md`:

- health/components
- classrooms
- classroom snapshot
- time-range telemetry/history
- filtered cursor-paginated events
- time-window/experiment energy
- asynchronous commands
- command status
- experiment start/stop/results/export
- classroom SSE stream

Keep the current `/api/*` routes as temporary compatibility adapters until the new dashboard and tests use v1. Remove them only if documentation and all consumers are migrated in the same change.

API rules:

- Typed request and response models.
- UTC ISO 8601 timestamps.
- Consistent structured errors with code, message, details, and request ID.
- `202 Accepted` for asynchronous commands.
- `409 Conflict` for conflicting/unsafe operations.
- `422` for validation failures.
- `503` when a required component cannot accept work.
- Explicit pagination and history-range limits.
- Complete OpenAPI descriptions and examples.

Implement typed SSE events:

- `telemetry.updated`
- `device.changed`
- `command.updated`
- `health.updated`
- `experiment.updated`
- `system.notice`

Bound subscriber queues. A slow browser must not crash MQTT ingestion. Coalesce/drop old telemetry updates when necessary, but do not discard command acknowledgements. Support reconnect through event IDs or a full snapshot refresh.

Exit criteria:

- Contract tests cover success and error responses.
- SSE reconnect, keepalive, slow subscriber, queue overflow, and cleanup are tested.
- OpenAPI accurately represents the public API.

#### Phase 5 — implement the complete dashboard design

Implement the final UI under `apps/dashboard` using semantic HTML, modular CSS, JavaScript ES modules, and DOM-safe rendering. Do not introduce React/Vue or a build requirement.

Use a locally vendored subset of Lucide SVG icons. Do not rely on a CDN. Use the exact icon map in `docs/implementation-blueprint.md`.

Required pages:

1. **Overview** — live status, freshness, environment metrics, four device cards, command progress, short trend, and recent meaningful activity.
2. **Trends** — temperature/humidity, estimated lux, occupancy step chart, device timeline/runtime, and energy over selectable ranges.
3. **Experiment** — explicit assumption/disclaimer, session state, AUTO/CONVENTIONAL comparison, durations/sample coverage, device breakdown, reset confirmation, CSV/JSON export.
4. **Activity** — filtered, paginated commands/state/sensor/network/system feed with expandable details.
5. **System** — backend, database, broker, SSE, device freshness, firmware/boot ID, sensor health, and read-only configuration.

Desktop structure:

- 240 px sidebar.
- 80 px header.
- 12-column content grid with 16 px gutters.
- Four environment cards.
- Four equipment cards.
- Eight-column trend panel plus four-column activity panel.

Responsive behavior:

- 72 px icon rail at tablet widths.
- Mobile navigation/drawer below 768 px.
- Two-column cards on tablet and one column on mobile.
- At least 44 × 44 px touch controls.

Visual tokens:

- Background `#0b1220`
- Surface `#111c2e`
- Raised surface `#162338`
- Border `#24324a`
- Primary text `#f3f7fc`
- Muted text `#9bacc2`
- Accent/live `#22d3c5`
- Warning/cooling `#f6b94a`
- Error/offline `#ef6461`
- Information `#7c9cff`

UX requirements:

- Actual device state and override selection are separate.
- Projector `COOLING DOWN` is visually distinct and explains the delay.
- Unknown readings say `Unavailable`, never silently become zero.
- Live, stale, offline, loading, empty, warning, and error states exist for every data component.
- Commands show confirming, sending, awaiting device, applied, rejected, timed out, and disabled states.
- Controls become unavailable when device telemetry is stale/offline unless durable queuing is explicitly implemented.
- Reset and consequential override actions use accessible confirmation dialogs.
- Do not show reset statistics in the global Overview toolbar.
- Do not plot temperature, lux, and occupancy against one unexplained scale.
- Use step charts for occupancy/device states and line charts for continuous sensors.
- While SSE is healthy, do not refetch every resource every five seconds.
- Escape/render all backend text safely; do not inject event strings with `innerHTML`.

Accessibility requirements:

- Complete keyboard navigation and logical focus order.
- Visible focus indicators.
- Status uses icon + text + color, never color alone.
- `aria-pressed` or equivalent semantics for segmented controls.
- Polite announcements only for important state/command changes.
- Chart table/text alternatives.
- Usable at 320 px and 200% zoom.
- Respect reduced-motion preferences.

Exit criteria:

- The five-second comprehension test passes: a user can identify room occupancy, operating mode, connection health, and all equipment states immediately.
- All five pages work with real APIs and explicit empty/error states.
- The UI visually follows `dashboard-overview-concept.png` without inventing unsupported data.

#### Phase 6 — experiment correctness and export

- Create explicit AUTO and CONVENTIONAL experiment runs.
- Capture counter baselines or calculate energy within each run window.
- Store start/end time, duration, sample count, data coverage, baseline assumption, mode, and status.
- Warn when compared durations or coverage differ.
- Calculate total/device Wh, saved Wh, and saving ratio safely.
- Generate reproducible CSV and JSON exports from the backend.
- Include formula, nominal wattages, time range, and assumptions in results/export metadata.

Exit criteria:

- A reviewer can reproduce the displayed comparison from the exported data.
- Zero baseline and incomplete-run cases are tested.
- No surface calls estimated values measured energy.

#### Phase 7 — tests, browser verification, and operational documentation

Add and run:

- domain/service unit tests;
- repository/migration tests;
- API contract tests;
- MQTT reconnect, malformed-message, duplicate, and acknowledgement tests;
- SSE concurrency/reconnect tests;
- frontend component/state tests where practical;
- keyboard/accessibility checks;
- responsive browser checks at 320, 768, 1024, and 1440 px;
- complete telemetry → storage/SSE → command → acknowledgement integration flow;
- existing firmware policy and Wokwi manual matrix.

If an in-app browser or Playwright environment is available, start the local server and inspect every page visually. Test live, stale, offline, empty, warning, error, and pending-command states. Fix layout overflow, console errors, inaccessible controls, chart blur, and incorrect content before declaring completion.

Update:

- `README.md`
- `docs/architecture.md`
- `docs/api.md`
- `docs/mqtt-contracts.md`
- `docs/test-plan.md`
- `docs/traceability.md`
- `docs/energy-experiment.md`
- `docs/validation.md`

Document both native and Docker startup, fresh database initialization, broker failure, Wokwi gateway limitations, test commands, backup procedure, and a presentation script that completes in under five minutes.

### Code-quality rules

- Prefer clear modules and typed boundaries over giant files.
- Do not create catch-all `utils` or `helpers` modules.
- Use descriptive names and one spelling for each domain concept.
- Keep API transport models distinct from persistence rows when they diverge.
- Avoid hidden fallbacks and misleading success messages.
- Do not suppress exceptions without logging actionable context.
- Keep queues bounded and define overflow behavior.
- Do not block firmware loops on network operations.
- Do not make unrelated dependency upgrades unless required to complete the task.
- Preserve compatibility intentionally and remove adapters deliberately.

### Required verification commands

At minimum, finish with:

```powershell
uv run --project apps/server --extra dev pytest -q
uv run --project apps/server python -m compileall apps/server/src
uv run --project apps/server python -m json.tool apps/firmware/diagram.json > $null
uvx platformio run -d apps/firmware
docker compose -f infra/compose.yaml config
```

Also start the server with MQTT disabled and verify `/`, `/docs`, the health endpoint, the snapshot/history endpoints, and static assets over HTTP.

### Definition of Done

Do not call the project complete until all of the following are true:

1. ESP32 local automation, hysteresis, delayed shutdown, overrides, and projector cool-down still work without network services.
2. Telemetry, command, acknowledgement, availability, REST, and SSE contracts are versioned and documented.
3. Commands visibly distinguish requested, published, applied, rejected, and timed-out states.
4. The database initializes/migrates automatically and preserves existing data.
5. Device state events represent actual changes rather than every sample.
6. Energy comparisons use explicit experiment windows and clearly labeled estimates.
7. Overview, Trends, Experiment, Activity, and System pages are complete and responsive.
8. Live/stale/offline and all loading/error/empty states are implemented.
9. Keyboard, focus, contrast, reduced motion, touch target, and chart-alternative requirements pass.
10. Automated tests, firmware build, JSON validation, Docker configuration, and available browser verification pass.
11. Documentation and traceability match the final implementation and no stale path remains.
12. The entire demo can be started and explained in under five minutes without a paid cloud service.

### Working behavior

- Begin with a concise audit and working checklist, then implement immediately.
- Make safe assumptions that preserve the documented Release 1 scope.
- Do not repeatedly ask for preferences already settled in the design documents.
- If an external dependency is unavailable, document the exact limitation, continue every independent task, and provide the precise command needed to verify it later.
- Preserve unrelated files and user data.
- After each phase, run focused tests before moving forward.
- Keep `docs/validation.md` current with commands, dates, outcomes, and genuine limitations.

### Final response format

When the Definition of Done is satisfied, report:

1. The completed product behavior.
2. The most important firmware, server, database, API, and UI changes.
3. Exact verification results and any warnings.
4. Exact commands to run the project and demonstration.
5. Remaining physical-hardware or external-service limitations only—do not list unfinished in-scope software work as “future work.”

---

