#!/usr/bin/env python3
"""Add (or replace) a script on the website from a "New script" GitHub issue.

Reads the issue body from the ISSUE_BODY environment variable, downloads the
attached PDF into scripts/, updates scripts.json (stamping today's date as
the "updated" field) and regenerates sitemap.xml.
Writes the new page id to $GITHUB_OUTPUT. Exits non-zero with a readable
message on any problem.
"""
import json
import os
import re
import sys
import urllib.parse
import urllib.request
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCRIPTS_JSON = ROOT / "scripts.json"
SITEMAP = ROOT / "sitemap.xml"
SITE = "https://habrahamyan.github.io"
NO_RESPONSE = "_No response_"
# Hand-made pages that are not scripts; kept in the sitemap on every rebuild.
EXTRA_PAGES = ["granada/"]


class UserError(Exception):
    pass


def parse_form(body: str) -> dict:
    """Split an issue-form body into {heading: value}."""
    fields, current, lines = {}, None, []
    for line in body.replace("\r\n", "\n").split("\n"):
        m = re.match(r"^### (.+?)\s*$", line)
        if m:
            if current is not None:
                fields[current] = "\n".join(lines).strip()
            current, lines = m.group(1), []
        elif current is not None:
            lines.append(line)
    if current is not None:
        fields[current] = "\n".join(lines).strip()
    return {k: ("" if v == NO_RESPONSE else v) for k, v in fields.items()}


def split_outside_math(text: str, sep: str) -> list:
    """Split on `sep`, ignoring separators inside $...$."""
    parts, buf, in_math = [], "", False
    for ch in text:
        if ch == "$":
            in_math = not in_math
        if ch == sep and not in_math:
            parts.append(buf)
            buf = ""
        else:
            buf += ch
    parts.append(buf)
    return parts


def parse_keywords(text: str) -> list:
    lines = [l.strip() for l in text.split("\n") if l.strip()]
    if len(lines) == 1:
        lines = split_outside_math(lines[0], ",")
    kws = []
    for l in lines:
        l = re.sub(r"^[-*]\s+", "", l.strip())  # allow markdown bullets
        if l and l not in kws:
            kws.append(l)
    return kws


def find_pdf_url(text: str):
    """Return (url, original_name) of the first attachment in the field."""
    m = re.search(r"\[([^\]]*)\]\((https://github\.com/[^)\s]+)\)", text)
    if m:
        return m.group(2), m.group(1)
    m = re.search(r"https://github\.com/\S+", text)
    if m:
        url = m.group(0).rstrip(")>")
        return url, urllib.parse.unquote(url.rsplit("/", 1)[-1])
    raise UserError(
        "I couldn't find an uploaded PDF in the **PDF file** field. "
        "Drag the PDF into that box and wait for the upload to finish."
    )


def sanitize_id(name: str) -> str:
    name = re.sub(r"\.pdf$", "", name.strip(), flags=re.I)
    name = re.sub(r"[^A-Za-z0-9_-]+", "_", name).strip("_")
    return name


def download_pdf(url: str, dest: Path):
    headers = {"User-Agent": "add-script-action"}
    token = os.environ.get("GITHUB_TOKEN")
    req = urllib.request.Request(url, headers=headers)
    try:
        data = urllib.request.urlopen(req, timeout=60).read()
    except Exception:
        if not token:
            raise
        # Private repos need auth for attachments.
        req = urllib.request.Request(url, headers={**headers, "Authorization": f"token {token}"})
        data = urllib.request.urlopen(req, timeout=60).read()
    if not data.startswith(b"%PDF"):
        raise UserError("The attached file doesn't look like a PDF. Please attach a `.pdf` file.")
    dest.write_bytes(data)


def write_sitemap(items: list):
    entries = ["""  <!-- Homepage -->
  <url>
    <loc>%s/</loc>
    <priority>1.0</priority>
  </url>
""" % SITE, "  <!-- Software -->"] + [f"""  <url>
    <loc>{SITE}/{page}</loc>
    <priority>0.9</priority>
  </url>
""" for page in EXTRA_PAGES] + ["  <!-- Paper viewer pages -->"]
    for item in items:
        pid = Path(item["file"]).stem
        loc = f"{SITE}/paper/?id={urllib.parse.quote(pid)}"
        entries.append(f"""  <url>
    <loc>{loc}</loc>
    <priority>0.8</priority>
  </url>
""")
    SITEMAP.write_text(
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n\n'
        + "\n".join(entries)
        + "\n</urlset>\n"
    )


def main():
    fields = parse_form(os.environ.get("ISSUE_BODY", ""))
    title = fields.get("Title", "").strip()
    description = " ".join(fields.get("Description", "").split())
    keywords = parse_keywords(fields.get("Keywords", ""))
    replace = "[x]" in fields.get("Replacing an existing script?", "").lower()

    if not title:
        raise UserError("The **Title** field is empty.")
    if not description:
        raise UserError("The **Description** field is empty.")

    url, original_name = find_pdf_url(fields.get("PDF file", ""))
    pid = sanitize_id(fields.get("File name (optional)", "")) or sanitize_id(original_name) or sanitize_id(title)
    if not pid:
        raise UserError("Couldn't derive a file name. Please fill in **File name (optional)**.")

    rel = f"scripts/{pid}.pdf"
    items = json.loads(SCRIPTS_JSON.read_text())
    existing = next((i for i, it in enumerate(items) if Path(it["file"]).stem == pid), None)
    if existing is not None and not replace:
        raise UserError(
            f"A script with the file name `{pid}` already exists. Either choose a different "
            "**File name**, or tick the **Replacing an existing script?** box to overwrite it."
        )

    download_pdf(url, ROOT / rel)

    entry = {"file": rel, "title": title, "updated": date.today().isoformat(), "description": description, "keywords": keywords}
    if existing is not None:
        items[existing] = entry
    else:
        items.append(entry)

    SCRIPTS_JSON.write_text(json.dumps(items, indent=2, ensure_ascii=False) + "\n")
    write_sitemap(items)

    out = os.environ.get("GITHUB_OUTPUT")
    if out:
        with open(out, "a") as f:
            f.write(f"id={pid}\n")
            f.write(f"action={'Updated' if existing is not None else 'Added'}\n")
    print(f"{'Updated' if existing is not None else 'Added'} {rel}")


if __name__ == "__main__":
    try:
        main()
    except UserError as e:
        msg = str(e)
    except Exception as e:  # unexpected problems
        msg = f"Unexpected error: `{type(e).__name__}: {e}`"
    else:
        sys.exit(0)
    print(msg, file=sys.stderr)
    err = os.environ.get("ERROR_FILE")
    if err:
        Path(err).write_text(msg)
    sys.exit(1)
