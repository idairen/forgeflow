#!/usr/bin/env node

import { readFileSync } from "node:fs";
import { dirname, join, resolve } from "node:path";
import { fileURLToPath } from "node:url";

import { installProject } from "../lib/installer.js";


const PACKAGE_ROOT = resolve(dirname(fileURLToPath(import.meta.url)), "../..");
const PACKAGE_METADATA = JSON.parse(
  readFileSync(join(PACKAGE_ROOT, "package.json"), "utf8"),
);
const PACKAGE_NAME = PACKAGE_METADATA.name;
const PACKAGE_VERSION = PACKAGE_METADATA.version;


function printHelp() {
  console.log(`ForgeFlow npx installer

Usage:
  npx ${PACKAGE_NAME} init [--adapter copilot|codex] [--force]

Options:
  -a, --adapter <name>  IDE adapter to install (default: copilot)
      --force           Refresh managed framework files in an existing project
  -h, --help            Show this help message
  -v, --version         Show the npm installer version

This package installs or refreshes ForgeFlow project files only.
Use the Python 'forge' CLI for plan, run, status, knowledge, reset, and handoff commands.`);
}


function parseArguments(argv) {
  if (argv.length === 0 || argv.includes("--help") || argv.includes("-h")) {
    return { help: true };
  }
  if (argv.length === 1 && (argv[0] === "--version" || argv[0] === "-v")) {
    return { version: true };
  }
  if (argv[0] !== "init") {
    throw new Error(
      "The npx package supports installation only. "
      + `Use 'npx ${PACKAGE_NAME} init' or the Python 'forge' CLI.`
    );
  }

  let adapter = "copilot";
  let force = false;
  for (let index = 1; index < argv.length; index += 1) {
    const argument = argv[index];
    if (argument === "--force") {
      force = true;
      continue;
    }
    if (argument === "--adapter" || argument === "-a") {
      index += 1;
      if (index >= argv.length) {
        throw new Error(`${argument} requires 'copilot' or 'codex'`);
      }
      adapter = argv[index];
      continue;
    }
    throw new Error(`Unsupported npx installer argument: ${argument}`);
  }

  if (!new Set(["copilot", "codex"]).has(adapter)) {
    throw new Error("adapter must be 'copilot' or 'codex'");
  }
  return { adapter, force };
}


function main() {
  const options = parseArguments(process.argv.slice(2));
  if (options.help) {
    printHelp();
    return 0;
  }
  if (options.version) {
    console.log(PACKAGE_VERSION);
    return 0;
  }

  const result = installProject({
    projectRoot: process.cwd(),
    adapter: options.adapter,
    force: options.force,
  });
  console.log(JSON.stringify(result, null, 2));
  return 0;
}


try {
  process.exitCode = main();
} catch (error) {
  const message = error instanceof Error ? error.message : String(error);
  console.error(`[ERROR] ${message}`);
  process.exitCode = 1;
}
