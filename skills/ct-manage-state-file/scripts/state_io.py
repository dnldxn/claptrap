#!/usr/bin/env python3
# /// script
# dependencies = ["beautifulsoup4"]
# ///
import argparse, datetime as dt, html, json, sys
from pathlib import Path
from bs4 import BeautifulSoup

SCHEMA = {"meta": {"state": "...", "last_action": "...", "last_updated": "YYYY-mm-dd H:M:S", "branch": "..."}, "summary": "...", "open": [{"spec": "...", "summary": "...", "plans": [{"file": "...", "summary": "...", "note": "optional"}]}], "archived": []}
TEMPLATE_PATH = Path(__file__).resolve().parent.parent / "assets/state.template.html"

def now(): return dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
def defaults(): return {"meta": {"state": "", "last_action": "", "last_updated": now(), "branch": ""}, "summary": "", "open": [], "archived": []}
def esc(s): return html.escape(str(s or ""), quote=True)

def schema_error(msg):
    return f'invalid payload: {msg}\nexpected schema: {json.dumps(SCHEMA,separators=(",",":"))}\npartial patch supported: send only fields to update.'

def validate(payload):
    if not isinstance(payload, dict): return "top-level JSON must be an object"
    allowed = {"meta", "summary", "open", "archived"}; bad = sorted(set(payload) - allowed)
    if bad: return f"unknown top-level fields: {', '.join(bad)}"
    if "summary" in payload and not isinstance(payload["summary"], str): return "summary must be a string"
    if "meta" in payload:
        if not isinstance(payload["meta"], dict): return "meta must be an object"
        m_allowed = {"state", "last_action", "last_updated", "branch"}; m_bad = sorted(set(payload["meta"]) - m_allowed)
        if m_bad: return f"unknown meta fields: {', '.join(m_bad)}"
        if any(not isinstance(v, str) for v in payload["meta"].values()): return "meta values must be strings"
    for section in ("open", "archived"):
        if section in payload:
            if not isinstance(payload[section], list): return f"{section} must be a list"
            for g in payload[section]:
                if not isinstance(g, dict): return f"{section} entries must be objects"
                if not isinstance(g.get("spec", ""), str) or not isinstance(g.get("summary", ""), str): return f"{section} entry spec/summary must be strings"
                plans = g.get("plans", [])
                if not isinstance(plans, list): return f"{section} entry plans must be a list"
                for p in plans:
                    if not isinstance(p, dict) or not isinstance(p.get("file", ""), str) or not isinstance(p.get("summary", ""), str): return f"{section} plan file/summary must be strings"
                    if "note" in p and not isinstance(p["note"], str): return f"{section} plan note must be a string"
    return None

def read_state(path):
    if not path.exists(): return defaults()
    soup = BeautifulSoup(path.read_text(encoding="utf-8"), "html.parser")
    script = soup.find("script", {"id": "state-data"})
    if script and script.string:
        try: return json.loads(script.string.strip())
        except Exception: pass
    data = defaults()
    for label, key in (("State", "state"), ("Last action", "last_action"), ("Last updated", "last_updated"), ("Branch", "branch")):
        dt_tag = soup.find("dt", string=lambda s: s and s.strip().lower() == label.lower())
        dd_tag = dt_tag.find_next_sibling("dd") if dt_tag else None
        if dd_tag: data["meta"][key] = dd_tag.get_text(" ", strip=True)
    h2 = soup.find("h2", string=lambda s: s and s.strip().lower() == "summary")
    p_tag = h2.find_next_sibling("p") if h2 else None
    if p_tag: data["summary"] = p_tag.get_text(" ", strip=True)
    return data

def render_accordion(groups):
    if not groups: return '<div class="empty muted">No entries</div>'
    out = []
    for g in groups:
        plans = g.get("plans", [])
        rows = "".join(
            f"<tr><td>{i}</td><td><code>{esc(p.get('file',''))}</code></td><td>{esc(p.get('summary',''))}"
            + (f' <span class="muted">{esc(p["note"])}</span>' if p.get("note") else "")
            + "</td></tr>"
            for i, p in enumerate(plans, start=1)
        ) or '<tr><td colspan="3" class="muted">No plans</td></tr>'
        out.append(f'<details class="item"><summary><code>{esc(g.get("spec",""))}</code></summary><div class="item-body"><p class="group-summary">{esc(g.get("summary",""))}</p><table class="plans-table"><tbody>{rows}</tbody></table></div></details>')
    return "".join(out)

def render_html(data):
    t = TEMPLATE_PATH.read_text(encoding="utf-8")
    state_json = json.dumps(data, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
    repl = {"{{STATE}}": esc(data["meta"].get("state", "")), "{{LAST_ACTION}}": esc(data["meta"].get("last_action", "")), "{{LAST_UPDATED}}": esc(data["meta"].get("last_updated", "")), "{{BRANCH}}": esc(data["meta"].get("branch", "")), "{{SUMMARY}}": esc(data.get("summary", "")), "{{OPEN_ACCORDION}}": render_accordion(data.get("open", [])), "{{ARCHIVED_ACCORDION}}": render_accordion(data.get("archived", [])), "{{STATE_JSON}}": state_json}
    for k, v in repl.items(): t = t.replace(k, v)
    return t

def main():
    p = argparse.ArgumentParser(add_help=False); p.add_argument("--help", action="store_true"); p.add_argument("--file", default=".planning/state.html")
    sub = p.add_subparsers(dest="cmd"); sub.add_parser("read", add_help=False); w = sub.add_parser("write", add_help=False); w.add_argument("--json", required=True)
    a = p.parse_args()
    if a.help or not a.cmd:
        print("Usage: state_io.py [--file .planning/state.html] read|write --json '<payload>'\nInfo: reads/writes structured state fields in HTML.\nFields: meta.state,last_action,last_updated,branch; summary; open[]; archived[].\nSchema: " + json.dumps(SCHEMA, separators=(",", ":")) + "\nPatch: write supports partial updates (only provided fields are changed)."); return
    path = Path(a.file); current = read_state(path)
    if a.cmd == "read": print(json.dumps(current, indent=2, ensure_ascii=False)); return
    try: patch = json.loads(a.json)
    except Exception: print(schema_error("malformed JSON"), file=sys.stderr); sys.exit(1)
    err = validate(patch)
    if err: print(schema_error(err), file=sys.stderr); sys.exit(1)
    merged = {"meta": {**current.get("meta", {}), **patch.get("meta", {})}, "summary": patch.get("summary", current.get("summary", "")), "open": patch.get("open", current.get("open", [])), "archived": patch.get("archived", current.get("archived", []))}
    path.parent.mkdir(parents=True, exist_ok=True); path.write_text(render_html(merged), encoding="utf-8")
    print(json.dumps(merged, indent=2, ensure_ascii=False))

if __name__ == "__main__": main()
