import { randomUUID } from "node:crypto";
import {
  copyFileSync,
  existsSync,
  lstatSync,
  mkdirSync,
  readFileSync,
  readdirSync,
  renameSync,
  rmSync,
  unlinkSync,
  writeFileSync,
} from "node:fs";
import { basename, dirname, join, resolve } from "node:path";
import { fileURLToPath } from "node:url";


export const FRAMEWORK_ENTRIES = Object.freeze([
  "forgeflow.md",
  "forgeflow.schema.json",
  "adapter",
  "protocol",
  "rules",
  "workflow",
]);
const LEGACY_MANAGED_ENTRIES = Object.freeze([
  "compatibility.md", "conformance", "workflow/tdd.md",
  "adapter/codex/forge-tdd.prompt.md", "adapter/copilot/forge-tdd.prompt.md",
]);
const REQUIRED_CONFIG_KEYS = new Set(["mode", "adapter", "root_artifact_dir"]);
const ALLOWED_CONFIG_KEYS = new Set([
  ...REQUIRED_CONFIG_KEYS,
  "model",
  "execution_timeout_seconds",
]);
const MODULE_DIRECTORY = dirname(fileURLToPath(import.meta.url));
const DEFAULT_PACKAGE_ROOT = resolve(MODULE_DIRECTORY, "../..");


function pathExists(path) {
  try {
    lstatSync(path);
    return true;
  } catch (error) {
    if (error && error.code === "ENOENT") {
      return false;
    }
    throw error;
  }
}


function assertRegularDirectory(path, label) {
  const status = lstatSync(path);
  if (status.isSymbolicLink()) {
    throw new Error(`${label} must not be a symbolic link: ${path}`);
  }
  if (!status.isDirectory()) {
    throw new Error(`${label} must be a directory: ${path}`);
  }
}


function rejectNestedSymlinks(root) {
  assertRegularDirectory(root, "ForgeFlow framework target");
  for (const entry of readdirSync(root, { withFileTypes: true })) {
    const path = join(root, entry.name);
    const status = lstatSync(path);
    if (status.isSymbolicLink()) {
      throw new Error(`Refusing to refresh framework containing symbolic link: ${path}`);
    }
    if (status.isDirectory()) {
      rejectNestedSymlinks(path);
    }
  }
}


function copyEntry(source, target) {
  const status = lstatSync(source);
  if (status.isSymbolicLink()) {
    throw new Error(`Framework package must not contain symbolic links: ${source}`);
  }
  if (status.isDirectory()) {
    mkdirSync(target, { recursive: true });
    for (const entry of readdirSync(source, { withFileTypes: true })) {
      if (entry.name === ".DS_Store") {
        continue;
      }
      copyEntry(join(source, entry.name), join(target, entry.name));
    }
    return;
  }
  if (!status.isFile()) {
    throw new Error(`Unsupported framework package entry: ${source}`);
  }
  mkdirSync(dirname(target), { recursive: true });
  copyFileSync(source, target);
}


function copyFramework(sourceRoot, targetRoot) {
  mkdirSync(targetRoot, { recursive: true });
  for (const entry of FRAMEWORK_ENTRIES) {
    const source = join(sourceRoot, entry);
    if (!pathExists(source)) {
      throw new Error(`Packaged framework entry is missing: ${source}`);
    }
    copyEntry(source, join(targetRoot, entry));
  }
}


function readJsonObject(path, label) {
  let data;
  try {
    data = JSON.parse(readFileSync(path, "utf8"));
  } catch (error) {
    throw new Error(`Unable to read ${label} at ${path}: ${error.message}`);
  }
  if (data === null || Array.isArray(data) || typeof data !== "object") {
    throw new Error(`${label} must contain a JSON object: ${path}`);
  }
  return data;
}


function validateConfig(config) {
  const keys = Object.keys(config);
  const missing = [...REQUIRED_CONFIG_KEYS].filter((key) => !(key in config));
  if (missing.length > 0) {
    throw new Error(`forgeflow.json is missing required fields: ${missing.sort().join(", ")}`);
  }
  const unknown = keys.filter((key) => !ALLOWED_CONFIG_KEYS.has(key));
  if (unknown.length > 0) {
    throw new Error(`forgeflow.json contains unsupported fields: ${unknown.sort().join(", ")}`);
  }
  if (!new Set(["auto", "manual"]).has(config.mode)) {
    throw new Error("mode must be 'auto' or 'manual'");
  }
  if (!new Set(["codex", "copilot"]).has(config.adapter)) {
    throw new Error("adapter must be 'codex' or 'copilot'");
  }
  if (config.root_artifact_dir !== ".forgeflow/artifacts") {
    throw new Error("root_artifact_dir must be the canonical '.forgeflow/artifacts'");
  }
  if (
    config.model !== null
    && (typeof config.model !== "string" || config.model.trim() === "")
  ) {
    throw new Error("model must be a non-empty string or null");
  }
  if (
    typeof config.execution_timeout_seconds !== "number"
    || !Number.isFinite(config.execution_timeout_seconds)
    || config.execution_timeout_seconds <= 0
  ) {
    throw new Error("execution_timeout_seconds must be a positive number");
  }
}


function prepareConfig(templatePath, targetPath, adapter, force) {
  const config = readJsonObject(templatePath, "packaged ForgeFlow configuration");
  if (force && pathExists(targetPath)) {
    const status = lstatSync(targetPath);
    if (status.isSymbolicLink()) {
      throw new Error(`Refusing to replace symbolic-link configuration: ${targetPath}`);
    }
    if (!status.isFile()) {
      throw new Error(`ForgeFlow configuration target must be a file: ${targetPath}`);
    }
    const existing = readJsonObject(targetPath, "existing ForgeFlow configuration");
    for (const key of Object.keys(config)) {
      if (Object.prototype.hasOwnProperty.call(existing, key)) {
        config[key] = existing[key];
      }
    }
  }
  config.adapter = adapter;
  validateConfig(config);
  return config;
}


function writeJsonAtomic(path, data) {
  mkdirSync(dirname(path), { recursive: true });
  const temporary = join(
    dirname(path),
    `.${basename(path)}.${process.pid}.${randomUUID()}.tmp`,
  );
  try {
    writeFileSync(temporary, `${JSON.stringify(data, null, 2)}\n`, "utf8");
    renameSync(temporary, path);
  } catch (error) {
    if (existsSync(temporary)) {
      unlinkSync(temporary);
    }
    throw error;
  }
}


function removeLegacyEntries(frameworkRoot) {
  for (const entry of LEGACY_MANAGED_ENTRIES) {
    const target = join(frameworkRoot, entry);
    if (pathExists(target)) {
      rmSync(target, { recursive: true, force: true });
    }
  }
}


function countFiles(root) {
  const status = lstatSync(root);
  if (status.isFile()) {
    return 1;
  }
  return readdirSync(root).reduce(
    (count, entry) => count + countFiles(join(root, entry)),
    0,
  );
}


function frameworkFileCount(root) {
  return FRAMEWORK_ENTRIES.reduce(
    (count, entry) => count + countFiles(join(root, entry)),
    0,
  );
}


export function installProject({
  projectRoot,
  adapter = "copilot",
  force = false,
  packageRoot = DEFAULT_PACKAGE_ROOT,
}) {
  if (!new Set(["copilot", "codex"]).has(adapter)) {
    throw new Error("adapter must be 'copilot' or 'codex'");
  }

  const project = resolve(projectRoot);
  const packageDirectory = resolve(packageRoot);
  const frameworkSource = join(packageDirectory, ".forgeflow");
  const configSource = join(packageDirectory, "forgeflow.json");
  const frameworkTarget = join(project, ".forgeflow");
  const configTarget = join(project, "forgeflow.json");
  mkdirSync(project, { recursive: true });

  const conflicts = [frameworkTarget, configTarget].filter(pathExists);
  if (conflicts.length > 0 && !force) {
    throw new Error(
      "ForgeFlow project files already exist; use --force to refresh: "
      + conflicts.join(", "),
    );
  }

  if (pathExists(frameworkTarget)) {
    const status = lstatSync(frameworkTarget);
    if (status.isSymbolicLink()) {
      throw new Error(`Refusing to initialize through symbolic link: ${frameworkTarget}`);
    }
    if (!status.isDirectory()) {
      throw new Error(`ForgeFlow framework target must be a directory: ${frameworkTarget}`);
    }
    if (force) {
      rejectNestedSymlinks(frameworkTarget);
    }
  }
  if (pathExists(configTarget) && lstatSync(configTarget).isSymbolicLink()) {
    throw new Error(`Refusing to replace symbolic-link configuration: ${configTarget}`);
  }

  const config = prepareConfig(configSource, configTarget, adapter, force);
  let frameworkAction;
  if (resolve(frameworkSource) === resolve(frameworkTarget)) {
    frameworkAction = "source";
  } else if (pathExists(frameworkTarget)) {
    copyFramework(frameworkSource, frameworkTarget);
    frameworkAction = "refreshed";
  } else {
    const staging = join(project, `.forgeflow.init-${randomUUID()}`);
    try {
      copyFramework(frameworkSource, staging);
      renameSync(staging, frameworkTarget);
    } catch (error) {
      rmSync(staging, { recursive: true, force: true });
      throw error;
    }
    frameworkAction = "created";
  }

  if (force) {
    removeLegacyEntries(frameworkTarget);
  }
  writeJsonAtomic(configTarget, config);

  return {
    project_root: project,
    framework: frameworkAction,
    config: configTarget,
    adapter,
    framework_files: frameworkFileCount(frameworkTarget),
    installer: "npx",
    python_cli_installed: false,
  };
}
