#!/usr/bin/env node
import fs from "node:fs";
import path from "node:path";
import { spawn } from "node:child_process";
import { fileURLToPath } from "node:url";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const mockDir = path.resolve(__dirname, "..");
const appRoot = path.resolve(mockDir, "..");
const deliveryDir = path.resolve(appRoot, "delivery-1");
const publicDir = path.resolve(mockDir, "public");
const bootstrapFile = path.resolve(publicDir, "__fixture_bootstrap__.json");

function parseArgs(argv) {
  const out = {
    task: null,
    fixture: null,
    auto: false,
    dryRun: false,
    viteArgs: [],
  };

  for (let i = 0; i < argv.length; i += 1) {
    const arg = argv[i];
    if (arg === "--task") {
      out.task = argv[i + 1] ?? null;
      i += 1;
      continue;
    }
    if (arg === "--fixture") {
      out.fixture = argv[i + 1] ?? null;
      i += 1;
      continue;
    }
    if (arg === "--auto") {
      out.auto = true;
      continue;
    }
    if (arg === "--dry-run") {
      out.dryRun = true;
      continue;
    }
    out.viteArgs.push(arg);
  }

  return out;
}

function normalizeTaskName(taskRaw) {
  if (!taskRaw) return null;
  const trimmed = String(taskRaw).trim();
  if (/^task_\d+$/i.test(trimmed)) return trimmed.toLowerCase();
  if (/^\d+$/.test(trimmed)) return `task_${trimmed.padStart(2, "0")}`;
  return `task_${trimmed}`;
}

function findFixtureFiles() {
  if (!fs.existsSync(deliveryDir)) return [];
  const dirs = fs.readdirSync(deliveryDir, { withFileTypes: true });
  const files = [];
  for (const d of dirs) {
    if (!d.isDirectory()) continue;
    if (!/^task_\d+$/i.test(d.name)) continue;
    const fixturePath = path.resolve(deliveryDir, d.name, "fixture.json");
    if (fs.existsSync(fixturePath)) files.push(fixturePath);
  }
  files.sort();
  return files;
}

function resolveFixturePath(options) {
  if (options.fixture) {
    const p = path.isAbsolute(options.fixture)
      ? options.fixture
      : path.resolve(process.cwd(), options.fixture);
    if (!fs.existsSync(p)) {
      throw new Error(`--fixture path does not exist: ${p}`);
    }
    return p;
  }

  const fixtures = findFixtureFiles();
  if (options.task) {
    const taskName = normalizeTaskName(options.task);
    const match = fixtures.find((p) =>
      p.toLowerCase().includes(`${path.sep}${taskName}${path.sep}`)
    );
    if (!match) {
      throw new Error(`No fixture.json found for ${taskName} in ${deliveryDir}`);
    }
    return match;
  }

  if (options.auto || fixtures.length === 1) {
    if (fixtures.length === 0) {
      throw new Error(`No fixture.json files found under ${deliveryDir}`);
    }
    if (fixtures.length > 1) {
      const list = fixtures.map((p) => `- ${path.relative(appRoot, p)}`).join("\n");
      throw new Error(
        `Multiple fixtures found; choose one with --task or --fixture:\n${list}`
      );
    }
    return fixtures[0];
  }

  throw new Error(
    "Provide one of: --task <NN>, --fixture <path>, or --auto.\n" +
      "Examples:\n" +
      "  npm run dev:fixture -- --task 51\n" +
      "  npm run dev:fixture -- --fixture ../delivery-1/task_51/fixture.json\n" +
      "  npm run dev:fixture -- --auto"
  );
}

function validateFixtureJson(raw, fixturePath) {
  let parsed;
  try {
    parsed = JSON.parse(raw);
  } catch (err) {
    throw new Error(`Invalid JSON in ${fixturePath}: ${String(err)}`);
  }
  if (!parsed || typeof parsed !== "object") {
    throw new Error(`Fixture must be a JSON object: ${fixturePath}`);
  }
  if (!parsed.frame || !Array.isArray(parsed.layers)) {
    throw new Error(`Fixture missing required keys {frame, layers}: ${fixturePath}`);
  }
  return JSON.stringify(parsed, null, 2);
}

function writeBootstrapFixture(fixturePath) {
  const raw = fs.readFileSync(fixturePath, "utf-8");
  const normalized = validateFixtureJson(raw, fixturePath);
  fs.mkdirSync(publicDir, { recursive: true });
  fs.writeFileSync(bootstrapFile, normalized, "utf-8");
}

function startVite(viteArgs) {
  const cmd = process.platform === "win32" ? "npx.cmd" : "npx";
  const child = spawn(cmd, ["vite", ...viteArgs], {
    cwd: mockDir,
    stdio: "inherit",
    env: {
      ...process.env,
      VITE_AUTO_FIXTURE: "1",
    },
  });
  child.on("exit", (code, signal) => {
    if (signal) process.kill(process.pid, signal);
    process.exit(code ?? 0);
  });
}

function main() {
  const args = parseArgs(process.argv.slice(2));
  const fixturePath = resolveFixturePath(args);
  writeBootstrapFixture(fixturePath);

  const relFixture = path.relative(appRoot, fixturePath);
  const relBootstrap = path.relative(appRoot, bootstrapFile);
  console.log(`[fixture] loaded source: ${relFixture}`);
  console.log(`[fixture] wrote bootstrap: ${relBootstrap}`);

  if (args.dryRun) return;
  startVite(args.viteArgs);
}

try {
  main();
} catch (err) {
  console.error(String(err instanceof Error ? err.message : err));
  process.exit(1);
}
