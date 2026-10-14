"""Generates docs/architecture.svg. Edit this file, never the SVG.

Run: python docs/architecture.py
"""
from pathlib import Path
from xml.sax.saxutils import escape

TITLE = "ads-mcp-agent — reference architecture, v0.3"
FOOTER = ("Each record in the persistence layer answers one evaluation "
          "question; the remaining layers exist to produce those records.")

# (heading, verb into this band, fill, stroke, boxes[(title, line1, line2)])
LAYERS = [
    ("ACTOR", None, "#f3effa", "#7b5ea7", [
        ("Owner", "issues requests and", "authorises every write"),
    ]),
    ("PRESENTATION", "uses", "#eef3fb", "#2f4a7a", [
        ("Chat interface", "requests, proposed actions,", "approval decisions"),
        ("Change history", "applied writes with", "prior and new values"),
    ]),
    ("APPLICATION", "invokes", "#eef6f1", "#2e6b4a", [
        ("Agent orchestrator", "model call with tool", "catalogue; tool selection"),
        ("Approval gate", "suspends writes pending", "explicit authorisation"),
        ("Spend guard", "rejects writes that", "exceed the spend cap"),
        ("MCP client", "tool discovery and", "invocation"),
    ]),
    ("PERSISTENCE", "records", "#fdf6ea", "#a8780f", [
        ("Write audit", "change, prior value,", "authorising approval"),
        ("Invocation log", "request, tools used,", "API call count"),
        ("Coverage gaps", "requests with no", "matching tool"),
    ]),
    ("INTEGRATION", "connects through", "#f6f3ee", "#7d6440", [
        ("Endpoint selector", "simulator or Amazon", "North America endpoint"),
        ("Token manager", "refresh-token exchange,", "hourly access tokens"),
        ("Secret store", "host-managed;", "excluded from source"),
    ]),
    ("EXTERNAL SERVICES", "calls", "#f3f4f6", "#6b7280", [
        ("Claude API", "language model", ""),
        ("Ads MCP simulator", "local server mirroring", "the tool contracts"),
        ("Amazon Ads MCP", "hosted server; requires", "API approval"),
        ("Login with Amazon", "OAuth authorisation", "server"),
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
