#!/usr/bin/env python3
"""Validate `plugins.yaml` against the registry guidelines documented in README.md.

This script enforces the contribution guidelines described in the project README:

* `plugins.yaml` is valid YAML and has the expected top-level structure.
* Every plugin entry has the required fields with the correct types.
* `name` is unique, uses snake_case (no spaces).
* `category` is one of the standard categories listed in the README.
* `description` is short (<= 100 characters as recommended by the guidelines).
* `repository` is a valid public Git URL (http(s) or git@).
* `version` is either `latest` or looks like a (semver-ish) tag.
* Entries are sorted alphabetically by `name`.
* The `Available Plugins` table in `README.md` stays in sync with `plugins.yaml`.
* Optionally (when `--check-remote` is given and `GITHUB_TOKEN` is available),
  each referenced GitHub repository is reachable, public, has a README,
  has a LICENSE, and — when `version` is not `latest` — exposes a tag/release
  matching the declared version.

Exits with status 0 when all checks pass, 1 otherwise. All discovered problems
are printed to stdout to make the GitHub Actions log easy to read.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

import yaml


REQUIRED_FIELDS: dict[str, type] = {
    "name": str,
    "description": str,
    "repository": str,
    "version": str,
    "author": str,
    "category": str,
}
OPTIONAL_FIELDS: dict[str, type] = {
    "tags": list,
}

ALLOWED_CATEGORIES = {
    "PerceptionStrategy",
    "LocalizationStrategy",
    "MappingStrategy",
    "PlanningStrategy",
    "ControlStrategy",
    "Executer",
    "WorldBridge",
}

NAME_RE = re.compile(r"^[A-Za-z0-9]+(?:_[A-Za-z0-9]+)*$")
# The README asks for snake_case names with no spaces. Existing entries
# (e.g. `ORBit_perception`) mix cases, so we accept letters and digits
# separated by underscores rather than enforcing strict lowercase.
VERSION_RE = re.compile(r"^(latest|v?\d+\.\d+(?:\.\d+)?(?:[-+][0-9A-Za-z.-]+)?)$")
URL_RE = re.compile(r"^(https?://|git@)[\w.@:/\-~]+?(?:\.git)?/?$")
GITHUB_URL_RE = re.compile(
    r"^https?://github\.com/(?P<owner>[\w.\-]+)/(?P<repo>[\w.\-]+?)(?:\.git)?/?$"
)
DESCRIPTION_MAX_LEN = 100

REPO_ROOT = Path(__file__).resolve().parents[2]
PLUGINS_YAML = REPO_ROOT / "plugins.yaml"
README_MD = REPO_ROOT / "README.md"


class Problems:
    def __init__(self) -> None:
        self.errors: list[str] = []
        self.warnings: list[str] = []

    def error(self, msg: str) -> None:
        self.errors.append(msg)

    def warn(self, msg: str) -> None:
        self.warnings.append(msg)

    def report(self) -> int:
        for w in self.warnings:
            print(f"::warning::{w}")
        for e in self.errors:
            print(f"::error::{e}")
        if self.errors:
            print(f"\nValidation failed with {len(self.errors)} error(s) "
                  f"and {len(self.warnings)} warning(s).")
            return 1
        print(f"Validation passed ({len(self.warnings)} warning(s)).")
        return 0


def load_plugins(problems: Problems) -> list[dict[str, Any]]:
    if not PLUGINS_YAML.is_file():
        problems.error(f"{PLUGINS_YAML} does not exist")
        return []
    try:
        data = yaml.safe_load(PLUGINS_YAML.read_text())
    except yaml.YAMLError as exc:
        problems.error(f"plugins.yaml is not valid YAML: {exc}")
        return []
    if not isinstance(data, dict) or "plugins" not in data:
        problems.error("plugins.yaml must be a mapping with a top-level `plugins` key")
        return []
    plugins = data["plugins"]
    if not isinstance(plugins, list):
        problems.error("`plugins` must be a list")
        return []
    return plugins


def validate_entry(idx: int, entry: Any, problems: Problems) -> None:
    label = f"plugins[{idx}]"
    if not isinstance(entry, dict):
        problems.error(f"{label} must be a mapping, got {type(entry).__name__}")
        return

    name = entry.get("name", f"<index {idx}>")
    label = f"plugin `{name}`"

    # Unknown fields
    known = set(REQUIRED_FIELDS) | set(OPTIONAL_FIELDS)
    for key in entry:
        if key not in known:
            problems.warn(f"{label}: unknown field `{key}`")

    # Required fields presence + type
    for field, expected in REQUIRED_FIELDS.items():
        if field not in entry:
            problems.error(f"{label}: missing required field `{field}`")
            continue
        value = entry[field]
        if not isinstance(value, expected) or (isinstance(value, str) and not value.strip()):
            problems.error(f"{label}: field `{field}` must be a non-empty {expected.__name__}")

    # Optional fields type
    for field, expected in OPTIONAL_FIELDS.items():
        if field in entry and not isinstance(entry[field], expected):
            problems.error(f"{label}: field `{field}` must be a {expected.__name__}")

    if "tags" in entry and isinstance(entry["tags"], list):
        for i, tag in enumerate(entry["tags"]):
            if not isinstance(tag, str) or not tag.strip():
                problems.error(f"{label}: tags[{i}] must be a non-empty string")

    # Name format
    if isinstance(entry.get("name"), str):
        if " " in entry["name"]:
            problems.error(f"{label}: `name` must not contain spaces")
        elif not NAME_RE.match(entry["name"]):
            problems.error(
                f"{label}: `name` must be snake_case "
                "(letters/digits separated by underscores)"
            )

    # Description length
    desc = entry.get("description")
    if isinstance(desc, str) and len(desc) > DESCRIPTION_MAX_LEN:
        problems.warn(
            f"{label}: `description` is {len(desc)} characters, "
            f"keep it under {DESCRIPTION_MAX_LEN}"
        )

    # Category
    cat = entry.get("category")
    if isinstance(cat, str) and cat not in ALLOWED_CATEGORIES:
        problems.error(
            f"{label}: category `{cat}` is not one of "
            f"{sorted(ALLOWED_CATEGORIES)}"
        )

    # Repository URL
    repo = entry.get("repository")
    if isinstance(repo, str) and not URL_RE.match(repo):
        problems.error(f"{label}: `repository` is not a valid URL: {repo!r}")

    # Version format
    version = entry.get("version")
    if isinstance(version, str) and not VERSION_RE.match(version):
        problems.warn(
            f"{label}: `version` {version!r} is not `latest` and does not look "
            "like a semver tag (e.g. `1.2.0` or `v1.2.0`)"
        )


def validate_collection(plugins: list[dict[str, Any]], problems: Problems) -> None:
    names = [p.get("name") for p in plugins if isinstance(p, dict) and isinstance(p.get("name"), str)]

    # Uniqueness
    seen: dict[str, int] = {}
    for n in names:
        seen[n] = seen.get(n, 0) + 1
    for n, count in seen.items():
        if count > 1:
            problems.error(f"Duplicate plugin name `{n}` appears {count} times")

    # Alphabetical sort (case-insensitive, as the README asks for sorted entries)
    sorted_names = sorted(names, key=str.lower)
    if names != sorted_names:
        out_of_order = [
            f"{a!r} should come after {b!r}"
            for a, b in zip(names, sorted_names)
            if a != b
        ]
        problems.error(
            "plugins.yaml entries must be sorted alphabetically by `name`. "
            f"First mismatch: {out_of_order[0] if out_of_order else 'unknown'}"
        )


def parse_readme_table(problems: Problems) -> list[dict[str, str]] | None:
    if not README_MD.is_file():
        problems.error("README.md not found")
        return None
    text = README_MD.read_text().splitlines()
    try:
        header_idx = next(
            i for i, line in enumerate(text)
            if line.strip().lower().startswith("## available plugins")
        )
    except StopIteration:
        problems.error("README.md is missing the `## Available Plugins` section")
        return None

    rows: list[dict[str, str]] = []
    # Skip to the table header row
    i = header_idx + 1
    while i < len(text) and not text[i].lstrip().startswith("|"):
        i += 1
    if i >= len(text):
        problems.error("`Available Plugins` section has no markdown table")
        return None
    header = [c.strip() for c in text[i].strip().strip("|").split("|")]
    i += 2  # skip the |---|---| separator
    while i < len(text) and text[i].lstrip().startswith("|"):
        cells = [c.strip() for c in text[i].strip().strip("|").split("|")]
        if len(cells) == len(header):
            rows.append(dict(zip(header, cells)))
        i += 1
    return rows


def validate_readme_in_sync(
    plugins: list[dict[str, Any]], problems: Problems
) -> None:
    rows = parse_readme_table(problems)
    if rows is None:
        return

    plugins_by_name = {
        p["name"]: p for p in plugins if isinstance(p, dict) and isinstance(p.get("name"), str)
    }
    table_names = {row.get("Name", "").strip() for row in rows}

    missing_in_table = set(plugins_by_name) - table_names
    extra_in_table = table_names - set(plugins_by_name)
    for n in sorted(missing_in_table):
        problems.error(
            f"README `Available Plugins` table is missing an entry for `{n}` "
            "(present in plugins.yaml)"
        )
    for n in sorted(extra_in_table):
        problems.error(
            f"README `Available Plugins` table lists `{n}` "
            "but it is not in plugins.yaml"
        )

    for row in rows:
        name = row.get("Name", "").strip()
        plugin = plugins_by_name.get(name)
        if not plugin:
            continue
        for col, field in (("Category", "category"),
                           ("Description", "description"),
                           ("Repository", "repository")):
            expected = str(plugin.get(field, "")).strip()
            actual = row.get(col, "").strip()
            if expected and actual != expected:
                problems.error(
                    f"README table for `{name}`: column `{col}` is "
                    f"{actual!r} but plugins.yaml has {expected!r}"
                )


# ---------------------------------------------------------------------------
# Optional remote checks (GitHub API)
# ---------------------------------------------------------------------------

def _gh_get(path: str, token: str | None) -> tuple[int, Any]:
    url = f"https://api.github.com{path}"
    req = urllib.request.Request(url, headers={
        "Accept": "application/vnd.github+json",
        "User-Agent": "avlite-plugins-validator",
    })
    if token:
        req.add_header("Authorization", f"Bearer {token}")
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            return resp.status, json.loads(resp.read() or b"null")
    except urllib.error.HTTPError as exc:
        body: Any = None
        try:
            body = json.loads(exc.read() or b"null")
        except Exception:
            body = None
        return exc.code, body
    except (urllib.error.URLError, TimeoutError) as exc:
        return 0, str(exc)


def validate_remote(plugins: list[dict[str, Any]], problems: Problems) -> None:
    token = os.environ.get("GITHUB_TOKEN")
    if not token:
        problems.warn(
            "GITHUB_TOKEN is not set; remote repository checks will be unauthenticated "
            "and may be rate-limited."
        )

    for entry in plugins:
        if not isinstance(entry, dict):
            continue
        name = entry.get("name", "<unknown>")
        repo_url = entry.get("repository", "")
        version = entry.get("version", "")
        if not isinstance(repo_url, str):
            continue
        m = GITHUB_URL_RE.match(repo_url)
        if not m:
            problems.warn(
                f"plugin `{name}`: repository {repo_url!r} is not a github.com URL; "
                "skipping remote checks"
            )
            continue
        owner, repo = m.group("owner"), m.group("repo")

        status, payload = _gh_get(f"/repos/{owner}/{repo}", token)
        if status == 0:
            problems.warn(f"plugin `{name}`: could not reach GitHub ({payload})")
            continue
        if status == 404:
            problems.error(
                f"plugin `{name}`: repository {repo_url} is not accessible (404). "
                "It must be public."
            )
            continue
        if status >= 400 or not isinstance(payload, dict):
            problems.warn(
                f"plugin `{name}`: GitHub API returned {status} for {repo_url}"
            )
            continue
        if payload.get("private"):
            problems.error(f"plugin `{name}`: repository {repo_url} is private")
        if not payload.get("license"):
            problems.error(
                f"plugin `{name}`: repository {repo_url} has no detected LICENSE"
            )

        # README presence
        status, _ = _gh_get(f"/repos/{owner}/{repo}/readme", token)
        if status == 404:
            problems.error(
                f"plugin `{name}`: repository {repo_url} has no README"
            )
        elif status >= 400 and status != 0:
            problems.warn(
                f"plugin `{name}`: could not verify README (HTTP {status})"
            )

        # Tag matches version
        if isinstance(version, str) and version and version != "latest":
            status, _ = _gh_get(f"/repos/{owner}/{repo}/git/ref/tags/{version}", token)
            if status == 404:
                # try with a leading 'v'
                alt = version if version.startswith("v") else f"v{version}"
                status2, _ = _gh_get(
                    f"/repos/{owner}/{repo}/git/ref/tags/{alt}", token
                )
                if status2 == 404:
                    problems.error(
                        f"plugin `{name}`: no tag matching version `{version}` "
                        f"found in {repo_url}"
                    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check-remote",
        action="store_true",
        help="Also verify that referenced GitHub repositories exist, are public, "
             "have a LICENSE/README, and expose the declared version tag.",
    )
    args = parser.parse_args()

    problems = Problems()
    plugins = load_plugins(problems)
    if plugins:
        for i, entry in enumerate(plugins):
            validate_entry(i, entry, problems)
        validate_collection(plugins, problems)
        validate_readme_in_sync(plugins, problems)
        if args.check_remote:
            validate_remote(plugins, problems)

    return problems.report()


if __name__ == "__main__":
    sys.exit(main())
