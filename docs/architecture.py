"""Generates docs/architecture.svg. Edit this file, never the SVG.

Run: python docs/architecture.py
"""
from pathlib import Path
from xml.sax.saxutils import escape

TITLE = "ads-mcp-agent — architecture, v0.2"
FOOTER = ("Every box in “what it writes” answers one of the "
          "experiment's questions. Everything else exists to produce it.")

# (heading, verb into this band, fill, stroke, boxes[(title, line1, line2)])
LAYERS = [
    ("PEOPLE", None, "#f3effa", "#7b5ea7", [
        ("You", "ask in plain words,", "approve every write"),
    ]),
    ("WHAT YOU OPEN", "opens", "#eef3fb", "#2f4a7a", [
        ("Chat page", "ask, see the agent's plan,", "say yes or no"),
        ("Write log page", "every change, before", "and after values"),
    ]),
    ("WHAT RUNS", "drives", "#eef6f1", "#2e6b4a", [
        ("Agent loop", "sends the chat and tool list,", "gets back a tool call"),
        ("Confirm gate", "holds a write until", "you say yes"),
        ("Cap check", "refuses a write", "above the spend cap"),
        ("MCP client", "lists tools,", "calls the one chosen"),
    ]),
    ("WHAT IT WRITES", "writes", "#fdf6ea", "#a8780f", [
        ("Write log", "what changed, from what,", "on whose yes"),
        ("Call log", "each ask, the tools it used,", "and how many calls"),
        ("Tool gaps", "asks no tool", "could answer"),
    ]),
    ("HOW IT REACHES AMAZON", "sends and reads through", "#f6f3ee", "#7d6440", [
        ("Endpoint switch", "fake server or", "Amazon's NA endpoint"),
        ("Token refresher", "swaps the refresh token", "for an hourly access token"),
        ("Secrets", "held by the host,", "never in the repo"),
    ]),
    ("EVERYTHING ELSE", "talks to", "#f3f4f6", "#6b7280", [
        ("Claude API", "the model", ""),
        ("Fake MCP server", "same tool shapes,", "no Amazon needed"),
        ("Amazon Ads MCP", "the real tools,", "once approved"),
        ("Login with Amazon", "issues access", "tokens"),
    ]),
]

W, PAD, BOX_W, BOX_H, GAP = 1000, 30, 215, 66, 16
BAND_H, HEAD_H, ARROW_H = BOX_H + 30, 26, 34
FONT = "font-family='DejaVu Sans, Helvetica, Arial, sans-serif'"


def box(x, y, title, l1, l2, stroke):
    out = [f"<rect x='{x}' y='{y}' width='{BOX_W}' height='{BOX_H}' rx='6' "
           f"fill='#ffffff' stroke='{stroke}' stroke-width='1.4'/>"]
    cx = x + BOX_W / 2
    out.append(f"<text x='{cx}' y='{y + 22}' text-anchor='middle' {FONT} "
               f"font-size='14' font-weight='700' fill='#1f2937'>"
               f"{escape(title)}</text>")
    for i, line in enumerate((l1, l2)):
        if line:
            out.append(f"<text x='{cx}' y='{y + 40 + i * 15}' "
                       f"text-anchor='middle' {FONT} font-size='11.5' "
                       f"fill='#4b5563'>{escape(line)}</text>")
    return out


def build():
    parts, y = [], 40
    parts.append(f"<text x='{PAD}' y='{y - 12}' {FONT} font-size='18' "
                 f"font-weight='700' fill='#111827'>{escape(TITLE)}</text>")
    for heading, verb, fill, stroke, boxes in LAYERS:
        if verb:
            ax = W / 2
            parts.append(f"<line x1='{ax}' y1='{y + 4}' x2='{ax}' "
                         f"y2='{y + ARROW_H - 8}' stroke='#6b7280' "
                         f"stroke-width='1.4' marker-end='url(#arrow)'/>")
            parts.append(f"<text x='{ax + 10}' y='{y + 20}' {FONT} "
                         f"font-size='11.5' font-style='italic' "
                         f"fill='#6b7280'>{escape(verb)}</text>")
            y += ARROW_H
        parts.append(f"<text x='{PAD + 8}' y='{y + 16}' {FONT} "
                     f"font-size='12' font-weight='700' letter-spacing='2' "
                     f"fill='#6b7280'>{heading}</text>")
        y += HEAD_H
        parts.append(f"<rect x='{PAD}' y='{y}' width='{W - 2 * PAD}' "
                     f"height='{BAND_H}' rx='10' fill='{fill}' "
                     f"stroke='#9ca3af' stroke-dasharray='6 4'/>")
        for i, (t, a, b) in enumerate(boxes):
            parts += box(PAD + 15 + i * (BOX_W + GAP), y + 15, t, a, b,
                         stroke)
        y += BAND_H
    y += 28
    parts.append(f"<text x='{PAD}' y='{y}' {FONT} font-size='12' "
                 f"fill='#4b5563'>{escape(FOOTER)}</text>")
    h = y + 20
    head = (f"<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 {W} {h}' "
            f"width='100%'><defs><marker id='arrow' viewBox='0 0 10 10' "
            f"refX='9' refY='5' markerWidth='7' markerHeight='7' "
            f"orient='auto'><path d='M0,0 L10,5 L0,10 z' fill='#6b7280'/>"
            f"</marker></defs><rect width='{W}' height='{h}' fill='#ffffff'/>")
    return head + "".join(parts) + "</svg>\n"


if __name__ == "__main__":
    out = Path(__file__).with_name("architecture.svg")
    out.write_text(build())
    print(f"wrote {out}")
