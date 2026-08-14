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

## Licensing

cdrdao is GPL-2.0 licensed upstream. This repository redistributes cdrdao binaries together with the applicable upstream license and source reference. The build/release scripts in this repository are also provided under GPL-2.0.

The corresponding source for each published binary is the exact upstream cdrdao tag recorded in the release manifest.
