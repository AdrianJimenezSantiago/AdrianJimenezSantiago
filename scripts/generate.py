#!/usr/bin/env python3
"""Generate every SVG used by the profile README.

Static artwork (header, terminal, project cards, footer) is always rebuilt.
Live metrics (stats, languages, activity) are fetched from the GitHub GraphQL
API when a token is available in GH_TOKEN / GITHUB_TOKEN; otherwise a calm
"syncing" placeholder is written so the README never shows a broken image.

Standard library only, so the workflow needs no dependencies.

    python scripts/generate.py            # static + live (if token)
    python scripts/generate.py --demo     # static + live with sample data
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import math
import os
import random
import urllib.request
from pathlib import Path
from xml.sax.saxutils import escape

USER = "AdrianJimenezSantiago"
ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "assets"
GEN = OUT / "generated"

SANS = "-apple-system,BlinkMacSystemFont,'Segoe UI','Helvetica Neue',Helvetica,Arial,sans-serif"
SERIF = "'Iowan Old Style','Palatino Linotype',Palatino,Georgia,'Times New Roman',serif"
MONO = "ui-monospace,SFMono-Regular,'SF Mono',Menlo,Consolas,'Liberation Mono',monospace"

THEMES = {
    "dark": {
        "bg": "#0d1117",
        "panel": "#10161f",
        "panel2": "#141b26",
        "border": "#232c3a",
        "text": "#ece6d8",
        "muted": "#8d97a6",
        "faint": "#1b2330",
        "gold": "#d9b36c",
        "gold2": "#f1d79c",
        "blue": "#7aa2f7",
        "green": "#7fd1a8",
        "red": "#f38b8b",
        "star": "#ece6d8",
    },
    "light": {
        "bg": "#ffffff",
        "panel": "#fbf9f4",
        "panel2": "#f4f0e6",
        "border": "#e4dccb",
        "text": "#1b2230",
        "muted": "#5d6878",
        "faint": "#efe9dc",
        "gold": "#9c7426",
        "gold2": "#c49a45",
        "blue": "#3456c8",
        "green": "#2f8a5f",
        "red": "#c24a4a",
        "star": "#9c7426",
    },
}

LANG_COLORS = {
    "Python": "#3572A5", "JavaScript": "#f1e05a", "TypeScript": "#3178c6",
    "Java": "#b07219", "C#": "#178600", "HTML": "#e34c26", "CSS": "#663399",
    "SCSS": "#c6538c", "Kotlin": "#A97BFF", "Shell": "#89e051", "RobotFramework": "#00c0b5",
    "Dockerfile": "#384d54", "Jinja": "#a52a22", "Vue": "#41b883",
}

REDUCED_MOTION = (
    "@media (prefers-reduced-motion: reduce){*{animation:none!important}"
    ".in,.ln{opacity:1!important;transform:none!important}"
    ".b,.bar{transform:none!important}.line{stroke-dashoffset:0!important}}"
)


def svg(width: int, height: int, body: str, style: str, title: str) -> str:
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
        f'viewBox="0 0 {width} {height}" role="img" aria-labelledby="t">'
        f"<title id=\"t\">{escape(title)}</title>"
        f"<style>{style}{REDUCED_MOTION}</style>{body}</svg>\n"
    )


def write(name: str, content: str, generated: bool = False) -> None:
    path = (GEN if generated else OUT) / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def stars(rng: random.Random, n: int, w: int, h: int, c: dict, avoid=None) -> str:
    out = []
    for i in range(n):
        x, y = rng.uniform(8, w - 8), rng.uniform(8, h - 8)
        if avoid and avoid(x, y):
            continue
        r = rng.choice([0.6, 0.8, 0.8, 1.0, 1.3])
        cls = "tw" if i % 3 == 0 else ""
        delay = rng.uniform(0, 6)
        out.append(
            f'<circle class="{cls}" cx="{x:.1f}" cy="{y:.1f}" r="{r}" fill="{c["star"]}" '
            f'opacity="{rng.uniform(.25, .7):.2f}" style="animation-delay:{delay:.1f}s"/>'
        )
    return "".join(out)


# --------------------------------------------------------------------------- header

def header(theme: str) -> str:
    c = THEMES[theme]
    w, h = 1200, 340
    rng = random.Random(7)
    cx, cy, rx, ry = 935, 172, 210, 64
    orbit = f"M {cx - rx} {cy} a {rx} {ry} 0 1 0 {2 * rx} 0 a {rx} {ry} 0 1 0 {-2 * rx} 0"
    orbit2 = f"M {cx - 128} {cy} a 128 40 0 1 1 256 0 a 128 40 0 1 1 -256 0"
    style = f"""
    .eyebrow{{font:600 13px {SANS};letter-spacing:.32em;fill:{c['gold']}}}
    .name{{font:400 58px {SERIF};fill:{c['text']};letter-spacing:-.01em}}
    .sub{{font:400 19px {SANS};fill:{c['muted']}}}
    .meta{{font:500 13px {MONO};fill:{c['muted']};letter-spacing:.04em}}
    .meta b{{fill:{c['gold']}}}
    .in{{opacity:0;animation:in 1.1s cubic-bezier(.2,.7,.2,1) forwards}}
    .d1{{animation-delay:.15s}}.d2{{animation-delay:.35s}}.d3{{animation-delay:.6s}}.d4{{animation-delay:.85s}}
    @keyframes in{{from{{opacity:0;transform:translateY(10px)}}to{{opacity:1;transform:none}}}}
    .tw{{animation:tw 4.5s ease-in-out infinite}}
    @keyframes tw{{0%,100%{{opacity:.15}}50%{{opacity:.9}}}}
    .line{{stroke-dasharray:240;stroke-dashoffset:240;animation:draw 1.4s .4s ease forwards}}
    @keyframes draw{{to{{stroke-dashoffset:0}}}}
    .glow{{animation:glow 6s ease-in-out infinite}}
    @keyframes glow{{0%,100%{{opacity:.55}}50%{{opacity:.9}}}}
    """
    body = f"""
    <defs>
      <radialGradient id="halo" cx="78%" cy="50%" r="55%">
        <stop offset="0" stop-color="{c['gold']}" stop-opacity=".16"/>
        <stop offset="1" stop-color="{c['gold']}" stop-opacity="0"/>
      </radialGradient>
      <radialGradient id="planet" cx="35%" cy="30%" r="75%">
        <stop offset="0" stop-color="{c['gold2']}"/>
        <stop offset=".55" stop-color="{c['gold']}"/>
        <stop offset="1" stop-color="{c['panel']}"/>
      </radialGradient>
      <linearGradient id="hair" x1="0" x2="1">
        <stop offset="0" stop-color="{c['gold']}"/><stop offset="1" stop-color="{c['gold']}" stop-opacity="0"/>
      </linearGradient>
      <clipPath id="frame"><rect width="{w}" height="{h}" rx="18"/></clipPath>
    </defs>
    <g clip-path="url(#frame)">
      <rect width="{w}" height="{h}" fill="{c['panel']}"/>
      <rect width="{w}" height="{h}" fill="url(#halo)" class="glow"/>
      {stars(rng, 140, w, h, c, avoid=lambda x, y: x < 640 and 70 < y < 280)}
      <g fill="none" stroke-linecap="round">
        <path d="{orbit}" stroke="{c['gold']}" stroke-opacity=".35" stroke-dasharray="2 7" transform="rotate(-12 {cx} {cy})"/>
        <path d="{orbit2}" stroke="{c['blue']}" stroke-opacity=".28" stroke-dasharray="1 5" transform="rotate(8 {cx} {cy})"/>
      </g>
      <circle cx="{cx}" cy="{cy}" r="46" fill="url(#planet)"/>
      <ellipse cx="{cx}" cy="{cy}" rx="78" ry="14" fill="none" stroke="{c['gold2']}" stroke-opacity=".55" stroke-width="1.4" transform="rotate(-18 {cx} {cy})"/>
      <g transform="rotate(-12 {cx} {cy})">
        <g>
          <rect x="-9" y="-3" width="7" height="6" rx="1" fill="{c['blue']}"/>
          <rect x="2" y="-3" width="7" height="6" rx="1" fill="{c['blue']}"/>
          <rect x="-2.5" y="-4" width="5" height="8" rx="1.2" fill="{c['text']}"/>
          <animateMotion dur="22s" repeatCount="indefinite" rotate="auto" path="{orbit}"/>
        </g>
      </g>
      <g transform="rotate(8 {cx} {cy})">
        <circle r="3.2" fill="{c['gold2']}">
          <animateMotion dur="13s" repeatCount="indefinite" path="{orbit2}" keyPoints="1;0" keyTimes="0;1" calcMode="linear"/>
        </circle>
      </g>
      <g transform="translate(72 0)">
        <text class="eyebrow in d1" x="0" y="104">SOFTWARE DEVELOPER · INDRA ESPACIO</text>
        <path class="line" d="M0 122 H220" stroke="url(#hair)" stroke-width="1.5"/>
        <text class="name in d2" x="-3" y="186">Adrián Jiménez Santiago</text>
        <text class="sub in d3" x="0" y="226">Clean, reliable software, from backend services to the browser.</text>
        <text class="meta in d4" x="0" y="272"><tspan fill="{c['gold']}">◆</tspan><tspan dx="10">Málaga, España</tspan><tspan dx="22" fill="{c['gold']}">◆</tspan><tspan dx="10">Java · Spring · Angular · Python</tspan></text>
      </g>
      <rect x=".5" y=".5" width="{w - 1}" height="{h - 1}" rx="18" fill="none" stroke="{c['border']}"/>
    </g>
    """
    return svg(w, h, body, style, "Adrián Jiménez Santiago, Software Developer at Indra Espacio")


# --------------------------------------------------------------------------- terminal

def terminal(theme: str) -> str:
    c = THEMES[theme]
    w = 1200
    k, s, g, b, m, t = c["blue"], c["green"], c["gold"], c["text"], c["muted"], c["text"]

    def kv(key: str, val: str) -> str:
        return f'<tspan fill="{k}">{key}</tspan><tspan fill="{m}">: </tspan>{val}'

    def st(text: str) -> str:
        return f'<tspan fill="{s}">{escape(text)}</tspan>'

    def lst(*items: str) -> str:
        inner = f'<tspan fill="{m}">, </tspan>'.join(st(i) for i in items)
        return f'<tspan fill="{m}">[</tspan>{inner}<tspan fill="{m}">]</tspan>'

    lines: list[tuple[str, str]] = [
        ("cmd", "whoami"),
        ("out", f'<tspan fill="{b}">Adrián Jiménez Santiago</tspan><tspan fill="{m}">  ·  software developer who enjoys turning ideas into tools people use</tspan>'),
        ("gap", ""),
        ("cmd", "cat profile.yaml"),
        ("out", kv("role", st("Junior Software Developer @ Indra Espacio"))),
        ("out", kv("based_in", st("Málaga, Spain"))),
        ("out", kv("languages", lst("Español (native)", "English"))),
        ("out", kv("focus", lst("full-stack web", "clean architecture", "local-first apps"))),
        ("out", kv("backend", lst("Java", "Spring Boot", "Python", "FastAPI", "C#"))),
        ("out", kv("frontend", lst("TypeScript", "Angular", "React", "Next.js", "Tailwind"))),
        ("out", kv("quality", lst("CI/CD", "typed code", "automated tests", "Robot Framework"))),
        ("out", kv("learning_now", lst("Angular signals", "Spring Boot 3", "cloud on AWS"))),
        ("out", kv("motto", st('"Code is the canvas. Logic is the brush."'))),
        ("gap", ""),
        ("cmd", ""),
    ]
    top, lh = 76, 27
    h = top + lh * len(lines) + 14
    style = f"""
    .t{{font:400 15.5px {MONO};fill:{t}}}
    .p{{fill:{g}}}
    .ttl{{font:500 12.5px {MONO};fill:{m};letter-spacing:.04em}}
    .ln{{opacity:0;animation:show .01s forwards}}
    @keyframes show{{to{{opacity:1}}}}
    .cur{{animation:blink 1.05s steps(1) infinite}}
    @keyframes blink{{50%{{opacity:0}}}}
    """
    rows, tline = [], 0.3
    for i, (kind, content) in enumerate(lines):
        y = top + i * lh
        if kind == "gap":
            continue
        if kind == "cmd":
            cmd_w = 9.35 * len(content)
            typing = 0.045 * max(len(content), 1)
            prompt = f'<tspan class="p">adrian@indra</tspan><tspan fill="{m}">:</tspan><tspan fill="{k}">~</tspan><tspan fill="{m}">$ </tspan>'
            px = 32 + 9.35 * 16
            if content:
                rows.append(
                    f'<g class="ln" style="animation-delay:{tline:.2f}s">'
                    f'<text class="t" x="32" y="{y}">{prompt}</text>'
                    f'<clipPath id="c{i}"><rect x="{px}" y="{y - 18}" height="24" width="0">'
                    f'<animate attributeName="width" from="0" to="{cmd_w + 4:.0f}" begin="{tline:.2f}s" dur="{typing:.2f}s" fill="freeze"/></rect></clipPath>'
                    f'<text class="t" x="{px}" y="{y}" clip-path="url(#c{i})">{escape(content)}</text></g>'
                )
                tline += typing + 0.35
            else:
                rows.append(
                    f'<g class="ln" style="animation-delay:{tline:.2f}s">'
                    f'<text class="t" x="32" y="{y}">{prompt}</text>'
                    f'<rect class="cur" x="{px + 1}" y="{y - 15}" width="9" height="19" fill="{g}"/></g>'
                )
        else:
            rows.append(f'<text class="t ln" x="32" y="{y}" style="animation-delay:{tline:.2f}s">{content}</text>')
            tline += 0.12
    body = f"""
    <rect x=".5" y=".5" width="{w - 1}" height="{h - 1}" rx="14" fill="{c['panel']}" stroke="{c['border']}"/>
    <path d="M1 44 H{w - 1}" stroke="{c['border']}"/>
    <circle cx="28" cy="22" r="6" fill="{c['red']}" opacity=".85"/>
    <circle cx="48" cy="22" r="6" fill="{c['gold']}" opacity=".85"/>
    <circle cx="68" cy="22" r="6" fill="{c['green']}" opacity=".85"/>
    <text class="ttl" x="{w / 2}" y="27" text-anchor="middle">adrian@indra — ~/profile — zsh</text>
    {''.join(rows)}
    """
    return svg(w, h, body, style, "About Adrián: Junior Software Developer at Indra Espacio, Málaga")


# --------------------------------------------------------------------------- project cards

PROJECTS = {
    "mtg-forge": {
        "title": "MPC Forge",
        "kicker": "LOCAL-FIRST DESKTOP APP",
        "tagline": "From any decklist to print-ready Magic: The Gathering proxies.",
        "points": [
            "Imports decks from 7+ sites, resolved through Scryfall",
            "SQLite FTS5 art index with perceptual-hash dedupe",
            "PDF Studio: bleed, cut guides, duplex calibration",
            "Packaged with PyInstaller · i18n (es / en) · CI releases",
        ],
        "chips": ["Python", "FastAPI", "SQLAlchemy", "Alpine.js", "Tailwind"],
        "lang": "Python",
        "glyph": "forge",
    },
    "dnd-grimoire": {
        "title": "Grimorio",
        "kicker": "OFFLINE-FIRST MOBILE & WEB APP",
        "tagline": "A D&D 2024 character sheet and spellbook that does the maths.",
        "points": [
            "Full 2024 rules: every class and subclass, 1 to 20",
            "Android APK with Capacitor + installable PWA on Vercel",
            "Combat mode, dice roller, inventory and journal",
            "Reads your own rulebook PDFs on-device with PDF.js",
        ],
        "chips": ["JavaScript", "Vite", "Capacitor", "Android", "PDF.js"],
        "lang": "JavaScript",
        "glyph": "book",
    },
}


def glyph(kind: str, c: dict) -> str:
    if kind == "forge":
        return (
            f'<g fill="none" stroke="{c["gold"]}" stroke-width="1.6" stroke-linejoin="round">'
            f'<rect x="-15" y="-19" width="22" height="30" rx="3"/>'
            f'<rect x="-7" y="-12" width="22" height="30" rx="3" fill="{c["panel2"]}"/>'
            f'<path d="M4 -2 l3 6 -3 6 -3 -6z" fill="{c["gold"]}" stroke="none"/></g>'
        )
    return (
        f'<g fill="none" stroke="{c["gold"]}" stroke-width="1.6" stroke-linejoin="round">'
        f'<path d="M0 -12 C-6 -17 -14 -17 -19 -15 V14 C-14 12 -6 12 0 17 C6 12 14 12 19 14 V-15 C14 -17 6 -17 0 -12 Z"/>'
        f'<path d="M0 -12 V17"/><path d="M9 -6 l1.6 3.4 3.7 .5 -2.7 2.6 .7 3.7 -3.3 -1.8 -3.3 1.8 .7 -3.7 -2.7 -2.6 3.7 -.5z" fill="{c["gold"]}" stroke="none"/></g>'
    )


def project_card(key: str, theme: str) -> str:
    c, p = THEMES[theme], PROJECTS[key]
    w, h = 600, 330
    style = f"""
    .k{{font:600 11px {SANS};letter-spacing:.26em;fill:{c['gold']}}}
    .ti{{font:400 30px {SERIF};fill:{c['text']}}}
    .tg{{font:400 14.5px {SANS};fill:{c['muted']}}}
    .pt{{font:400 14px {SANS};fill:{c['text']}}}
    .ch{{font:500 11.5px {MONO};fill:{c['text']}}}
    .ft{{font:500 12px {MONO};fill:{c['muted']}}}
    .sweep{{animation:sw 7s ease-in-out infinite}}
    @keyframes sw{{0%{{transform:translateX(-260px)}}60%,100%{{transform:translateX({w + 40}px)}}}}
    """
    pts = "".join(
        f'<circle cx="40" cy="{164 + i * 27}" r="2.4" fill="{c["gold"]}"/>'
        f'<text class="pt" x="54" y="{169 + i * 27}">{escape(t)}</text>'
        for i, t in enumerate(p["points"])
    )
    chips, x = [], 32
    for ch in p["chips"]:
        cw = 7.1 * len(ch) + 22
        chips.append(
            f'<rect x="{x}" y="{h - 52}" width="{cw:.0f}" height="24" rx="12" fill="{c["faint"]}" stroke="{c["border"]}"/>'
            f'<text class="ch" x="{x + cw / 2:.0f}" y="{h - 36}" text-anchor="middle">{escape(ch)}</text>'
        )
        x += cw + 8
    body = f"""
    <defs>
      <linearGradient id="sh" x1="0" x2="1"><stop offset="0" stop-color="{c['gold']}" stop-opacity="0"/>
      <stop offset=".5" stop-color="{c['gold']}" stop-opacity=".09"/><stop offset="1" stop-color="{c['gold']}" stop-opacity="0"/></linearGradient>
      <clipPath id="cc"><rect width="{w}" height="{h}" rx="16"/></clipPath>
    </defs>
    <g clip-path="url(#cc)">
      <rect width="{w}" height="{h}" fill="{c['panel']}"/>
      <rect class="sweep" x="0" y="0" width="220" height="{h}" fill="url(#sh)" transform="skewX(-12)"/>
      <rect width="{w}" height="3" fill="{c['gold']}"/>
    </g>
    <rect x=".5" y=".5" width="{w - 1}" height="{h - 1}" rx="16" fill="none" stroke="{c['border']}"/>
    <g transform="translate({w - 56} 58)">
      <circle r="30" fill="{c['panel2']}" stroke="{c['border']}"/>{glyph(p['glyph'], c)}
    </g>
    <text class="k" x="32" y="48">{escape(p['kicker'])}</text>
    <text class="ti" x="31" y="88">{escape(p['title'])}</text>
    <text class="tg" x="32" y="118">{escape(p['tagline'])}</text>
    <path d="M32 138 H{w - 32}" stroke="{c['border']}"/>
    {pts}
    {''.join(chips)}
    <text class="ft" x="{w - 32}" y="{h - 36}" text-anchor="end">view ↗</text>
    """
    return svg(w, h, body, style, f"{p['title']}: {p['tagline']}")


# --------------------------------------------------------------------------- principles

PRINCIPLES = [
    ("01", "Local-first", "Your data stays on your device:", "no accounts, works offline."),
    ("02", "Automated quality", "CI on every push, linters, typed", "code and tests before release."),
    ("03", "Built for people", "Clear UX, accessible, translated,", "and documented end to end."),
]


def principles(theme: str) -> str:
    c = THEMES[theme]
    w, h = 1200, 170
    colw = (w - 1 - 2 * 24) / 3
    style = f"""
    .n{{font:400 34px {SERIF};fill:{c['gold']}}}
    .h{{font:600 17px {SANS};fill:{c['text']}}}
    .d{{font:400 14px {SANS};fill:{c['muted']}}}
    .in{{opacity:0;animation:in .9s ease forwards}}
    @keyframes in{{from{{opacity:0;transform:translateY(8px)}}to{{opacity:1;transform:none}}}}
    """
    cols = []
    for i, (n, head, l1, l2) in enumerate(PRINCIPLES):
        x = .5 + i * (colw + 24)
        cols.append(
            f'<g transform="translate({x:.1f} .5)"><g class="in" style="animation-delay:{.15 + i * .2:.2f}s">'
            f'<rect width="{colw:.0f}" height="{h - 1}" rx="14" fill="{c["panel"]}" stroke="{c["border"]}"/>'
            f'<text class="n" x="24" y="58">{n}</text>'
            f'<path d="M24 74 H64" stroke="{c["gold"]}" stroke-width="1.5"/>'
            f'<text class="h" x="24" y="104">{head}</text>'
            f'<text class="d" x="24" y="130">{escape(l1)}</text>'
            f'<text class="d" x="24" y="150">{escape(l2)}</text></g></g>'
        )
    return svg(w, h, "".join(cols), style, "Engineering principles: local-first, automated quality, built for people")


# --------------------------------------------------------------------------- footer

def footer(theme: str) -> str:
    c = THEMES[theme]
    w, h = 1200, 120
    rng = random.Random(3)
    style = f"""
    .m{{font:italic 400 17px {SERIF};fill:{c['muted']};letter-spacing:.06em}}
    .tw{{animation:tw 4s ease-in-out infinite}}
    @keyframes tw{{0%,100%{{opacity:.15}}50%{{opacity:.85}}}}
    """
    body = f"""
    <defs><linearGradient id="f" x1="0" x2="1">
      <stop offset="0" stop-color="{c['gold']}" stop-opacity="0"/><stop offset=".5" stop-color="{c['gold']}" stop-opacity=".7"/>
      <stop offset="1" stop-color="{c['gold']}" stop-opacity="0"/></linearGradient></defs>
    {stars(rng, 50, w, h, c, avoid=lambda x, y: 380 < x < 820)}
    <path d="M140 62 H520" stroke="url(#f)"/><path d="M680 62 H1060" stroke="url(#f)"/>
    <text class="m" x="{w / 2}" y="68" text-anchor="middle">ad astra per codicem</text>
    """
    return svg(w, h, body, style, "Ad astra per codicem: to the stars through code")


# --------------------------------------------------------------------------- live metrics

QUERY = """
query($login: String!) {
  user(login: $login) {
    createdAt
    followers { totalCount }
    pullRequests { totalCount }
    issues { totalCount }
    repositoriesContributedTo(contributionTypes: [COMMIT, PULL_REQUEST, ISSUE]) { totalCount }
    repositories(first: 100, ownerAffiliations: OWNER, isFork: false) {
      totalCount
      nodes {
        stargazerCount
        languages(first: 10, orderBy: {field: SIZE, direction: DESC}) {
          edges { size node { name color } }
        }
      }
    }
    contributionsCollection {
      totalCommitContributions
      restrictedContributionsCount
      totalPullRequestContributions
      contributionCalendar {
        totalContributions
        weeks { contributionDays { date contributionCount } }
      }
    }
  }
}
"""


def fetch(token: str) -> dict:
    req = urllib.request.Request(
        "https://api.github.com/graphql",
        data=json.dumps({"query": QUERY, "variables": {"login": USER}}).encode(),
        headers={"Authorization": f"bearer {token}", "User-Agent": USER},
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        payload = json.load(r)
    if "errors" in payload:
        raise RuntimeError(payload["errors"])
    return payload["data"]["user"]


def demo_data() -> dict:
    rng = random.Random(42)
    start = dt.date.today() - dt.timedelta(days=364)
    weeks = []
    for wk in range(53):
        days = []
        for d in range(7):
            day = start + dt.timedelta(days=wk * 7 + d)
            base = 1 + 3 * (1 + math.sin(wk / 5))
            days.append({"date": day.isoformat(), "contributionCount": max(0, int(rng.gauss(base, 2.5)))})
        weeks.append({"contributionDays": days})
    total = sum(d["contributionCount"] for w in weeks for d in w["contributionDays"])
    langs = [("Python", 52), ("JavaScript", 31), ("TypeScript", 8), ("HTML", 5), ("CSS", 4)]
    return {
        "createdAt": "2025-03-18T16:01:50Z",
        "followers": {"totalCount": 0},
        "pullRequests": {"totalCount": 64},
        "issues": {"totalCount": 18},
        "repositoriesContributedTo": {"totalCount": 3},
        "repositories": {"totalCount": 8, "nodes": [{"stargazerCount": 0, "languages": {"edges": [
            {"size": s * 1000, "node": {"name": n, "color": LANG_COLORS.get(n)}} for n, s in langs]}}]},
        "contributionsCollection": {
            "totalCommitContributions": 812, "restrictedContributionsCount": 140,
            "totalPullRequestContributions": 58,
            "contributionCalendar": {"totalContributions": total, "weeks": weeks},
        },
    }


def fmt(n: int) -> str:
    return f"{n / 1000:.1f}k" if n >= 10000 else f"{n:,}".replace(",", " ")


def stats_card(data: dict | None, theme: str) -> str:
    c = THEMES[theme]
    w, h = 600, 300
    style = f"""
    .k{{font:600 11px {SANS};letter-spacing:.26em;fill:{c['gold']}}}
    .v{{font:400 34px {SERIF};fill:{c['text']}}}
    .l{{font:500 12.5px {SANS};fill:{c['muted']}}}
    .s{{font:400 14px {SANS};fill:{c['muted']}}}
    .in{{opacity:0;animation:in .8s ease forwards}}
    @keyframes in{{from{{opacity:0;transform:translateY(6px)}}to{{opacity:1;transform:none}}}}
    """
    frame = (
        f'<rect x=".5" y=".5" width="{w - 1}" height="{h - 1}" rx="16" fill="{c["panel"]}" stroke="{c["border"]}"/>'
        f'<text class="k" x="32" y="48">THE YEAR IN NUMBERS</text>'
    )
    if not data:
        return svg(w, h, frame + f'<text class="s" x="32" y="150">Syncing with GitHub… metrics refresh daily.</text>', style, "GitHub metrics")
    cc = data["contributionsCollection"]
    stars_total = sum(n["stargazerCount"] for n in data["repositories"]["nodes"])
    kpis = [
        (cc["totalCommitContributions"] + cc["restrictedContributionsCount"], "commits · last 12 months"),
        (cc["contributionCalendar"]["totalContributions"], "total contributions"),
        (data["pullRequests"]["totalCount"], "pull requests"),
        (data["repositories"]["totalCount"], "repositories"),
        (data["issues"]["totalCount"], "issues"),
        (stars_total, "stars earned"),
    ]
    cells = []
    for i, (v, label) in enumerate(kpis):
        col, row = i % 3, i // 3
        x, y = 32 + col * 184, 112 + row * 92
        cells.append(
            f'<g class="in" style="animation-delay:{.1 + i * .08:.2f}s">'
            f'<text class="v" x="{x}" y="{y}">{fmt(v)}</text>'
            f'<text class="l" x="{x}" y="{y + 24}">{label}</text></g>'
        )
    divider = f'<path d="M32 {h - 50} H{w - 32}" stroke="{c["border"]}"/>'
    streak = longest_streak(cc["contributionCalendar"]["weeks"])
    foot = f'<text class="l" x="32" y="{h - 24}">Longest streak · <tspan fill="{c["gold"]}">{streak} days</tspan></text>'
    stamp = f'<text class="l" x="{w - 32}" y="{h - 24}" text-anchor="end">updated {dt.date.today():%d %b %Y}</text>'
    return svg(w, h, frame + "".join(cells) + divider + foot + stamp, style, "GitHub metrics for the last 12 months")


def longest_streak(weeks: list) -> int:
    best = cur = 0
    for wk in weeks:
        for d in wk["contributionDays"]:
            cur = cur + 1 if d["contributionCount"] else 0
            best = max(best, cur)
    return best


def languages_card(data: dict | None, theme: str) -> str:
    c = THEMES[theme]
    w, h = 600, 300
    style = f"""
    .k{{font:600 11px {SANS};letter-spacing:.26em;fill:{c['gold']}}}
    .n{{font:500 14px {SANS};fill:{c['text']}}}
    .p{{font:500 13px {MONO};fill:{c['muted']}}}
    .s{{font:400 14px {SANS};fill:{c['muted']}}}
    .bar{{transform-origin:left;transform:scaleX(0);animation:grow 1.2s cubic-bezier(.2,.7,.2,1) forwards}}
    @keyframes grow{{to{{transform:scaleX(1)}}}}
    """
    frame = (
        f'<rect x=".5" y=".5" width="{w - 1}" height="{h - 1}" rx="16" fill="{c["panel"]}" stroke="{c["border"]}"/>'
        f'<text class="k" x="32" y="48">LANGUAGES I SHIP IN</text>'
    )
    if not data:
        return svg(w, h, frame + '<text class="s" x="32" y="150">Syncing with GitHub… metrics refresh daily.</text>', style, "Top languages")
    sizes: dict[str, int] = {}
    colors: dict[str, str] = {}
    for repo in data["repositories"]["nodes"]:
        for e in repo["languages"]["edges"]:
            name = e["node"]["name"]
            sizes[name] = sizes.get(name, 0) + e["size"]
            colors[name] = e["node"].get("color") or LANG_COLORS.get(name, c["muted"])
    total = sum(sizes.values()) or 1
    top = sorted(sizes.items(), key=lambda kv: -kv[1])[:6]
    rows = []
    bar_x, bar_w = 160, w - 160 - 90
    for i, (name, size) in enumerate(top):
        y = 92 + i * 32
        pct = size / total
        rows.append(
            f'<circle cx="38" cy="{y - 5}" r="5" fill="{colors[name]}"/>'
            f'<text class="n" x="52" y="{y}">{escape(name)}</text>'
            f'<rect x="{bar_x}" y="{y - 10}" width="{bar_w}" height="8" rx="4" fill="{c["faint"]}"/>'
            f'<rect class="bar" style="animation-delay:{.1 + i * .1:.1f}s" x="{bar_x}" y="{y - 10}" '
            f'width="{max(bar_w * pct, 8):.1f}" height="8" rx="4" fill="{colors[name]}"/>'
            f'<text class="p" x="{w - 32}" y="{y}" text-anchor="end">{pct * 100:.1f}%</text>'
        )
    return svg(w, h, frame + "".join(rows), style, "Top languages across my repositories")


def activity_card(data: dict | None, theme: str) -> str:
    c = THEMES[theme]
    w, h = 1200, 260
    style = f"""
    .k{{font:600 11px {SANS};letter-spacing:.26em;fill:{c['gold']}}}
    .s{{font:400 14px {SANS};fill:{c['muted']}}}
    .t{{font:400 26px {SERIF};fill:{c['text']}}}
    .m{{font:500 11.5px {MONO};fill:{c['muted']}}}
    .b{{transform-box:fill-box;transform-origin:bottom;transform:scaleY(0);animation:up .9s cubic-bezier(.2,.7,.2,1) forwards}}
    @keyframes up{{to{{transform:scaleY(1)}}}}
    """
    frame = (
        f'<rect x=".5" y=".5" width="{w - 1}" height="{h - 1}" rx="16" fill="{c["panel"]}" stroke="{c["border"]}"/>'
        f'<text class="k" x="32" y="48">ACTIVITY · LAST 52 WEEKS</text>'
    )
    if not data:
        return svg(w, h, frame + '<text class="s" x="32" y="140">Syncing with GitHub… metrics refresh daily.</text>', style, "Contribution activity")
    cal = data["contributionsCollection"]["contributionCalendar"]
    weeks = cal["weeks"][-52:]
    sums = [sum(d["contributionCount"] for d in wk["contributionDays"]) for wk in weeks]
    peak = max(sums) or 1
    x0, base, plot_h = 32, h - 46, 128
    gap = 4
    bw = (w - 64 - gap * (len(sums) - 1)) / len(sums)
    bars, labels, last_month = [], [], None
    for i, (wk, v) in enumerate(zip(weeks, sums)):
        x = x0 + i * (bw + gap)
        bh = max(3, plot_h * (v / peak) ** 0.8)
        op = 0.35 + 0.65 * (v / peak)
        bars.append(
            f'<rect class="b" style="animation-delay:{i * .018:.3f}s" x="{x:.1f}" y="{base - bh:.1f}" '
            f'width="{bw:.1f}" height="{bh:.1f}" rx="{min(3, bw / 2):.1f}" fill="{c["gold"]}" fill-opacity="{op:.2f}"/>'
        )
        first = dt.date.fromisoformat(wk["contributionDays"][0]["date"])
        if first.month != last_month and first.day <= 7:
            labels.append(f'<text class="m" x="{x:.1f}" y="{h - 22}">{first:%b}</text>')
            last_month = first.month
    head = (
        f'<text class="t" x="{w - 32}" y="52" text-anchor="end">{fmt(cal["totalContributions"])}'
        f'<tspan class="s" dx="8">contributions in the last year</tspan></text>'
    )
    axis = f'<path d="M32 {base + .5} H{w - 32}" stroke="{c["border"]}"/>'
    return svg(w, h, frame + head + "".join(bars) + axis + "".join(labels), style, "Weekly contribution activity over the last year")


# --------------------------------------------------------------------------- main

def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--demo", action="store_true", help="render live cards with sample data")
    ap.add_argument("--static-only", action="store_true")
    args = ap.parse_args()

    for theme in THEMES:
        write(f"header-{theme}.svg", header(theme))
        write(f"about-{theme}.svg", terminal(theme))
        write(f"principles-{theme}.svg", principles(theme))
        write(f"footer-{theme}.svg", footer(theme))
        for key in PROJECTS:
            write(f"project-{key}-{theme}.svg", project_card(key, theme))

    if args.static_only:
        return
    token = os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN")
    data = None
    if args.demo:
        data = demo_data()
    elif token:
        try:
            data = fetch(token)
        except Exception as exc:  # keep the last good cards rather than failing the README
            print(f"::warning::Could not fetch GitHub metrics: {exc}")
    if data is None and (GEN / "stats-dark.svg").exists():
        print("No token: keeping existing live metrics.")
        return
    for theme in THEMES:
        write(f"stats-{theme}.svg", stats_card(data, theme), generated=True)
        write(f"languages-{theme}.svg", languages_card(data, theme), generated=True)
        write(f"activity-{theme}.svg", activity_card(data, theme), generated=True)
    print("Live metrics:", "demo" if args.demo else ("fetched" if data else "placeholder"))


if __name__ == "__main__":
    main()
