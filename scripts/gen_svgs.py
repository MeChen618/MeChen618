"""Generate the animated SVGs for the profile README.

Edit SCRIPT (terminal lines) or STATS (character card bars), then run:
    python3 scripts/gen_svgs.py
"""
import os
import random
from html import escape

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets")
MONO = "'JetBrains Mono','Cascadia Code','SFMono-Regular',Consolas,'Liberation Mono',monospace"

# ---------------------------------------------------------------- terminal
# (kind, text) - "cmd" lines are typed out, "out" lines appear at once
SCRIPT = [
    ("cmd", "whoami"),
    ("out", "asta  ·  an ordinary person."),
    ("cmd", "cat about.txt"),
    ("out", "location : USA"),
    ("out", "language : Java ☕  (and whatever the bug needs)"),
    ("out", "hobby    : making game servers run faster than they should"),
    ("cmd", "ls ~/projects"),
    ("out", "AstaPS/    next-idea/    todo-forever.md"),
    ("cmd", "sudo become-extraordinary"),
    ("out", "[sudo] password for asta: ********"),
    ("err", "Permission denied. Still ordinary. Still shipping."),
]

W, LINE_H, TOP, LEFT = 820, 24, 62, 26
H = TOP + LINE_H * (len(SCRIPT) + 1) + 10
CHAR_W = 8.6          # approx width of a 14px monospace char
TYPE_SPEED = 0.07     # seconds per char
PAUSE = 0.45

parts = [f'''<svg xmlns="http://www.w3.org/2000/svg" xml:space="preserve" style="white-space:pre" width="{W}" height="{H}" viewBox="0 0 {W} {H}" font-family="{MONO}" font-size="14">
  <defs>
    <linearGradient id="bg" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0" stop-color="#0f1320"/><stop offset="1" stop-color="#171b2e"/>
    </linearGradient>
  </defs>
  <rect width="{W}" height="{H}" rx="12" fill="url(#bg)" stroke="#2b3150"/>
  <rect width="{W}" height="36" rx="12" fill="#1c2136"/>
  <rect y="24" width="{W}" height="12" fill="#1c2136"/>
  <circle cx="22" cy="18" r="6" fill="#ff5f57"/><circle cx="42" cy="18" r="6" fill="#febc2e"/><circle cx="62" cy="18" r="6" fill="#28c840"/>
  <text x="{W/2}" y="23" text-anchor="middle" fill="#7d86a8" font-size="13">asta@earth: ~</text>''']

t = 0.6
y = TOP
for i, (kind, text) in enumerate(SCRIPT):
    if kind == "cmd":
        dur = max(len(text) * TYPE_SPEED, 0.2)
        parts.append(f'''  <clipPath id="c{i}"><rect x="{LEFT}" y="{y-16}" height="{LINE_H}" width="{2*CHAR_W}"><animate attributeName="width" begin="{t:.2f}s" dur="{dur:.2f}s" fill="freeze" calcMode="discrete" keyTimes="{';'.join(f'{k/(len(text)+1):.4f}' for k in range(len(text)+1))}" values="{';'.join(f'{(3+k)*CHAR_W+4:.1f}' for k in range(len(text)+1))}"/></rect></clipPath>
  <g opacity="0"><set attributeName="opacity" to="1" begin="{t-0.3:.2f}s" fill="freeze"/>
    <text x="{LEFT}" y="{y}" clip-path="url(#c{i})"><tspan fill="#7ee787">❯ </tspan><tspan fill="#e6edf3">{escape(text)}</tspan></text>
  </g>''')
        t += dur + PAUSE
    else:
        color = {"out": "#a5b1d6", "err": "#ff7b72"}[kind]
        parts.append(f'''  <text x="{LEFT}" y="{y}" fill="{color}" opacity="0" xml:space="preserve">{escape(text)}<set attributeName="opacity" to="1" begin="{t:.2f}s" fill="freeze"/></text>''')
        t += 0.25 if SCRIPT[i + 1:i + 2] and SCRIPT[i + 1][0] != "cmd" else PAUSE + 0.2
    y += LINE_H

# final prompt with blinking cursor
parts.append(f'''  <g opacity="0"><set attributeName="opacity" to="1" begin="{t:.2f}s" fill="freeze"/>
    <text x="{LEFT}" y="{y}" fill="#7ee787">❯</text>
    <rect x="{LEFT + 2*CHAR_W}" y="{y-13}" width="8" height="16" fill="#e6edf3"><animate attributeName="opacity" values="1;1;0;0" keyTimes="0;0.5;0.5;1" dur="1s" repeatCount="indefinite"/></rect>
  </g>
</svg>''')

with open(f"{OUT}/terminal.svg", "w") as f:
    f.write("\n".join(parts) + "\n")

# ---------------------------------------------------------------- character card
random.seed(618)
CW, CH = 820, 300
STATS = [  # label, value (0-100), color
    ("Java", 88, "#f0b35b"),
    ("Server / Networking", 76, "#6cc5ff"),
    ("Debugging", 81, "#b58cff"),
    ("Coffee Resistance", 12, "#ff7b72"),
]

stars = "\n".join(
    f'    <circle cx="{random.randint(0, CW)}" cy="{random.randint(0, CH)}" r="{random.choice([0.8, 1, 1.3])}" fill="#fff">'
    f'<animate attributeName="opacity" values="0.15;0.9;0.15" dur="{random.uniform(2, 5):.1f}s" begin="{random.uniform(0, 3):.1f}s" repeatCount="indefinite"/></circle>'
    for _ in range(46)
)

bars = []
bx, by = 330, 176
for k, (label, val, color) in enumerate(STATS):
    yy = by + k * 28
    full = 300 * val / 100
    shown = "∞" if label == "Coffee Resistance" else str(val)
    bars.append(f'''    <text x="{bx}" y="{yy}" fill="#c9d1f0" font-size="13">{escape(label)}</text>
    <text x="{bx + 450}" y="{yy}" fill="{color}" font-size="13" text-anchor="end" font-weight="bold">{shown}</text>
    <rect x="{bx + 150}" y="{yy - 10}" width="250" height="8" rx="4" fill="#ffffff14"/>
    <rect x="{bx + 150}" y="{yy - 10}" width="0" height="8" rx="4" fill="{color}"><animate attributeName="width" from="0" to="{full * 250 / 300:.1f}" begin="{0.6 + k * 0.2:.1f}s" dur="1.2s" fill="freeze" calcMode="spline" keySplines="0.2 0.8 0.2 1" keyTimes="0;1"/></rect>''')

card = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{CW}" height="{CH}" viewBox="0 0 {CW} {CH}" font-family="'Segoe UI','PingFang SC','Microsoft YaHei','Noto Sans CJK SC',Helvetica,Arial,sans-serif">
  <defs>
    <linearGradient id="sky" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0" stop-color="#101629"/><stop offset="0.6" stop-color="#1d1b3f"/><stop offset="1" stop-color="#2a1f4a"/>
    </linearGradient>
    <linearGradient id="gold" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0" stop-color="#ffe7a8"/><stop offset="1" stop-color="#d49a3a"/>
    </linearGradient>
    <radialGradient id="glow"><stop offset="0" stop-color="#f7c96b" stop-opacity="0.45"/><stop offset="1" stop-color="#f7c96b" stop-opacity="0"/></radialGradient>
    <clipPath id="frame"><rect width="{CW}" height="{CH}" rx="16"/></clipPath>
  </defs>
  <g clip-path="url(#frame)">
    <rect width="{CW}" height="{CH}" fill="url(#sky)"/>
{stars}
    <circle cx="160" cy="150" r="140" fill="url(#glow)"/>
  </g>
  <rect x="1" y="1" width="{CW-2}" height="{CH-2}" rx="16" fill="none" stroke="url(#gold)" stroke-opacity="0.55"/>

  <!-- emblem -->
  <g transform="translate(160 150)">
    <circle r="92" fill="none" stroke="url(#gold)" stroke-width="1.5" stroke-dasharray="4 8">
      <animateTransform attributeName="transform" type="rotate" from="0" to="360" dur="40s" repeatCount="indefinite"/>
    </circle>
    <g>
      <polygon points="0,-78 67,-39 67,39 0,78 -67,39 -67,-39" fill="#ffffff08" stroke="url(#gold)" stroke-width="2"/>
      <animateTransform attributeName="transform" type="rotate" from="360" to="0" dur="60s" repeatCount="indefinite"/>
    </g>
    <circle r="58" fill="#141a33" stroke="url(#gold)" stroke-width="2"/>
    <text y="22" text-anchor="middle" font-size="64" font-weight="700" fill="url(#gold)" font-family="Georgia,'Times New Roman',serif">A</text>
    <g fill="url(#gold)">
      <path d="M0,-104 l4,8 -4,8 -4,-8z"/><path d="M0,104 l4,-8 -4,-8 -4,8z"/>
    </g>
  </g>

  <!-- identity -->
  <text x="330" y="70" fill="#8e97c2" font-size="13" letter-spacing="3">CHARACTER · 角色档案</text>
  <text x="330" y="112" fill="#fff" font-size="40" font-weight="700" letter-spacing="1">Asta</text>
  <text x="440" y="112" fill="url(#gold)" font-size="22">★★★★★</text>
  <text x="330" y="140" fill="#c9d1f0" font-size="15" font-style="italic">“An ordinary person.” — 一个平平无奇的普通人</text>
{chr(10).join(bars)}
  <text x="{CW-24}" y="{CH-16}" fill="#5d6591" font-size="11" text-anchor="end">Class: Server Tinkerer · Region: USA · Element: ☕</text>
</svg>
'''
with open(f"{OUT}/character-card.svg", "w") as f:
    f.write(card)
print("generated assets/terminal.svg and assets/character-card.svg")
