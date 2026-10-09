"""Workspace tools shared by every stage. Plain functions: type hints + docstrings become the tool schema."""
import html
import json
import pathlib
import re
import subprocess
import urllib.request

ROOT = pathlib.Path(".").resolve()
AUTO_APPROVE = False
MAX_CHARS = 20_000


def configure(root: str, auto_approve: bool) -> None:
    global ROOT, AUTO_APPROVE
    ROOT, AUTO_APPROVE = pathlib.Path(root).resolve(), auto_approve


def _safe(path: str) -> pathlib.Path:
    p = (ROOT / path).resolve()
    if not p.is_relative_to(ROOT):
        raise ValueError(f"path outside workspace: {path}")
    return p


def list_files(path: str = ".") -> str:
    """List files under a workspace directory (skips hidden folders).

    Args:
        path: Directory relative to the workspace root.
    """
    base = _safe(path)
    files = [str(f.relative_to(ROOT)) for f in base.rglob("*") if f.is_file()
             and not any(part.startswith(".") for part in f.relative_to(ROOT).parts)]
    return "\n".join(sorted(files)[:500]) or "(empty)"


def read_file(path: str) -> str:
    """Read a text file from the workspace.

    Args:
        path: File path relative to the workspace root.
    """
    return _safe(path).read_text(errors="replace")[:MAX_CHARS]


def write_file(path: str, content: str) -> str:
    """Create or overwrite a text file in the workspace.

    Args:
        path: File path relative to the workspace root.
        content: Full file content.
    """
    p = _safe(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content)
    return f"wrote {path} ({len(content)} chars)"


def run_shell(command: str) -> str:
    """Run a shell command in the workspace and return exit code and output (120 s timeout).

    Args:
        command: The shell command to run.
    """
    if not AUTO_APPROVE and input(f"\nRun `{command}`? [y/N] ").strip().lower() != "y":
        return "denied by user"
    try:
        r = subprocess.run(command, shell=True, cwd=ROOT, capture_output=True, text=True, timeout=120)
        return f"exit {r.returncode}\n{(r.stdout + r.stderr)[-MAX_CHARS:]}"
    except subprocess.TimeoutExpired:
        return "timed out after 120 s"


def package_license(name: str, ecosystem: str = "pypi") -> str:
    """Look up a package's latest version and declared licence from its official registry.

    Args:
        name: Package name.
        ecosystem: "pypi" or "npm".
    """
    url = (f"https://pypi.org/pypi/{name}/json" if ecosystem == "pypi"
           else f"https://registry.npmjs.org/{name}/latest")
    try:
        with urllib.request.urlopen(url, timeout=15) as r:
            data = json.load(r)
    except Exception as e:
        return f"lookup failed: {e}"
    if ecosystem == "pypi":
        info = data["info"]
        classifiers = [c.split(" :: ")[-1] for c in info.get("classifiers", []) if c.startswith("License")]
        licence = info.get("license_expression") or ", ".join(classifiers) or (info.get("license") or "")[:80]
        return f"{name} {info['version']} licence: {licence or 'UNKNOWN'} {info.get('project_url', '')}"
    return f"{name} {data.get('version')} licence: {data.get('license') or 'UNKNOWN'}"


def fetch_url(url: str) -> str:
    """Fetch a web page (docs, README, paper abstract) as plain text.

    Args:
        url: The http(s) URL to fetch.
    """
    req = urllib.request.Request(url, headers={"User-Agent": "trident/0.1"})
    try:
        with urllib.request.urlopen(req, timeout=20) as r:
            text = r.read(2_000_000).decode(errors="replace")
    except Exception as e:
        return f"fetch failed: {e}"
    text = re.sub(r"(?s)<(script|style).*?</\1>", " ", text)
    return html.unescape(re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", text)))[:MAX_CHARS]


READ_TOOLS = [list_files, read_file, package_license, fetch_url]
BUILD_TOOLS = READ_TOOLS + [write_file, run_shell]
CHECK_TOOLS = [list_files, read_file, run_shell, package_license]
