#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path

root = Path(__file__).resolve().parents[1]
dist = root / "dist"
version = (root / "UPSTREAM_VERSION").read_text(encoding="utf-8").strip()
tag = (root / "UPSTREAM_TAG").read_text(encoding="utf-8").strip()

platforms = {
    "linux-x64": {"os": "linux", "arch": "x64"},
    "linux-arm64": {"os": "linux", "arch": "arm64"},
    "macos-x64": {"os": "macos", "arch": "x64"},
    "macos-arm64": {"os": "macos", "arch": "arm64"},
}

assets = []
for path in sorted(dist.iterdir()):
    if not path.is_file() or path.name in {"manifest.json", "SHA256SUMS"}:
        continue
    target = next((key for key in platforms if f"-{key}." in path.name), None)
    if target is None:
        continue
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    assets.append({
        "target": target,
        **platforms[target],
        "asset": path.name,
        "sha256": digest,
    })

manifest = {
    "schema": 1,
    "tool": "cdrdao",
    "version": version,
    "upstream_repository": "https://github.com/cdrdao/cdrdao",
    "upstream_tag": tag,
    "assets": assets,
}

(dist / "manifest.json").write_text(
    json.dumps(manifest, indent=2) + "\n",
    encoding="utf-8",
)

with (dist / "SHA256SUMS").open("w", encoding="utf-8", newline="\n") as out:
    for item in assets:
        out.write(f"{item['sha256']}  {item['asset']}\n")

print(f"Wrote manifest for {len(assets)} assets")
