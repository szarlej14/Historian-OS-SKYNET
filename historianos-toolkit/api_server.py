#!/usr/bin/env python3
"""HistorianOS share, embed and read-only research API."""
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse
from email.parser import BytesParser
from email.policy import default as email_policy
import html
import io
import json
import os
import re
import tempfile
import zipfile

ROOT = Path(os.environ.get("HISTORIANOS_VAULT", "/vault")).resolve()
SHOWCASE = Path(os.environ.get("HISTORIANOS_SHOWCASE", "/showcase/zjazd-gnieznienski")).resolve()
DEFAULT_VAULT_ID = os.environ.get("HISTORIANOS_DEFAULT_VAULT", "gniezno")
DEFAULT_VAULT_NAME = os.environ.get("HISTORIANOS_DEFAULT_NAME", "Zjazd Gnieźnieński 1000")
MAX_UPLOAD = int(os.environ.get("HISTORIANOS_MAX_UPLOAD_MB", "100")) * 1024 * 1024
MAX_FILE = 5 * 1024 * 1024


def safe_name(value):
    value = re.sub(r"[^A-Za-z0-9._-]+", "-", value).strip("-._")
    return value[:80] or "vault"


def is_hidden(path, base):
    return any(part.startswith(".") for part in path.relative_to(base).parts)


def vault_path(vault_id):
    """Resolve the default showcase and uploaded vaults safely."""
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]{0,79}", vault_id):
        return None
    direct = ROOT / vault_id
    if direct.is_dir():
        return direct
    if vault_id == DEFAULT_VAULT_ID:
        if SHOWCASE.is_dir():
            return SHOWCASE
        showcase = ROOT / "zjazd-gnieznienski"
        if showcase.is_dir():
            return showcase
        if any(ROOT.glob("*.md")):
            return ROOT
    return None


def vault_name(vault_id, base):
    if vault_id == DEFAULT_VAULT_ID:
        return DEFAULT_VAULT_NAME
    return vault_id.replace("-", " ").replace("_", " ").title()


def files(base):
    return [p for p in base.rglob("*") if p.is_file() and not is_hidden(p, base)]


def md_files(base):
    return [p for p in files(base) if p.suffix.lower() == ".md" and p.stat().st_size <= MAX_FILE]


def parse(p, base):
    text = p.read_text(encoding="utf-8", errors="ignore")
    out = {"file": str(p.relative_to(base))}
    for line in text.splitlines():
        m = re.match(r'^([A-Za-z_][\w-]*):\s*["\']?(.*?)["\']?$', line)
        if m:
            out[m.group(1)] = m.group(2)
    return out


def records(base, kind=None):
    result = []
    for p in md_files(base):
        row = parse(p, base)
        if not kind or row.get("type") == kind:
            result.append(row)
    return result


def stats(base):
    facts = records(base, "fakt")
    return {
        "files": len(md_files(base)),
        "osoba": len(records(base, "osoba")),
        "miejsce": len(records(base, "miejsce")),
        "wydarzenie": len(records(base, "wydarzenie")),
        "zrodlo": len(records(base, "zrodlo")),
        "fakt": sum(int(r.get("fact_count", "1")) for r in facts),
        "fact_files": len(facts),
        "relacja": len(records(base, "relacja")),
        "seria": len(records(base, "seria")),
        "gaps_review": sum(1 for r in facts if r.get("status") == "REVIEW_REQUIRED"),
    }


def timeline(base):
    result = []
    for row in records(base, "wydarzenie"):
        start = row.get("start") or row.get("date") or row.get("data")
        if start:
            row["start"] = start
            result.append(row)
    return sorted(result, key=lambda r: r.get("start", ""))


def map_items(base):
    result = []
    for row in records(base, "miejsce"):
        try:
            if "lat" in row and "lon" in row:
                row["lat"] = float(row["lat"])
                row["lon"] = float(row["lon"])
                result.append(row)
        except (TypeError, ValueError):
            pass
    return result


def gaps(base):
    return [
        {
            "type": "REVIEW_REQUIRED",
            "file": r["file"],
            "name": r.get("name", ""),
            "decision_log": r.get("decision_log", ""),
        }
        for r in records(base, "fakt")
        if r.get("status") == "REVIEW_REQUIRED"
    ]


def share_payload(vault_id, base):
    return {
        "vault_id": vault_id,
        "name": vault_name(vault_id, base),
        "file_count": len(md_files(base)),
        "counts": stats(base),
        "share_url": f"/vault/{vault_id}",
        "dashboard_url": f"/dashboard?vault={vault_id}",
        "export_url": f"/api/vaults/{vault_id}/export",
        "api_stats_url": f"/api/stats?vault={vault_id}",
        "qr_data": f"/vault/{vault_id}",
    }


def html_page(title, body, embed=False):
    frame = "" if embed else "<header><a href='/'>Historian OS SKYNET</a></header>"
    css = """
    :root{color-scheme:light dark} body{font-family:system-ui,-apple-system,sans-serif;max-width:1100px;margin:0 auto;padding:24px;line-height:1.5}
    header{font-weight:800;font-size:22px;margin-bottom:24px} a{color:#0891b2} .grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:14px}
    .card{border:1px solid #d4d4d8;border-radius:12px;padding:18px;background:rgba(127,127,127,.06)} .num{font-size:28px;font-weight:800}
    .actions{display:flex;flex-wrap:wrap;gap:10px;margin:18px 0}.btn{display:inline-block;padding:9px 13px;border-radius:8px;text-decoration:none;border:1px solid #a1a1aa}
    .amber{background:#f59e0b;color:#111827;border-color:#f59e0b}.cyan{background:#06b6d4;color:#062a30;border-color:#06b6d4}
    .muted{color:#71717a}.embed{padding:14px}.timeline-item{padding:10px 0;border-bottom:1px solid #e4e4e7}.code{background:#18181b;color:#f4f4f5;padding:12px;border-radius:8px;overflow:auto}
    """
    return f"<!doctype html><html><head><meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-scale=1'><title>{html.escape(title)}</title><style>{css}</style></head><body>{frame}{body}</body></html>"


def render_stats(st):
    labels = [("files", "Pliki"), ("fakt", "Fakty"), ("wydarzenie", "Wydarzenia"), ("miejsce", "Miejsca"), ("osoba", "Osoby")]
    return "<div class='grid'>" + "".join(
        f"<div class='card'><div class='muted'>{label}</div><div class='num'>{st.get(key,0)}</div></div>"
        for key, label in labels
    ) + "</div>"


def render_timeline(items):
    if not items:
        return "<div class='card muted'>Brak zdarzeń w tym vaultcie.</div>"
    return "".join(
        f"<div class='timeline-item'><strong>{html.escape(str(x.get('start','')))}</strong> — {html.escape(str(x.get('name') or x.get('title') or x.get('file','')))}</div>"
        for x in items[:100]
    )


def render_map(items):
    if not items:
        return "<div class='card muted'>Brak miejsc z współrzędnymi.</div>"
    return "<div class='grid'>" + "".join(
        f"<div class='card'><strong>{html.escape(str(x.get('name') or x.get('file','')))}</strong><br><span class='muted'>{x['lat']:.5f}, {x['lon']:.5f}</span></div>"
        for x in items[:100]
    ) + "</div>"


def dashboard_html(vault_id, base):
    st = stats(base)
    body = f"""
    <h1>Command Center — {html.escape(vault_name(vault_id, base))}</h1>
    <p class='muted'>Vault: {html.escape(vault_id)} · tryb evidence-first</p>
    {render_stats(st)}
    <h2>Timeline</h2><div class='card'>{render_timeline(timeline(base))}</div>
    <h2>Mapa</h2>{render_map(map_items(base))}
    <div class='actions'><a class='btn cyan' href='/vault/{html.escape(vault_id)}'>Share</a>
    <a class='btn' href='/api/vaults/{html.escape(vault_id)}/export'>Download ZIP</a></div>
    """
    return html_page(f"Dashboard — {vault_name(vault_id, base)}", body)


def share_html(vault_id, base):
    p = share_payload(vault_id, base)
    full = f"https://{os.environ.get('PUBLIC_HOST','historianos.fly.dev')}{p['share_url']}"
    iframe_full = f'<iframe src="{full}?embed=true" width="100%" height="600" frameborder="0"></iframe>'
    iframe_tl = f'<iframe src="{full}?embed=timeline" width="100%" height="300" frameborder="0"></iframe>'
    iframe_map = f'<iframe src="{full}?embed=map" width="100%" height="300" frameborder="0"></iframe>'
    body = f"""
    <h1>SHARE — {html.escape(vault_id)}</h1>
    <div class='card'><span class='muted'>SHOWCASE</span><h2>{html.escape(p['name'])}</h2>
    <div class='code' id='share-url'>{html.escape(full)}</div>
    <div class='actions'><button class='btn cyan' type='button' onclick='copyShare()'>Copy Link</button>
    <a class='btn amber' href='{p['dashboard_url']}'>Open Dashboard</a>
    <a class='btn' href='{p['export_url']}'>Download ZIP</a><a class='btn' href='{p['api_stats_url']}'>API Stats</a></div>
    <p id='copy-state' class='muted'></p>
    <div class='card'><img alt='QR code for this vault' width='180' height='180'
      src='https://quickchart.io/qr?size=180&text={html.escape(full, quote=True)}'></div></div>
    {render_stats(p['counts'])}
    <h2>Embed</h2>
    <p class='muted'>Wklej iframe na stronę WWW, bloga lub WordPressa.</p>
    <div class='card'><strong>Full</strong><pre class='code'>{html.escape(iframe_full)}</pre></div>
    <div class='card'><strong>Timeline</strong><pre class='code'>{html.escape(iframe_tl)}</pre></div>
    <div class='card'><strong>Mapa</strong><pre class='code'>{html.escape(iframe_map)}</pre></div>
    <h2>Live preview</h2><div class='card'>{render_timeline(timeline(base))}</div>
    <div class='card'>{render_map(map_items(base))}</div>
    <script>
    async function copyShare() {{
      const url = document.getElementById('share-url').textContent;
      try {{ await navigator.clipboard.writeText(url); }}
      catch (_) {{
        const area = document.createElement('textarea'); area.value = url;
        document.body.appendChild(area); area.select(); document.execCommand('copy'); area.remove();
      }}
      document.getElementById('copy-state').textContent = 'Copied!';
    }}
    </script>
    """
    return html_page(f"Share — {p['name']}", body)


def embed_html(vault_id, base, mode):
    st = stats(base)
    if mode in ("stats",):
        body = render_stats(st)
    elif mode == "timeline":
        body = "<div class='embed'><h2>Timeline</h2>" + render_timeline(timeline(base)) + "</div>"
    elif mode == "map":
        body = "<div class='embed'><h2>Mapa</h2>" + render_map(map_items(base)) + "</div>"
    else:
        body = "<div class='embed'>" + render_stats(st) + "<h2>Timeline</h2><div class='card'>" + render_timeline(timeline(base)) + "</div><h2>Mapa</h2>" + render_map(map_items(base)) + "</div>"
    return html_page(vault_name(vault_id, base), body, embed=True)


class Handler(BaseHTTPRequestHandler):
    def send_bytes(self, data, code=200, content_type="text/html; charset=utf-8", headers=None):
        self.send_response(code)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Cache-Control", "no-store")
        if headers:
            for key, value in headers.items():
                self.send_header(key, value)
        self.end_headers()
        self.wfile.write(data)

    def send_json(self, obj, code=200):
        self.send_bytes(
            json.dumps(obj, ensure_ascii=False).encode(),
            code,
            "application/json; charset=utf-8",
            {"Access-Control-Allow-Origin": "*"},
        )

    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET,POST,OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path
        qs = parse_qs(parsed.query)
        if path == "/api/health":
            return self.send_json({"status": "ok", "mode": "share-readonly", "vault": str(ROOT)})
        if path == "/":
            return self.send_bytes(self.landing_html().encode())

        m = re.fullmatch(r"/vault/([^/]+)", path)
        if m:
            vid = m.group(1)
            base = vault_path(vid)
            if not base:
                return self.send_json({"error": "vault_not_found"}, 404)
            embed = (qs.get("embed", [None])[0] or "").lower()
            if embed:
                return self.send_bytes(
                    embed_html(vid, base, embed if embed in {"timeline","map","stats","true","full"} else "full").encode(),
                    headers={"Content-Security-Policy": "frame-ancestors *"},
                )
            return self.send_bytes(share_html(vid, base).encode())

        m = re.fullmatch(r"/dashboard", path)
        if m:
            vid = qs.get("vault", [DEFAULT_VAULT_ID])[0]
            base = vault_path(vid)
            if not base:
                return self.send_json({"error": "vault_not_found"}, 404)
            return self.send_bytes(dashboard_html(vid, base).encode())

        m = re.fullmatch(r"/api/vaults/([^/]+)/export", path)
        if m:
            vid = m.group(1)
            base = vault_path(vid)
            if not base:
                return self.send_json({"error": "vault_not_found"}, 404)
            return self.export_zip(vid, base)

        m = re.fullmatch(r"/api/vaults/([^/]+)/share", path)
        if m:
            vid = m.group(1)
            base = vault_path(vid)
            if not base:
                return self.send_json({"error": "vault_not_found"}, 404)
            return self.send_json(share_payload(vid, base))

        if path.startswith("/api/"):
            vid = qs.get("vault", [DEFAULT_VAULT_ID])[0]
            base = vault_path(vid)
            if not base:
                return self.send_json({"error": "vault_not_found"}, 404)
            routes = {
                "/api/stats": lambda: stats(base),
                "/api/timeline": lambda: {"items": timeline(base)},
                "/api/map": lambda: {"items": map_items(base)},
                "/api/entities": lambda: {"items": records(base)},
                "/api/events": lambda: {"items": records(base, "wydarzenie")},
                "/api/sources": lambda: {"items": records(base, "zrodlo")},
                "/api/relations": lambda: {"items": records(base, "relacja")},
                "/api/series": lambda: {"items": records(base, "seria")},
                "/api/gaps": lambda: {"items": gaps(base)},
                "/api/provenance": lambda: {"items": [r for r in records(base) if any(k in r for k in ("zrodlo","źródło","zrodla","sources"))]},
            }
            if path in routes:
                return self.send_json(routes[path]())
        return self.send_json({"error": "not_found"}, 404)

    def do_POST(self):
        if self.path != "/api/vaults/upload":
            return self.send_json({"error": "not_found"}, 404)
        length = int(self.headers.get("Content-Length", "0"))
        if length <= 0 or length > MAX_UPLOAD:
            return self.send_json({"error": "upload_too_large_or_empty"}, 413)
        body = self.rfile.read(length)
        ctype = self.headers.get("Content-Type", "")
        if "multipart/form-data" not in ctype:
            return self.send_json({"error": "expected_multipart_form_data"}, 400)
        try:
            msg = BytesParser(policy=email_policy).parsebytes(
                ("Content-Type: " + ctype + "\r\nMIME-Version: 1.0\r\n\r\n").encode() + body
            )
            upload = None
            filename = "vault.zip"
            for part in msg.iter_attachments():
                if part.get_filename():
                    upload = part.get_payload(decode=True)
                    filename = part.get_filename()
                    break
            if not upload or not filename.lower().endswith(".zip"):
                return self.send_json({"error": "zip_file_required"}, 400)
            with zipfile.ZipFile(io.BytesIO(upload)) as z:
                infos = [i for i in z.infolist() if not i.is_dir()]
                if len(infos) > 5000:
                    return self.send_json({"error": "too_many_files"}, 413)
                total = 0
                for i in infos:
                    parts = Path(i.filename).parts
                    if i.filename.startswith("/") or ".." in parts or any(p.startswith(".") for p in parts):
                        continue
                    if i.file_size > MAX_FILE:
                        continue
                    total += i.file_size
                    if total > MAX_UPLOAD:
                        return self.send_json({"error": "extracted_data_too_large"}, 413)
                stem = safe_name(Path(filename).stem)
                vid = stem
                n = 1
                while (ROOT / vid).exists() or vid == DEFAULT_VAULT_ID:
                    vid = f"{stem}-{n}"
                    n += 1
                target = ROOT / vid
                target.mkdir(parents=True, exist_ok=False)
                for i in infos:
                    parts = Path(i.filename).parts
                    if i.filename.startswith("/") or ".." in parts or any(p.startswith(".") for p in parts):
                        continue
                    if i.file_size > MAX_FILE:
                        continue
                    dest = target.joinpath(*parts)
                    dest.parent.mkdir(parents=True, exist_ok=True)
                    dest.write_bytes(z.read(i))
            return self.send_json({"vault_id": vid, "file_count": len(md_files(target))}, 201)
        except (zipfile.BadZipFile, ValueError, OSError) as exc:
            return self.send_json({"error": "invalid_zip", "detail": str(exc)}, 400)

    def export_zip(self, vid, base):
        buf = io.BytesIO()
        with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as z:
            for p in files(base):
                if p.stat().st_size > MAX_FILE:
                    continue
                z.write(p, p.relative_to(base))
        name = safe_name(vid) + ".zip"
        return self.send_bytes(
            buf.getvalue(),
            200,
            "application/zip",
            {"Content-Disposition": f'attachment; filename="{name}"'},
        )

    def landing_html(self):
        vaults = []
        if ROOT.exists():
            if any(ROOT.glob("*.md")):
                vaults.append((DEFAULT_VAULT_ID, DEFAULT_VAULT_NAME))
            for d in sorted(ROOT.iterdir()):
                if d.is_dir() and not d.name.startswith(".") and any(d.rglob("*.md")):
                    if d.name == "zjazd-gnieznienski":
                        vaults.append((DEFAULT_VAULT_ID, DEFAULT_VAULT_NAME))
                    elif d.name != DEFAULT_VAULT_ID:
                        vaults.append((d.name, vault_name(d.name, d)))
        cards = "".join(
            f"<div class='card'><h2>{html.escape(name)}</h2><p class='muted'>{html.escape(vid)}</p>"
            f"<div class='actions'><a class='btn cyan' href='/vault/{html.escape(vid)}'>Share</a>"
            f"<a class='btn amber' href='/dashboard?vault={html.escape(vid)}'>Open</a>"
            f"<a class='btn' href='/api/vaults/{html.escape(vid)}/export'>ZIP</a>"
            f"<a class='btn' href='/api/stats?vault={html.escape(vid)}'>Stats</a></div></div>"
            for vid, name in vaults
        )
        body = f"<h1>Historian OS SKYNET</h1><p>Evidence-first historical research engine.</p><div class='grid'>{cards}</div><h2>Upload</h2><form action='/api/vaults/upload' method='post' enctype='multipart/form-data'><input type='file' name='file' accept='.zip' required><button class='btn cyan' type='submit'>Upload ZIP</button></form><p class='muted'>ZIP jest rozpakowywany do osobnego vaulta; pliki ukryte i większe niż 5 MB są pomijane.</p>"
        return html_page("Historian OS SKYNET", body)

    def log_message(self, *args):
        pass


if __name__ == "__main__":
    ThreadingHTTPServer(("0.0.0.0", int(os.environ.get("PORT", "8080"))), Handler).serve_forever()
