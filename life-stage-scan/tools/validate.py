#!/usr/bin/env python3
"""Validate the skill in this repository.

Checks SKILL.md against the Agent Skills format, makes sure every file it
points to exists, flags reference files nothing points to, and checks the
eval case folders. Exits 1 on errors; warnings don't fail the run.

Usage: python3 tools/validate.py [skill-folder]   (default: the folder named
       after this repository that contains SKILL.md)
Requires: PyYAML (pip install pyyaml)
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

import yaml

NAME_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
SEMVER_RE = re.compile(r"^\d+\.\d+\.\d+$")
SKILL_KEYS = {"name", "description", "license", "compatibility", "metadata", "allowed-tools"}
PROMPT_KEYS = {"tags", "max_turns", "timeout_seconds", "allowed_tools"}
REF_RE = re.compile(r"(?:references|scripts|assets)/[A-Za-z0-9_.\-/]+\.[A-Za-z0-9]+")
MAX_SKILL_LINES = 500

errors: list[str] = []
warnings: list[str] = []


def err(where, msg):
    errors.append(f"{where}: {msg}")


def warn(where, msg):
    warnings.append(f"{where}: {msg}")


def frontmatter(path: Path):
    text = path.read_text(encoding="utf-8")
    m = re.match(r"^---\n(.*?)\n---\n?(.*)$", text, re.DOTALL)
    if not m:
        err(path, "missing YAML frontmatter delimited by --- lines")
        return None, text
    try:
        data = yaml.safe_load(m.group(1))
    except yaml.YAMLError as e:
        err(path, f"frontmatter is not valid YAML: {e}")
        return None, m.group(2)
    if not isinstance(data, dict):
        err(path, "frontmatter must be a mapping")
        return None, m.group(2)
    return data, m.group(2)


def check_skill(skill_dir: Path) -> None:
    skill_md = skill_dir / "SKILL.md"
    extra = [p for p in skill_dir.rglob("SKILL.md")
             if p != skill_md and "evals" not in p.relative_to(skill_dir).parts]
    if extra:
        err(skill_dir, f"extra SKILL.md files would be rejected on upload: {extra}")

    fm, body = frontmatter(skill_md)
    if fm is None:
        return
    unknown = set(fm) - SKILL_KEYS
    if unknown:
        err(skill_md, f"unknown frontmatter keys {sorted(unknown)}; allowed: {sorted(SKILL_KEYS)}")

    name = fm.get("name")
    if not isinstance(name, str) or not NAME_RE.match(name) or len(name) > 64:
        err(skill_md, f"name {name!r} must be lowercase letters, digits and hyphens, 1-64 chars")
    elif name != skill_dir.name:
        err(skill_md, f"name {name!r} must match the folder name {skill_dir.name!r}")

    desc = fm.get("description")
    if not isinstance(desc, str) or not desc.strip():
        err(skill_md, "description is required")
    else:
        if len(desc) > 1024:
            err(skill_md, f"description is {len(desc)} chars; max 1024")
        if "<" in desc or ">" in desc:
            err(skill_md, "description cannot contain angle brackets")

    meta = fm.get("metadata") or {}
    if not isinstance(meta, dict) or not all(isinstance(v, str) for v in meta.values()):
        err(skill_md, "metadata must map strings to strings (quote version numbers)")
    elif "version" in meta and not SEMVER_RE.match(meta["version"]):
        err(skill_md, f"metadata.version {meta['version']!r} is not MAJOR.MINOR.PATCH")

    lines = skill_md.read_text(encoding="utf-8").count("\n")
    if lines > MAX_SKILL_LINES:
        warn(skill_md, f"{lines} lines; keep SKILL.md under {MAX_SKILL_LINES} and move detail to references/")

    ref_dir = skill_dir / "references"
    ref_files = sorted(ref_dir.glob("*.md")) if ref_dir.is_dir() else []
    texts = {p: p.read_text(encoding="utf-8") for p in [skill_md, *ref_files]}
    for path, text in texts.items():
        for ref in REF_RE.findall(text):
            if not (skill_dir / ref).exists():
                err(path, f"points to missing file {ref}")
    for ref_file in ref_files:
        mentioned = any(ref_file.name in text for p, text in texts.items() if p != ref_file)
        if not mentioned:
            warn(ref_file, "nothing in SKILL.md or other reference files points to it")


def check_evals(evals_dir: Path) -> int:
    count = 0
    for case in sorted(p for p in evals_dir.iterdir() if p.is_dir() and p.name != "results"):
        count += 1
        if not NAME_RE.match(case.name):
            err(case, "case folder name must be lowercase-with-hyphens")
        prompt = case / "prompt.md"
        if not prompt.is_file():
            err(case, "missing prompt.md")
        else:
            fm, body = frontmatter(prompt)
            if fm is not None and set(fm) - PROMPT_KEYS:
                err(prompt, f"unknown settings keys {sorted(set(fm) - PROMPT_KEYS)}")
            if not body.strip():
                err(prompt, "prompt is empty")
        case_yaml = case / "case.yaml"
        if not case_yaml.is_file():
            err(case, "missing case.yaml")
        else:
            data = yaml.safe_load(case_yaml.read_text(encoding="utf-8")) or {}
            if not isinstance(data.get("schema_version"), str):
                err(case_yaml, "schema_version must be a quoted string")
            if data.get("name") != case.name:
                err(case_yaml, f"name must equal the folder name {case.name!r}")
        graders = sorted((case / "graders").glob("*.md")) if (case / "graders").is_dir() else []
        if not graders:
            err(case, "no graders/*.md")
        for g in graders:
            fm, body = frontmatter(g)
            if fm is not None and "type" not in fm:
                err(g, "grader needs a type (e.g. llm)")
            if not body.strip():
                err(g, "grader statement is empty")
    return count


def main() -> int:
    root = Path(__file__).resolve().parent.parent
    if len(sys.argv) > 1:
        skill_dir = Path(sys.argv[1]).resolve()
    else:
        found = sorted(p.parent for p in root.glob("*/SKILL.md"))
        if len(found) != 1:
            print(f"ERROR    expected exactly one <folder>/SKILL.md in {root}, found {len(found)}")
            return 1
        skill_dir = found[0]
    if not (skill_dir / "SKILL.md").is_file():
        print(f"ERROR    {skill_dir}: no SKILL.md")
        return 1

    check_skill(skill_dir)
    cases = check_evals(skill_dir / "evals") if (skill_dir / "evals").is_dir() else 0
    if not cases:
        warn(skill_dir, "no eval cases in evals/")

    for w in warnings:
        print(f"warning  {w}")
    for e in errors:
        print(f"ERROR    {e}")
    print(f"\n{'FAILED' if errors else 'OK'}: {skill_dir.name}, {cases} eval case(s); "
          f"{len(errors)} error(s), {len(warnings)} warning(s)")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
