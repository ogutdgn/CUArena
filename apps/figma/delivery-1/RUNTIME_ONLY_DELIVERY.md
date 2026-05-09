# Runtime-Only Delivery (No Source Checkout Needed)

This mode ships prebuilt Docker images and a tiny runtime wrapper so the client runs the environment without receiving the repo source tree directly.

Important: Docker images are not a cryptographic code-protection boundary. A determined recipient can still inspect image layers. This setup removes plain-source handoff and keeps usage host-command driven.

## Producer steps (internal)

From `apps/figma/`:

```bash
./scripts/package_runtime_delivery.sh
```

This creates:

- `runtime-delivery_<timestamp>/`
- `runtime-delivery_<timestamp>.tar.gz`

## What to hand off

Send only:

- `runtime-delivery_<timestamp>.tar.gz`

Do not send the repository checkout.

## Client steps

```bash
tar -xzf runtime-delivery_<timestamp>.tar.gz
cd runtime-delivery_<timestamp>
./run_host.sh load-images
./run_host.sh up
```

Open:

- `http://127.0.0.1:5173`

If port `5173` is busy, edit `.env` in the runtime folder:

```bash
FIGMA_HOST_PORT=5174
```

Then run `./run_host.sh up` again and open `http://127.0.0.1:5174`.

After agent/user actions, score a task:

```bash
./run_host.sh score task_01
```

Optional session-pinned score:

```bash
./run_host.sh score task_01 --session-id <session_uuid>
```

Stop services:

```bash
./run_host.sh down
```

## Runtime outputs

Outputs persist on host under:

- `out/logs/`
- `out/scores/`

No source mounts are used in this runtime compose.
