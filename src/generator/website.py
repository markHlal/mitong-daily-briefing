"""Generate the 米桶 AI 早报 website — letterpress morning-gazette edition.

Design language: a printed Chinese morning newspaper.
  · Cream paper, ink black, a single vermilion accent (朱砂).
  · Song/serif headlines with tight leading, oldstyle numerals.
  · Hairline rules and newspaper column-rules instead of cards.
  · Direction-aware masthead (hides on scroll down, returns on scroll up).
  · Lead story and numbered briefs carry RSS images when available,
    with a light sepia tone for a printed-photograph feel.
  · Section tabs filter the news columns by 资讯类型.
  · No external JS/CSS dependencies — everything works offline.
"""

import json
import re
from datetime import datetime
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
OUTPUT_DIR = PROJECT_ROOT / "output"
WEB_DIR = PROJECT_ROOT / "website"

WEEKDAYS_CN = ["星期一", "星期二", "星期三", "星期四", "星期五", "星期六", "星期日"]

# ── News sections (资讯类型栏目) ──
try:
    from utils.config_loader import load_sections, section_of_category
    SECTIONS = [(s["id"], s["name"]) for s in load_sections()]
    if not SECTIONS:
        raise ValueError("no sections configured")
except Exception:  # fallback when utils is not importable
    SECTIONS = [("ai", "AI 资讯"), ("world", "国际时事"), ("finance", "证券资讯")]

    def section_of_category(cat_id: str) -> str:
        return {"world": "world", "finance": "finance"}.get(cat_id, "ai")


# ───────────────────────── helpers ─────────────────────────

def _slug(date: str) -> str:
    """Filesystem-safe slug for a briefing date."""
    return date.replace(" ", "_").replace(".", "-")


def _esc(text) -> str:
    s = str(text or "")
    return (s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
             .replace('"', "&quot;"))


def _fmt_date(date: str) -> str:
    """'2026-07-31' -> '2026年7月31日 星期五' (falls back to raw string)."""
    m = re.match(r"(\d{4})-(\d{2})-(\d{2})", date)
    if not m:
        return date
    try:
        dt = datetime(int(m.group(1)), int(m.group(2)), int(m.group(3)))
        return f"{dt.year}年{dt.month}月{dt.day}日 {WEEKDAYS_CN[dt.weekday()]}"
    except ValueError:
        return date


def _issue_no(date: str) -> str:
    m = re.match(r"(\d{4})-(\d{2})-(\d{2})", date)
    return f"NO.{m.group(1)}{m.group(2)}{m.group(3)}" if m else ""


def _valid_url(url: str) -> bool:
    return bool(url) and url != "#" and url.startswith(("http://", "https://"))


def get_all_briefings() -> list[dict]:
    """Scan output directory and return all briefings sorted by date (newest first)."""
    briefings = []
    if not OUTPUT_DIR.exists():
        return briefings
    for date_dir in sorted(OUTPUT_DIR.iterdir()):
        if not date_dir.is_dir():
            continue
        data_file = date_dir / "data.json"
        if not data_file.exists():
            continue
        data = {}
        try:
            with open(data_file, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception:
            pass
        briefings.append({
            "date": date_dir.name,
            "slug": _slug(date_dir.name),
            "date_cn": _fmt_date(date_dir.name),
            "issue_no": _issue_no(date_dir.name),
            "items": data.get("items", []),
            "highlights": data.get("highlights", []),
        })
    return list(reversed(briefings))


# ───────────────────────── shared CSS ─────────────────────────
CSS = '''<style>
:root {
    --paper: #F6F1E7;
    --paper-deep: #EDE5D4;
    --ink: #1B1611;
    --ink-soft: #57503F;
    --ink-faint: #93876F;
    --verm: #C2341B;
    --verm-deep: #9E2A15;
    --rule: rgba(27, 22, 17, 0.18);
    --rule-soft: rgba(27, 22, 17, 0.09);
    --serif: "Songti SC", "STSong", "Noto Serif SC", "SimSun", Georgia, serif;
    --sans: -apple-system, BlinkMacSystemFont, "SF Pro Text", "PingFang SC", "Microsoft YaHei", sans-serif;
    --ease-out: cubic-bezier(0.19, 1, 0.22, 1);
}
* { margin: 0; padding: 0; box-sizing: border-box; }
html { scroll-behavior: smooth; }
body {
    font-family: var(--sans);
    background: var(--paper);
    color: var(--ink);
    line-height: 1.6;
    font-variant-numeric: oldstyle-nums;
    -webkit-font-smoothing: antialiased;
    -moz-osx-font-smoothing: grayscale;
}
/* paper grain */
body::before {
    content: "";
    position: fixed; inset: 0;
    pointer-events: none;
    z-index: 1;
    opacity: 0.05;
    background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='140' height='140'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='2'/%3E%3C/filter%3E%3Crect width='140' height='140' filter='url(%23n)'/%3E%3C/svg%3E");
}
::selection { background: var(--verm); color: var(--paper); }

/* ── Masthead ── */
.masthead {
    position: fixed; top: 0; left: 0; right: 0;
    z-index: 100;
    background: var(--paper);
    border-bottom: 1px solid var(--rule);
    transition: transform 0.45s var(--ease-out);
}
.masthead.hidden { transform: translateY(-101%); }
.masthead-inner {
    max-width: 1080px;
    margin: 0 auto;
    padding: 13px 28px;
    display: flex;
    align-items: baseline;
    justify-content: space-between;
    gap: 16px;
}
.brand {
    text-decoration: none;
    color: var(--ink);
    display: flex;
    align-items: center;
}
.brand-text {
    display: flex;
    flex-direction: column;
    line-height: 1.2;
}
.brand-name {
    font-family: var(--serif);
    font-size: 19px;
    font-weight: 700;
    letter-spacing: 0.06em;
}
.brand-sub {
    display: flex;
    align-items: center;
    gap: 5px;
    font-size: 10.5px;
    letter-spacing: 0.3em;
    color: var(--ink-faint);
}
.brand-sub img {
    width: 13px;
    height: 13px;
    object-fit: contain;
    border-radius: 3px;
}
.masthead-meta {
    font-size: 12px;
    letter-spacing: 0.14em;
    color: var(--ink-soft);
    text-transform: uppercase;
}
.masthead-meta a {
    color: var(--verm);
    text-decoration: none;
    border-bottom: 1px solid transparent;
    transition: border-color 0.25s;
}
.masthead-meta a:hover { border-color: var(--verm); }

/* ── Front page hero ── */
.frontpage {
    max-width: 1080px;
    margin: 0 auto;
    padding: 118px 28px 0;
    position: relative;
    z-index: 2;
}
.dateline {
    display: flex;
    justify-content: space-between;
    align-items: baseline;
    gap: 12px;
    flex-wrap: wrap;
    border-top: 1px solid var(--ink);
    border-bottom: 1px solid var(--rule);
    padding: 9px 2px;
    font-size: 12.5px;
    letter-spacing: 0.12em;
    color: var(--ink-soft);
    text-transform: uppercase;
}
.dateline .live::before {
    content: "";
    display: inline-block;
    width: 6px; height: 6px;
    background: var(--verm);
    border-radius: 50%;
    margin-right: 7px;
    vertical-align: 1px;
    animation: beat 2.4s ease-in-out infinite;
}
@keyframes beat { 0%, 100% { opacity: 1; } 50% { opacity: 0.25; } }
.nameplate {
    text-align: center;
    padding: 34px 0 26px;
    position: relative;
}
.nameplate h1 {
    font-family: var(--serif);
    font-size: clamp(38px, 5.6vw, 64px);
    font-weight: 900;
    line-height: 1.1;
    letter-spacing: 0.1em;
}
.nameplate .ch-wrap {
    display: inline-block;
    overflow: hidden;
    vertical-align: bottom;
}
.nameplate .ch { display: inline-block; will-change: transform; }
.nameplate .ch-gap { display: inline-block; width: 0.3em; }
.nameplate .latin {
    margin-top: 12px;
    font-size: 11px;
    letter-spacing: 0.52em;
    text-indent: 0.52em;
    text-transform: uppercase;
    color: var(--ink-soft);
}
.nameplate .motto {
    margin-top: 16px;
    font-family: var(--serif);
    font-size: 14px;
    color: var(--ink-faint);
    letter-spacing: 0.3em;
    text-indent: 0.3em;
}
/* vermilion seal (印章), stamped on load */
.seal {
    position: absolute;
    right: 48px;
    top: 8px;
    width: 74px; height: 74px;
    border: 2px solid var(--verm);
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    color: var(--verm);
    font-family: var(--serif);
    font-weight: 700;
    font-size: 17px;
    letter-spacing: 0.12em;
    text-indent: 0.12em;
    transform: rotate(-8deg);
    opacity: 0.92;
}
.seal::after {
    content: "";
    position: absolute; inset: 5px;
    border: 1px solid var(--verm);
    border-radius: 50%;
    opacity: 0.55;
}
/* classic newspaper double rule: thick over thin */
.double-rule {
    border: 0;
    border-top: 3px solid var(--ink);
    border-bottom: 1px solid var(--ink);
    height: 4px;
    margin: 0 0 8px;
}
.thin-rule { border: 0; border-top: 1px solid var(--rule); }

/* ── Section headings ── */
.section { max-width: 1080px; margin: 0 auto; padding: 44px 28px 8px; position: relative; z-index: 2; }
.section-head {
    display: flex;
    align-items: baseline;
    justify-content: space-between;
    gap: 16px;
    margin-bottom: 26px;
}
.section-title {
    font-family: var(--serif);
    font-size: 27px;
    font-weight: 700;
    letter-spacing: 0.08em;
    display: flex;
    align-items: baseline;
    gap: 14px;
}
.section-title .no {
    font-size: 13px;
    color: var(--verm);
    letter-spacing: 0.2em;
    font-family: var(--sans);
}
.section-note {
    font-size: 12px;
    letter-spacing: 0.16em;
    color: var(--ink-faint);
    text-transform: uppercase;
}

/* ── Lead story (头条) ── */
.lead {
    display: grid;
    grid-template-columns: 1fr;
    gap: 14px;
    padding: 30px 0 34px;
    border-top: 1px solid var(--ink);
    border-bottom: 1px solid var(--rule);
    text-decoration: none;
    color: inherit;
}
@media (min-width: 861px) {
    .lead:has(figure) {
        grid-template-columns: 1.1fr 0.9fr;
        gap: 40px;
        align-items: center;
    }
}
.lead-text { display: grid; gap: 14px; }
.kicker {
    font-size: 12px;
    letter-spacing: 0.28em;
    text-transform: uppercase;
    color: var(--verm);
    font-weight: 600;
}
.lead h3 {
    font-family: var(--serif);
    font-size: clamp(30px, 4.6vw, 46px);
    font-weight: 900;
    line-height: 1.22;
    letter-spacing: 0.01em;
    max-width: 22em;
}
.lead p {
    font-size: 16px;
    color: var(--ink-soft);
    max-width: 44em;
    line-height: 1.85;
}
.lead figure {
    border: 1px solid var(--ink);
    outline: 1px solid var(--rule);
    outline-offset: 5px;
    background: var(--paper-deep);
    align-self: center;
}
.lead figure img {
    width: 100%;
    aspect-ratio: 4/3;
    object-fit: cover;
    display: block;
    filter: sepia(0.16) saturate(0.88) contrast(0.98);
}
.byline {
    display: flex;
    gap: 18px;
    font-size: 12.5px;
    letter-spacing: 0.12em;
    color: var(--ink-faint);
    text-transform: uppercase;
}
/* cross-platform attention badge */
.heat {
    color: var(--verm);
    font-weight: 600;
    letter-spacing: 0.14em;
}
.news-item .heat { font-size: 11.5px; }
a.lead h3, a.brief h4 { transition: color 0.25s; }
a.lead:hover h3 { color: var(--verm); }

/* ── Sub-highlights (numbered briefs) ── */
.briefs {
    display: grid;
    grid-template-columns: 1fr 1fr;
}
.brief {
    display: grid;
    grid-template-columns: auto 1fr;
    gap: 20px;
    padding: 26px 0;
    text-decoration: none;
    color: inherit;
}
.brief + .brief { border-left: 1px solid var(--rule); padding-left: 34px; }
.brief:first-child { padding-right: 34px; }
.brief .num {
    font-family: var(--serif);
    font-size: 46px;
    font-weight: 900;
    line-height: 1;
    color: var(--verm);
    font-variant-numeric: oldstyle-nums;
}
.brief .thumb {
    width: 100%;
    aspect-ratio: 16/9;
    object-fit: cover;
    display: block;
    margin-bottom: 14px;
    border: 1px solid var(--ink);
    outline: 1px solid var(--rule);
    outline-offset: 3px;
    filter: sepia(0.14) saturate(0.9) contrast(0.98);
}
.brief h4 {
    font-family: var(--serif);
    font-size: 20px;
    font-weight: 700;
    line-height: 1.4;
    margin: 4px 0 8px;
}
a.brief:hover h4 { color: var(--verm); }
.brief p {
    font-size: 13.5px;
    color: var(--ink-soft);
    line-height: 1.75;
    margin-bottom: 10px;
}

/* ── Section tabs (资讯类型) ── */
.tabs {
    display: flex;
    flex-wrap: wrap;
    border-top: 1px solid var(--ink);
    border-bottom: 1px solid var(--rule);
    margin-bottom: 8px;
}
.tab {
    font-family: var(--sans);
    font-size: 13px;
    letter-spacing: 0.18em;
    padding: 12px 18px 10px;
    background: none;
    border: none;
    border-bottom: 2px solid transparent;
    margin-bottom: -1px;
    cursor: pointer;
    color: var(--ink-soft);
    transition: color 0.25s, border-color 0.25s;
}
.tab .n {
    font-size: 10.5px;
    color: var(--ink-faint);
    margin-left: 6px;
}
.tab:hover { color: var(--ink); }
.tab.active {
    color: var(--verm);
    border-bottom-color: var(--verm);
    font-weight: 600;
}
.tab.active .n { color: var(--verm); }
.tab-empty {
    padding: 52px 20px;
    text-align: center;
    color: var(--ink-faint);
    font-family: var(--serif);
    letter-spacing: 0.24em;
}

/* ── News columns (newspaper column-rule) ── */
.news-columns {
    columns: 3;
    column-gap: 44px;
    column-rule: 1px solid var(--rule-soft);
}
.news-item {
    break-inside: avoid;
    display: block;
    padding: 20px 2px 22px;
    border-bottom: 1px solid var(--rule-soft);
    text-decoration: none;
    color: inherit;
}
.news-item .row {
    display: flex;
    align-items: baseline;
    gap: 12px;
    margin-bottom: 8px;
}
.news-item .idx {
    font-family: var(--serif);
    font-size: 15px;
    font-weight: 700;
    color: var(--verm);
    min-width: 2ch;
}
.tag {
    font-size: 10.5px;
    letter-spacing: 0.2em;
    text-transform: uppercase;
    padding: 2px 9px 1px;
    border: 1px solid currentColor;
    font-weight: 600;
}
.news-item h4 {
    font-family: var(--serif);
    font-size: 17.5px;
    font-weight: 700;
    line-height: 1.5;
    margin-bottom: 7px;
    transition: color 0.25s;
}
a.news-item:hover h4 { color: var(--verm); }
.news-item p {
    font-size: 13px;
    color: var(--ink-soft);
    line-height: 1.75;
    margin-bottom: 9px;
}
.news-item .meta {
    font-size: 11.5px;
    letter-spacing: 0.14em;
    color: var(--ink-faint);
    text-transform: uppercase;
    display: flex;
    justify-content: space-between;
    gap: 10px;
}
.news-item .more {
    color: var(--verm);
    opacity: 0;
    transition: opacity 0.25s;
}
a.news-item:hover .more { opacity: 1; }

/* ── Archive index ── */
.archive-row {
    display: grid;
    grid-template-columns: auto 1fr auto auto;
    align-items: baseline;
    gap: 22px;
    padding: 17px 2px;
    border-bottom: 1px solid var(--rule-soft);
    text-decoration: none;
    color: inherit;
}
.archive-row:first-child { border-top: 1px solid var(--ink); }
.archive-row .a-date {
    font-family: var(--serif);
    font-size: 19px;
    font-weight: 700;
    letter-spacing: 0.04em;
    transition: color 0.25s;
}
.archive-row:hover .a-date { color: var(--verm); }
.archive-row .a-week { font-size: 12.5px; color: var(--ink-faint); letter-spacing: 0.14em; }
.archive-row .a-count { font-size: 12px; letter-spacing: 0.16em; color: var(--ink-soft); text-transform: uppercase; }
.archive-row .a-arrow {
    font-family: var(--serif);
    color: var(--verm);
    transform: translateX(-6px);
    opacity: 0;
    transition: all 0.3s var(--ease-out);
}
.archive-row:hover .a-arrow { transform: translateX(0); opacity: 1; }

/* ── Empty ── */
.empty { text-align: center; padding: 90px 20px; color: var(--ink-faint); font-family: var(--serif); letter-spacing: 0.2em; }

/* ── Footer / colophon ── */
.footer {
    max-width: 1080px;
    margin: 70px auto 0;
    padding: 26px 28px 60px;
    border-top: 3px solid var(--ink);
    position: relative;
    z-index: 2;
    display: flex;
    justify-content: space-between;
    flex-wrap: wrap;
    gap: 12px;
    font-size: 12px;
    letter-spacing: 0.14em;
    color: var(--ink-faint);
    text-transform: uppercase;
}
.footer .zh { font-family: var(--serif); letter-spacing: 0.1em; text-transform: none; }

/* ── Reveal hooks: initial hidden states are set by GSAP only,
     so the page stays fully visible when JS/CDN is unavailable ── */

/* ── Responsive ── */
@media (max-width: 860px) {
    .news-columns { columns: 2; }
    .seal { display: none; }
}
@media (max-width: 640px) {
    .frontpage { padding: 104px 20px 0; }
    .section { padding: 36px 20px 4px; }
    .news-columns { columns: 1; }
    .briefs { grid-template-columns: 1fr; }
    .brief + .brief { border-left: 0; border-top: 1px solid var(--rule); padding-left: 0; }
    .brief:first-child { padding-right: 0; }
    .masthead-inner { padding: 11px 20px; }
    .archive-row { grid-template-columns: 1fr auto; row-gap: 4px; }
    .archive-row .a-week { display: none; }
}
</style>'''


# ───────────────────────── shared JS ─────────────────────────
GSAP_CDN = '''<script src="https://cdnjs.cloudflare.com/ajax/libs/gsap/3.12.5/gsap.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/gsap/3.12.5/ScrollTrigger.min.js"></script>'''

PAGE_JS = '''<script>
// Direction-aware masthead: hide on scroll down, return on scroll up (vanilla, always on).
(function () {
    const mh = document.querySelector(".masthead");
    let lastY = window.scrollY;
    window.addEventListener("scroll", () => {
        const y = window.scrollY;
        if (y > 140 && y > lastY + 4) mh.classList.add("hidden");
        else if (y < lastY - 4 || y <= 140) mh.classList.remove("hidden");
        lastY = y;
    }, { passive: true });
})();

// Section tabs: filter the news columns by 资讯类型 (vanilla, always on).
(function () {
    const tabs = document.querySelectorAll("#news-tabs .tab");
    if (!tabs.length) return;
    const items = document.querySelectorAll("#news-columns .news-item");
    const emptyEl = document.getElementById("news-empty");
    tabs.forEach((tab) => tab.addEventListener("click", () => {
        tabs.forEach((t) => t.classList.remove("active"));
        tab.classList.add("active");
        const sec = tab.dataset.sec;
        let shown = 0;
        items.forEach((it) => {
            const match = sec === "all" || it.dataset.section === sec;
            it.style.display = match ? "" : "none";
            if (match) shown++;
        });
        if (emptyEl) emptyEl.hidden = shown !== 0;
    }));
})();

// ── GSAP choreography ──
// Everything below only runs when the CDN delivered GSAP and the user
// hasn't asked for reduced motion; otherwise the page is simply static.
(function () {
    if (!window.gsap || !window.ScrollTrigger) return;
    if (window.matchMedia("(prefers-reduced-motion: reduce)").matches) return;
    gsap.registerPlugin(ScrollTrigger);

    // · Opening sequence: press-room curtain-up ·
    const tl = gsap.timeline({ defaults: { ease: "power4.out" } });
    tl.from(".masthead-inner", { y: -26, opacity: 0, duration: 0.6 })
        .from(".dateline > *", { y: 14, opacity: 0, stagger: 0.08, duration: 0.5 }, "-=0.25")
        .from(".nameplate .ch", {
            yPercent: 118, rotate: 5, stagger: 0.075, duration: 0.95,
        }, "-=0.2")
        .from(".nameplate .latin, .nameplate .motto", {
            y: 12, opacity: 0, stagger: 0.12, duration: 0.5,
        }, "-=0.55")
        .from(".double-rule", {
            scaleX: 0, transformOrigin: "left center", duration: 0.9, ease: "power3.inOut",
        }, "-=0.35");

    const seal = document.querySelector(".seal");
    if (seal) {
        tl.from(seal, {
            scale: 1.8, opacity: 0, rotate: -20,
            duration: 0.42, ease: "back.out(2.4)",
        }, "-=0.25");
    }

    // · Section headers rise as they enter ·
    gsap.utils.toArray(".section-head").forEach((el) => {
        gsap.from(el, {
            y: 26, opacity: 0, duration: 0.7,
            scrollTrigger: { trigger: el, start: "top 88%" },
        });
    });

    // · Lead story: text rises, photograph unveiled with a curtain wipe + parallax ·
    const lead = document.querySelector(".lead");
    if (lead) {
        gsap.from(lead.querySelector(".lead-text"), {
            y: 44, opacity: 0, duration: 0.9,
            scrollTrigger: { trigger: lead, start: "top 82%" },
        });
        const fig = lead.querySelector("figure");
        if (fig) {
            gsap.fromTo(fig,
                { clipPath: "inset(0 0 0 100%)" },
                {
                    clipPath: "inset(0 0 0 0%)", duration: 1.15, ease: "power4.inOut",
                    scrollTrigger: { trigger: lead, start: "top 78%" },
                });
            gsap.fromTo(fig.querySelector("img"),
                { yPercent: -6, scale: 1.08 },
                {
                    yPercent: 6, ease: "none",
                    scrollTrigger: { trigger: lead, start: "top bottom", end: "bottom top", scrub: true },
                });
        }
    }

    // · Numbered briefs ·
    gsap.utils.toArray(".brief").forEach((b, i) => {
        gsap.from(b, {
            y: 34, opacity: 0, duration: 0.7, delay: i * 0.12,
            scrollTrigger: { trigger: b, start: "top 88%" },
        });
    });

    // · News columns and archive rows: batched stagger on scroll ·
    if (document.querySelector(".news-item")) {
        ScrollTrigger.batch(".news-item", {
            start: "top 93%",
            onEnter: (els) => gsap.fromTo(els,
                { y: 24, opacity: 0 },
                { y: 0, opacity: 1, stagger: 0.05, duration: 0.55, overwrite: true }),
        });
    }
    if (document.querySelector(".archive-row")) {
        ScrollTrigger.batch(".archive-row", {
            start: "top 94%",
            onEnter: (els) => gsap.fromTo(els,
                { x: -18, opacity: 0 },
                { x: 0, opacity: 1, stagger: 0.06, duration: 0.5, overwrite: true }),
        });
    }
})();
</script>'''


# ───────────────────────── HTML builders ─────────────────────────

def _item_parts(item: dict) -> dict:
    title = _esc(item.get("title", ""))
    summary = item.get("brief") or item.get("summary", "")
    summary = _esc(summary[:120] + ("..." if len(summary) > 120 else ""))
    return {
        "url": item.get("url", ""),
        "title": title,
        "summary": summary,
        "source": _esc(item.get("source_name", "")),
        "cat": _esc(item.get("category", "其他")),
        "cat_color": item.get("category_color", "#93876F"),
        "pub": _esc(item.get("published_at", "")[:10]),
        "image": item.get("image_url", ""),
        "heat": item.get("sources_count", 1),
        "linked": _valid_url(item.get("url", "")),
    }


def _heat_html(p: dict) -> str:
    """Cross-platform attention badge: only shown when 2+ sources covered the story."""
    if p["heat"] > 1:
        return f'<span class="heat">◆ {p["heat"]} 家报道</span>'
    return ""


def _news_item_html(item: dict, idx: int) -> str:
    """One story in the news columns. Renders as <a> only when a real URL exists."""
    p = _item_parts(item)
    sec = section_of_category(item.get("category_id", ""))
    tag, attrs = ("a", f'href="{_esc(p["url"])}" target="_blank" rel="noopener"') if p["linked"] else ("article", "")
    more = '<span class="more">阅读原文 →</span>' if p["linked"] else ""
    return f'''
    <{tag} {attrs} class="news-item" data-section="{sec}">
        <div class="row"><span class="idx">{idx:02d}</span><span class="tag" style="color:{p['cat_color']}">{p['cat']}</span></div>
        <h4>{p['title']}</h4>
        <p>{p['summary']}</p>
        <div class="meta"><span>{p['source']} · {p['pub']}</span>{_heat_html(p)}{more}</div>
    </{tag}>'''


def _lead_html(item: dict) -> str:
    """The front-page lead story (头条), with photograph when the feed provides one."""
    p = _item_parts(item)
    tag, attrs = ("a", f'href="{_esc(p["url"])}" target="_blank" rel="noopener"') if p["linked"] else ("article", "")
    fig = ""
    if p["image"]:
        fig = (f'<figure><img src="{_esc(p["image"])}" alt="{p["title"]}" loading="lazy" '
               f'onerror="this.parentElement.remove()"></figure>')
    return f'''
    <{tag} {attrs} class="lead">
        <div class="lead-text">
            <span class="kicker">头条 · {p['cat']}</span>
            <h3>{p['title']}</h3>
            <p>{p['summary']}</p>
            <div class="byline"><span>{p['source']}</span><span>{p['pub']}</span>{_heat_html(p)}</div>
        </div>
        {fig}
    </{tag}>'''


def _brief_html(item: dict, num: int) -> str:
    """A numbered sub-highlight (贰条 / 叁条), with a thumbnail when available."""
    p = _item_parts(item)
    tag, attrs = ("a", f'href="{_esc(p["url"])}" target="_blank" rel="noopener"') if p["linked"] else ("article", "")
    thumb = ""
    if p["image"]:
        thumb = (f'<img class="thumb" src="{_esc(p["image"])}" alt="{p["title"]}" loading="lazy" '
                 f'onerror="this.remove()">')
    return f'''
    <{tag} {attrs} class="brief">
        <span class="num">{num:02d}</span>
        <div>
            {thumb}
            <span class="kicker">{p['cat']}</span>
            <h4>{p['title']}</h4>
            <p>{p['summary']}</p>
            <div class="byline"><span>{p['source']}</span><span>{p['pub']}</span>{_heat_html(p)}</div>
        </div>
    </{tag}>'''


def _highlights_section(highlights: list[dict]) -> str:
    if not highlights:
        return ""
    lead = _lead_html(highlights[0])
    briefs = '\n'.join(_brief_html(it, i + 2) for i, it in enumerate(highlights[1:3]))
    briefs_html = f'<div class="briefs">{briefs}</div>' if briefs else ""
    return f'''
    <section class="section">
        <div class="section-head">
            <h2 class="section-title"><span class="no">壹</span>今日看点</h2>
            <span class="section-note">Front Page</span>
        </div>
        {lead}
        {briefs_html}
    </section>'''


def _news_section(items: list[dict]) -> str:
    if not items:
        return ""
    counts = {}
    for it in items:
        sec = section_of_category(it.get("category_id", ""))
        counts[sec] = counts.get(sec, 0) + 1
    tabs = [f'<button class="tab active" data-sec="all">全部<span class="n">{len(items)}</span></button>']
    for sec_id, sec_name in SECTIONS:
        tabs.append(f'<button class="tab" data-sec="{sec_id}">{sec_name}<span class="n">{counts.get(sec_id, 0)}</span></button>')
    cards = '\n'.join(_news_item_html(it, i + 1) for i, it in enumerate(items))
    return f'''
    <section class="section">
        <div class="section-head">
            <h2 class="section-title"><span class="no">贰</span>全部资讯</h2>
            <span class="section-note">{len(items)} 条 · All Stories</span>
        </div>
        <div class="tabs" id="news-tabs">
            {''.join(tabs)}
        </div>
        <div class="news-columns" id="news-columns">
            {cards}
        </div>
        <div class="tab-empty" id="news-empty" hidden>本栏目今日暂无资讯</div>
    </section>'''


def _archive_section(history: list[dict]) -> str:
    if not history:
        return ""
    rows = ""
    for b in history:
        rows += f'''
        <a href="./{b['slug']}/" class="archive-row">
            <span class="a-date">{_esc(b['date'][:10])}</span>
            <span class="a-week">{_esc(b['date_cn'].split(' ')[-1])}</span>
            <span class="a-count">{len(b.get('items', []))} 条资讯</span>
            <span class="a-arrow">→</span>
        </a>'''
    return f'''
    <section class="section">
        <div class="section-head">
            <h2 class="section-title"><span class="no">叁</span>往期存档</h2>
            <span class="section-note">{len(history)} 期 · Archive</span>
        </div>
        {rows}
    </section>'''


def _masthead(home_href: str, right_html: str) -> str:
    return f'''
    <header class="masthead">
        <div class="masthead-inner">
            <a href="{home_href}" class="brand">
                <span class="brand-text">
                    <span class="brand-name">AI 早报</span>
                    <span class="brand-sub"><img src="{home_href}icon.jpg" alt="米桶">米桶</span>
                </span>
            </a>
            <span class="masthead-meta">{right_html}</span>
        </div>
    </header>'''


def _frontpage(date_cn: str, issue_no: str) -> str:
    # split the nameplate into per-character spans for the GSAP stagger
    chars = ""
    for c in "AI 早报":
        if c == " ":
            chars += '<span class="ch-gap"></span>'
        else:
            chars += f'<span class="ch-wrap"><span class="ch">{c}</span></span>'
    return f'''
    <section class="frontpage">
        <div class="dateline">
            <span>{date_cn}</span>
            <span class="live">每日更新中</span>
            <span>{issue_no}</span>
        </div>
        <div class="nameplate">
            <div class="seal">米桶</div>
            <h1>{chars}</h1>
            <div class="latin">Mitong AI Daily Briefing</div>
            <div class="motto">每日精选 · 十秒速览</div>
        </div>
        <hr class="double-rule">
    </section>'''


def _page_shell(title: str, body: str, prefix: str = "./") -> str:
    return f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link rel="icon" href="{prefix}icon.jpg" type="image/jpeg">
    <title>{title}</title>
    {CSS}
</head>
<body>
{body}

    <footer class="footer">
        <span class="zh">米桶 AI 早报 · 仅供信息参考，不构成任何建议</span>
        <span>Sources · 机器之心 / 量子位 / 36氪 / BBC / FT / 华尔街见闻</span>
    </footer>

{GSAP_CDN}
{PAGE_JS}
</body>
</html>'''


def _detail_page_html(b: dict) -> str:
    """Archive page for one date, at website/<slug>/index.html."""
    items = b.get("items", [])
    highlights = b.get("highlights") or items[:3]
    body = f'''
    {_masthead("../", '<a href="../">← 返回首页</a>')}
    {_frontpage(b["date_cn"], b["issue_no"])}
    {_highlights_section(highlights)}
    {_news_section(items)}
    {'' if items else '<div class="empty">当日暂无资讯记录</div>'}'''
    return _page_shell(f"{b['date'][:10]} · 米桶 AI 早报", body, prefix="../")


def _home_page_html(latest: dict, history: list[dict]) -> str:
    items = latest.get("items", [])
    highlights = latest.get("highlights") or items[:3]
    body = f'''
    {_masthead("./", latest["date_cn"])}
    {_frontpage(latest["date_cn"], latest["issue_no"])}
    {_highlights_section(highlights)}
    {_news_section(items)}
    {_archive_section(history)}
    {'' if items else '<div class="empty">暂无资讯，敬请期待</div>'}'''
    return _page_shell("米桶 AI 早报", body)


# ───────────────────────── entry point ─────────────────────────

def generate_website():
    briefings = get_all_briefings()
    if not briefings:
        print("No briefings found.")
        return

    WEB_DIR.mkdir(exist_ok=True)

    # Detail (archive) pages
    for b in briefings:
        detail_dir = WEB_DIR / b["slug"]
        detail_dir.mkdir(exist_ok=True)
        (detail_dir / "index.html").write_text(_detail_page_html(b), encoding="utf-8")
        print(f"  Archive page: {detail_dir}/index.html")

    # Home page
    latest = briefings[0]
    (WEB_DIR / "index.html").write_text(
        _home_page_html(latest, briefings[1:]), encoding="utf-8")

    print(f"✅ Website generated: {WEB_DIR}/index.html")
    print(f"   Briefings: {len(briefings)} · Latest: {latest['date']} · Items: {len(latest.get('items', []))}")


if __name__ == "__main__":
    generate_website()
