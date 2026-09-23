import assert from "node:assert/strict";
import { execFileSync, spawnSync } from "node:child_process";
import {
  existsSync,
  lstatSync,
  mkdirSync,
  mkdtempSync,
  readFileSync,
  rmSync,
  symlinkSync,
  writeFileSync,
} from "node:fs";
import { tmpdir } from "node:os";
import { delimiter, dirname, join, resolve } from "node:path";
import { fileURLToPath } from "node:url";
import test from "node:test";


const TEST_DIRECTORY = dirname(fileURLToPath(import.meta.url));
const REPOSITORY_ROOT = resolve(TEST_DIRECTORY, "../..");
const CLI_PATH = join(REPOSITORY_ROOT, "npm", "bin", "forgeflow.js");


function temporaryProject(testContext) {
  const project = mkdtempSync(join(tmpdir(), "forgeflow-npx-test-"));
  testContext.after(() => rmSync(project, { recursive: true, force: true }));
  return project;
}


function runInstaller(project, ...arguments_) {
  return spawnSync(process.execPath, [CLI_PATH, ...arguments_], {
    cwd: project,
    encoding: "utf8",
  });
}


function readJson(path) {
  return JSON.parse(readFileSync(path, "utf8"));
}


test("initializes a Copilot project without installing a Node runtime CLI", (testContext) => {
  const project = temporaryProject(testContext);
  const result = runInstaller(project, "init");

  assert.equal(result.status, 0, result.stderr);
  const summary = JSON.parse(result.stdout);
  assert.equal(summary.adapter, "copilot");
  assert.equal(summary.framework, "created");
  assert.equal(summary.installer, "npx");
  assert.equal(summary.python_cli_installed, false);
  assert.ok(summary.framework_files > 0);
  assert.equal(readJson(join(project, "forgeflow.json")).adapter, "copilot");
  assert.equal(lstatSync(join(project, ".forgeflow", "forgeflow.md")).isFile(), true);
});


test("installs the selected Codex adapter in project configuration", (testContext) => {
  const project = temporaryProject(testContext);
  const result = runInstaller(project, "init", "--adapter", "codex");

  assert.equal(result.status, 0, result.stderr);
  assert.equal(readJson(join(project, "forgeflow.json")).adapter, "codex");
});

test("refresh removes retired TDD launchers and preserves legacy project evidence", (testContext) => {
  const project = temporaryProject(testContext);
  assert.equal(runInstaller(project, "init").status, 0);
  const root = join(project, ".forgeflow");
  for (const name of ["workflow/tdd.md", "adapter/codex/forge-tdd.prompt.md", "adapter/copilot/forge-tdd.prompt.md"]) {
    writeFileSync(join(root, name), "retired framework file");
  }
  mkdirSync(join(root, "artifacts"), { recursive: true });
  const evidence = join(root, "artifacts/tdd-feature-01-slice-01.md");
  writeFileSync(evidence, "original legacy evidence");
  const result = runInstaller(project, "init", "--force");
  assert.equal(result.status, 0, result.stderr);
  for (const name of ["workflow/tdd.md", "adapter/codex/forge-tdd.prompt.md", "adapter/copilot/forge-tdd.prompt.md"]) {
    assert.equal(existsSync(join(root, name)), false);
  }
  assert.equal(readFileSync(evidence, "utf8"), "original legacy evidence");
  for (const name of ["protocol/transition.md", "protocol/review-recovery.md", "workflow/implement.md"]) {
    assert.equal(existsSync(join(root, name)), true);
  }
});


test("refuses existing project files without force", (testContext) => {
  const project = temporaryProject(testContext);
  assert.equal(runInstaller(project, "init").status, 0);
  const planningPath = join(project, ".forgeflow", "forgeflow.md");
  const before = readFileSync(planningPath, "utf8");

  const result = runInstaller(project, "init");

  assert.equal(result.status, 1);
  assert.match(result.stderr, /use --force to refresh/);
  assert.equal(readFileSync(planningPath, "utf8"), before);
});


test("force refreshes managed files and preserves project-owned evidence and config", (testContext) => {
  const project = temporaryProject(testContext);
  assert.equal(runInstaller(project, "init").status, 0);

  const frameworkRoot = join(project, ".forgeflow");
  const promptPath = join(frameworkRoot, "adapter", "copilot", "forge-plan.prompt.md");
  writeFileSync(promptPath, "stale managed prompt\n", "utf8");
  mkdirSync(join(frameworkRoot, "artifacts"), { recursive: true });
  writeFileSync(join(frameworkRoot, "artifacts", "planning.md"), "project evidence\n");
  mkdirSync(join(frameworkRoot, "reports", "custom"), { recursive: true });
  writeFileSync(join(frameworkRoot, "reports", "custom", "report.md"), "report evidence\n");
  mkdirSync(join(frameworkRoot, "runtime"), { recursive: true });
  writeFileSync(join(frameworkRoot, "runtime", "state.json"), "{}\n");
  mkdirSync(join(frameworkRoot, "rules", "reviews", "custom-plugin"), { recursive: true });
  writeFileSync(
    join(frameworkRoot, "rules", "reviews", "custom-plugin", "rules.md"),
    "# Custom rules\n",
  );
  writeFileSync(join(frameworkRoot, "compatibility.md"), "legacy\n");
  mkdirSync(join(frameworkRoot, "conformance"), { recursive: true });
  writeFileSync(join(frameworkRoot, "conformance", "legacy.md"), "legacy\n");
  writeFileSync(
    join(project, "forgeflow.json"),
    `${JSON.stringify({
      mode: "manual",
      adapter: "copilot",
      model: "test-model",
      execution_timeout_seconds: 42,
      root_artifact_dir: ".forgeflow/artifacts",
      ignored_unknown_key: "removed",
    }, null, 2)}\n`,
  );

  const result = runInstaller(project, "init", "--adapter", "codex", "--force");

  assert.equal(result.status, 0, result.stderr);
  const config = readJson(join(project, "forgeflow.json"));
  assert.deepEqual(config, {
    mode: "manual",
    adapter: "codex",
    model: "test-model",
    execution_timeout_seconds: 42,
    root_artifact_dir: ".forgeflow/artifacts",
  });
  assert.match(readFileSync(promptPath, "utf8"), /ForgeFlow Plan Launcher/);
  assert.equal(readFileSync(join(frameworkRoot, "artifacts", "planning.md"), "utf8"), "project evidence\n");
  assert.equal(readFileSync(join(frameworkRoot, "reports", "custom", "report.md"), "utf8"), "report evidence\n");
  assert.equal(readFileSync(join(frameworkRoot, "runtime", "state.json"), "utf8"), "{}\n");
  assert.equal(
    readFileSync(join(frameworkRoot, "rules", "reviews", "custom-plugin", "rules.md"), "utf8"),
    "# Custom rules\n",
  );
  assert.equal(existsSync(join(frameworkRoot, "compatibility.md")), false);
  assert.equal(existsSync(join(frameworkRoot, "conformance")), false);
});


test("validates config before changing managed files", (testContext) => {
  const project = temporaryProject(testContext);
  assert.equal(runInstaller(project, "init").status, 0);
  const promptPath = join(project, ".forgeflow", "adapter", "copilot", "forge-plan.prompt.md");
  writeFileSync(promptPath, "must remain unchanged\n", "utf8");
  const config = readJson(join(project, "forgeflow.json"));
  config.mode = "invalid";
  writeFileSync(join(project, "forgeflow.json"), `${JSON.stringify(config, null, 2)}\n`);

  const result = runInstaller(project, "init", "--force");

  assert.equal(result.status, 1);
  assert.match(result.stderr, /mode must be/);
  assert.equal(readFileSync(promptPath, "utf8"), "must remain unchanged\n");
});


test("rejects Node implementations of Python CLI commands", (testContext) => {
  const project = temporaryProject(testContext);
  for (const command of ["plan", "run", "status", "knowledge", "reset", "handoff"]) {
    const result = runInstaller(project, command);
    assert.equal(result.status, 1);
    assert.match(result.stderr, /supports installation only/);
    assert.ok(result.stderr.includes(`npx ${readJson(join(REPOSITORY_ROOT, "package.json")).name} init`));
  }
});


test("prints installer-only help without modifying the project", (testContext) => {
  const project = temporaryProject(testContext);
  const result = runInstaller(project, "--help");

  assert.equal(result.status, 0, result.stderr);
  assert.match(result.stdout, /installs or refreshes ForgeFlow project files only/);
  assert.match(result.stdout, /Python 'forge' CLI/);
  assert.ok(result.stdout.includes(`npx ${readJson(join(REPOSITORY_ROOT, "package.json")).name} init`));
  assert.equal(runInstaller(project, "--version").stdout.trim(), "0.1.0");
});


test("rejects symbolic links during force refresh", {
  skip: process.platform === "win32",
}, (testContext) => {
  const project = temporaryProject(testContext);
  assert.equal(runInstaller(project, "init").status, 0);
  const external = temporaryProject(testContext);
  symlinkSync(external, join(project, ".forgeflow", "linked"));

  const result = runInstaller(project, "init", "--force");

  assert.equal(result.status, 1);
  assert.match(result.stderr, /containing symbolic link/);
});


test("the Python CLI remains available from the Python package", () => {
  const pythonPath = [
    join(REPOSITORY_ROOT, "src"),
    process.env.PYTHONPATH,
  ].filter(Boolean).join(delimiter);
  const output = execFileSync(
    process.env.PYTHON || "python3",
    ["-m", "forgeflow", "--help"],
    {
      cwd: REPOSITORY_ROOT,
      encoding: "utf8",
      env: { ...process.env, PYTHONPATH: pythonPath },
    },
  );

  assert.match(output, /ForgeFlow CLI/);
  assert.match(output, /plan/);
  assert.match(output, /run/);
  assert.match(output, /status/);
});
