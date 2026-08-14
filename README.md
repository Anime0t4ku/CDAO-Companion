# MiSTer Companion cdrdao Builds

Reproducible, unmodified builds of [cdrdao](https://github.com/cdrdao/cdrdao) for MiSTer Companion.

This repository does **not** contain a modified cdrdao source tree. GitHub Actions checks out a pinned upstream cdrdao release and builds the command-line tools required by MiSTer Companion.

## Targets

| Target | GitHub runner | Build environment |
|---|---|---|
| Windows x64 | `windows-2025` | MSYS2 UCRT64 |
| Windows ARM64 | `windows-11-arm` | MSYS2 CLANGARM64 |
| Linux x64 | `ubuntu-22.04` | Native GCC |
| Linux ARM64 | `ubuntu-22.04-arm` | Native GCC |
| macOS Intel | `macos-15-intel` | Native Clang |
| macOS Apple Silicon | `macos-14` | Native Clang |

The Windows ARM64 target is a native ARM64 build, not an x64 binary intended for emulation.

## Included tools

Each archive contains only the pieces MiSTer Companion needs:

- `cdrdao`
- `toc2cue`
- `cue2toc`
- required non-system runtime libraries where applicable
- cdrdao's `COPYING`, `AUTHORS`, and `README.md`
- `VERSION`

The builds intentionally disable cdrdao's optional GUI and compressed-audio helpers. MiSTer Companion only needs CD reading/writing and TOC/CUE conversion.

## Build

Run **Build cdrdao** from the Actions tab, or push a tag such as:

```text
cdrdao-1.2.6-1
```

A tag creates a GitHub Release with platform archives, SHA-256 checksums, and `manifest.json`.

## Updating upstream

1. Change `UPSTREAM_VERSION`.
2. Change `UPSTREAM_TAG` to the matching cdrdao tag.
3. Run the workflow manually.
4. Test every produced binary in MiSTer Companion.
5. Create a release tag only after validation.

No upstream source patches should be added here unless they are strictly required. If a platform fix becomes necessary, keep it as a small patch under `patches/`, document why it exists, and submit it upstream where practical.

## Licensing

cdrdao is GPL-2.0 licensed upstream. This repository redistributes cdrdao binaries together with the applicable upstream license and source reference. The build/release scripts in this repository are also provided under GPL-2.0.

The corresponding source for each published binary is the exact upstream cdrdao tag recorded in the release manifest.
