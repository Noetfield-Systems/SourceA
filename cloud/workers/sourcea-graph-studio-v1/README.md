# sourcea-graph-studio-v1

Graph Studio Worker + DO. Validate / publish / run pinned plans via service binding to `sourcea-executive-governor-v1`.

Endpoints:

- `GET /health`
- `GET /v1/registry`
- `GET /v1/blueprints/golden`
- `POST /v1/blueprints/validate`
- `POST /v1/blueprints/publish`
- `POST /v1/runs` (requires `plan_hash`)
- `GET /v1/runs/:id`

Law: never execute React Flow JSON; layout stays out of `plan_hash`.
