# npm registry installation — 2026-09-23

Package: [`@dairen/forgeflow@0.1.0`](https://www.npmjs.com/package/@dairen/forgeflow).
Source: `486b3d88b32f227594f2a5cb099545083f7a524f` in the public repository.
Environment: macOS 26.6.2, Node.js 22.23.1, npm 10.9.8.

## Observed results

- Anonymous registry installation passed using empty user/global npm configuration,
  no npm token environment variables and separate fresh caches and project directories.
- The pinned `0.1.0` version initialized the Codex adapter; `next` initialized Copilot.
  Each reported 29 framework files, the requested adapter and no Python CLI installation.
  Configuration adapter values and the installed Implement workflow were checked.
- The registry tarball matched the locally reviewed archive byte for byte.
  SHA256: `d396c17523e1b3de7b61932483ca9db80afd35d77016d7e46f85e880bf039de3`.
- Both `latest` and `next` resolved to `0.1.0` when checked. The release remains a
  Technical Preview; use an explicit version for reproducibility.

## Reproduce

In two empty application directories, run respectively:

```bash
npx --yes @dairen/forgeflow@0.1.0 init --adapter codex
npx --yes @dairen/forgeflow@next init --adapter copilot
```

For an anonymous cold-cache check, use empty npm user/global configuration files,
remove token environment variables and set a new `--cache` directory for each run.
The recorded checks used `npm exec --yes --package <package> -- forgeflow init
--adapter <adapter>`, equivalent to the npx entry above.

These checks establish registry download and initialization only. They did not
invoke an agent, test IDE prompt discovery or establish current workflow acceptance.
The original GitHub v0.1.0 assets retain the earlier `@idairen/forgeflow` identity;
this registry archive is a separate build after the npm scope correction.
