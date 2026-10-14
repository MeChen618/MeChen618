"""Generate the animated "AstaPS server console" SVG with live repository stats.

Run by .github/workflows/profile.yml once a day:
    python3 scripts/gen_console.py dist/astaps-console.svg

Uses only the standard library. Set GITHUB_TOKEN to avoid API rate limits.
"""
import datetime
import json
import math
import os
import sys
import urllib.request
from html import escape

REPO = "MeChen618/AstaPS"
API = os.environ.get("ASTAPS_API", "https://api.github.com")
MONO = "'JetBrains Mono','Cascadia Code','SFMono-Regular',Consolas,'DejaVu Sans Mono',monospace"


def get(path):
    req = urllib.request.Request(API + path, headers={"Accept": "application/vnd.github+json"})
    if os.environ.get("GITHUB_TOKEN"):
        req.add_header("Authorization", "Bearer " + os.environ["GITHUB_TOKEN"])
    with urllib.request.urlopen(req, timeout=20) as r:
        return json.load(r)


def fetch_stats():
    repo = get(f"/repos/{REPO}")
    issues = get(f"/search/issues?q=repo:{REPO}+type:issue+state:open&per_page=1")
    return repo["stargazers_count"], repo["forks_count"], issues["total_count"]


def render(stars, forks, issues, now):
    W, H, TOP, LH = 850, 470, 62, 25
    log = [
        ("INFO", "#7ee787", "Starting AstaPS · Grasscutter 7.1.0 (optimized)"),
        ("INFO", "#7ee787", "Loading resources ........................ done in 1.2s"),
        ("INFO", "#7ee787", "Dispatch server listening on 0.0.0.0:443"),
        ("INFO", "#7ee787", "Game server listening on 0.0.0.0:22102"),
        ("INFO", "#7ee787", "Player Asta joined · \"an ordinary person.\""),
        ("WARN", "#f0b35b", "Coffee level low. Continuing anyway."),
        ("INFO", "#7ee787", "/tps enabled · third-person shooting is live"),
    ]
    p = [f'''<svg xmlns="http://www.w3.org/2000/svg" xml:space="preserve" width="{W}" height="{H}" viewBox="0 0 {W} {H}" font-family="{MONO}" font-size="13.5">
  <defs>
    <linearGradient id="bg" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#0b0f17"/><stop offset="1" stop-color="#111827"/></linearGradient>
    <pattern id="scan" width="4" height="4" patternUnits="userSpaceOnUse"><rect width="4" height="1" fill="#ffffff05"/></pattern>
  </defs>
  <rect width="{W}" height="{H}" rx="12" fill="url(#bg)" stroke="#263042"/>
  <rect width="{W}" height="{H}" rx="12" fill="url(#scan)"/>
  <rect width="{W}" height="38" rx="12" fill="#151c2a"/><rect y="26" width="{W}" height="12" fill="#151c2a"/>
  <circle cx="22" cy="19" r="6" fill="#ff5f57"/><circle cx="42" cy="19" r="6" fill="#febc2e"/><circle cx="62" cy="19" r="6" fill="#28c840"/>
  <text x="{W / 2}" y="24" text-anchor="middle" fill="#7d86a8" font-size="12.5">AstaPS — server console</text>
  <circle cx="{W - 30}" cy="19" r="4" fill="#28c840"><animate attributeName="opacity" values="1;.25;1" dur="1.6s" repeatCount="indefinite"/></circle>
  <text x="{W - 42}" y="23.5" text-anchor="end" fill="#28c840" font-size="11.5">ONLINE</text>''']

    for i, (lvl, col, msg) in enumerate(log):
        stamp = (now + datetime.timedelta(seconds=i)).strftime("%H:%M:%S")
        p.append(f'''  <g opacity="0"><set attributeName="opacity" to="1" begin="{0.4 + i * 0.55:.2f}s" fill="freeze"/>
    <text x="24" y="{TOP + i * LH}"><tspan fill="#56607a">[{stamp} </tspan><tspan fill="{col}">{lvl}</tspan><tspan fill="#56607a">]</tspan><tspan fill="#c9d1e6">  {escape(msg)}</tspan></text></g>''')

    # prompt typing /stats
    ty, cmd = TOP + len(log) * LH + 6, "/stats"
    t0 = 0.4 + len(log) * 0.55 + 0.3
    p.append(f'''  <g opacity="0"><set attributeName="opacity" to="1" begin="{t0:.2f}s" fill="freeze"/>
    <text x="24" y="{ty}" fill="#7ee787">&gt;</text>''')
    for k, ch in enumerate(cmd):
        p.append(f'''    <text x="{42 + k * 8.15:.1f}" y="{ty}" fill="#e6edf3" opacity="0">{escape(ch)}<set attributeName="opacity" to="1" begin="{t0 + 0.15 + k * 0.09:.2f}s" fill="freeze"/></text>''')
    p.append(f'''    <rect x="{42 + len(cmd) * 8.15 + 3:.1f}" y="{ty - 12}" width="8" height="15" fill="#e6edf3"><animate attributeName="opacity" values="1;1;0;0" keyTimes="0;.5;.5;1" dur="1s" repeatCount="indefinite"/></rect>
  </g>''')

    # stat tiles (TPS is decorative: 20 ticks/s, and a nod to the /tps command)
    tiles = [("STARS", str(stars), "#f0b35b", "★"), ("FORKS", str(forks), "#6cc5ff", "⑂"),
             ("OPEN ISSUES", str(issues), "#ff7b72", "●"), ("TPS", "20.0", "#7ee787", "▲")]
    tw, tg, top, th = 186, 16, 290, 92
    panel_t = t0 + 0.9
    for i, (label, val, col, icon) in enumerate(tiles):
        x, bt = 24 + i * (tw + tg), panel_t + i * 0.12
        p.append(f'''  <g opacity="0" transform="translate(0 8)">
    <set attributeName="opacity" to="1" begin="{bt:.2f}s" fill="freeze"/>
    <animateTransform attributeName="transform" type="translate" from="0 8" to="0 0" begin="{bt:.2f}s" dur=".35s" fill="freeze"/>
    <rect x="{x}" y="{top}" width="{tw}" height="{th}" rx="8" fill="#ffffff07" stroke="{col}" stroke-opacity=".35"/>
    <text x="{x + 14}" y="{top + 24}" fill="#7d86a8" font-size="11" letter-spacing="1.5">{icon} {label}</text>
    <text x="{x + 14}" y="{top + 66}" fill="{col}" font-size="34" font-weight="bold">{escape(val)}</text>''')
        if label == "TPS":
            pts = " ".join(f"{x + 96 + j * 6},{top + 64 - 12 * (0.55 + 0.45 * math.sin(j * 1.3) * math.cos(j * 0.4)):.1f}" for j in range(14))
            p.append(f'''    <polyline points="{pts}" fill="none" stroke="{col}" stroke-width="1.6" stroke-opacity=".8"/>''')
        p.append("  </g>")

    p.append(f'''  <g opacity="0"><set attributeName="opacity" to="1" begin="{panel_t + 0.7:.2f}s" fill="freeze"/>
    <line x1="24" y1="408" x2="{W - 24}" y2="408" stroke="#263042"/>
    <text x="24" y="436" fill="#7d86a8" font-size="12">Asta · USA · Java ☕   discord: <tspan fill="#a5b4fc">mechen618</tspan></text>
    <text x="{W - 24}" y="436" text-anchor="end" fill="#56607a" font-size="11.5">updated {now:%Y-%m-%d} UTC · TPS = ticks/s · /tps = third-person shooting</text>
  </g>
</svg>''')
    return "\n".join(p) + "\n"


if __name__ == "__main__":
    out = sys.argv[1] if len(sys.argv) > 1 else "dist/astaps-console.svg"
    os.makedirs(os.path.dirname(out) or ".", exist_ok=True)
    now = datetime.datetime.now(datetime.timezone.utc).replace(microsecond=0)
    with open(out, "w", encoding="utf-8") as f:
        f.write(render(*fetch_stats(), now))
    print("wrote", out)
