#!/usr/bin/env bash
# Build the upload file: dist/<skill-name>.zip
# The ZIP's top level is the skill folder itself (<skill-name>/SKILL.md), which
# is what claude.ai expects. Test cases (evals/) are left out.
set -euo pipefail

root="$(cd "$(dirname "$0")/.." && pwd)"
shopt -s nullglob
skills=("$root"/*/SKILL.md)
if [ "${#skills[@]}" -ne 1 ]; then
  echo "ERROR: expected exactly one <folder>/SKILL.md in $root" >&2
  exit 1
fi

name="$(basename "$(dirname "${skills[0]}")")"
mkdir -p "$root/dist"
out="$root/dist/$name.zip"
rm -f "$out"
(cd "$root" && zip -qr "$out" "$name" -x "$name/evals/*" "*/.DS_Store" "*/__pycache__/*" "*.pyc")

# Every entry must start with "<name>/", or Claude won't recognize the upload as a skill.
if unzip -Z1 "$out" | grep -qv "^$name/"; then
  echo "ERROR: $out has entries outside $name/" >&2
  exit 1
fi
echo "built dist/$name.zip ($(unzip -Z1 "$out" | grep -vc '/$') files)"
