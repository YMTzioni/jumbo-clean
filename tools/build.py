# -*- coding: utf-8 -*-
"""Builds index.html, one page per service, sitemap.xml and responsive images.
Run:  python tools/build.py        (from the site root)"""
import json, os, re, sys, html
from urllib.parse import quote
from datetime import date
sys.path.insert(0, os.path.dirname(__file__))
from content import *  # noqa

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW = os.path.join(ROOT, "raw")
OUT_IMG = os.path.join(ROOT, "assets", "img")
WIDTHS = (640, 1200, 1800)
TODAY = date.today().isoformat()

# ---------- images ----------
def build_images():
    from PIL import Image
    os.makedirs(OUT_IMG, exist_ok=True)
    for f in sorted(os.listdir(RAW)):
        if not f.endswith(".png"):
            continue
        name = f[:-4]
        im = Image.open(os.path.join(RAW, f)).convert("RGB")
        for w in WIDTHS:
            dst = os.path.join(OUT_IMG, f"{name}-{w}.webp")
            if os.path.exists(dst) and os.path.getmtime(dst) > os.path.getmtime(os.path.join(RAW, f)):
                continue
            h = round(im.height * w / im.width)
            im.resize((w, h), Image.LANCZOS).save(dst, "WEBP", quality=78, method=6)
    og = Image.open(os.path.join(RAW, "home-done.png")).convert("RGB")
    og = og.resize((1200, round(og.height * 1200 / og.width)), Image.LANCZOS)
    top = (og.height - 630) // 2
    og.crop((0, top, 1200, top + 630)).save(os.path.join(ROOT, "assets", "og.jpg"), quality=82)

def img(name, alt, pre, sizes="(max-width: 900px) 100vw, 50vw", cls="", eager=False, w=1800, h=1196):
    srcset = ", ".join(f"{pre}assets/img/{name}-{x}.webp {x}w" for x in WIDTHS)
    load = 'fetchpriority="high"' if eager else 'loading="lazy" decoding="async"'
    c = f' class="{cls}"' if cls else ""
    return f'<img{c} src="{pre}assets/img/{name}-1200.webp" srcset="{srcset}" sizes="{sizes}" width="{w}" height="{h}" alt="{html.escape(alt)}" {load}>'

# ---------- shared pieces ----------
ICONS = """<svg width="0" height="0" style="position:absolute" aria-hidden="true">
<symbol id="i-phone" viewBox="0 0 24 24"><path fill="none" stroke="currentColor" stroke-width="1.9" stroke-linejoin="round" d="M5 3.5h3.5l1.7 4.3-2.2 1.4a11 11 0 0 0 6.8 6.8l1.4-2.2 4.3 1.7V19a1.5 1.5 0 0 1-1.5 1.5A16.5 16.5 0 0 1 3.5 5 1.5 1.5 0 0 1 5 3.5z"/></symbol>
<symbol id="i-wa" viewBox="0 0 24 24"><path fill="currentColor" d="M12 2a10 10 0 0 0-8.6 15.1L2 22l5-1.3A10 10 0 1 0 12 2zm0 18.2a8.2 8.2 0 0 1-4.2-1.15l-.3-.18-3 .78.8-2.9-.2-.3A8.2 8.2 0 1 1 12 20.2zm4.5-6.1c-.25-.12-1.46-.72-1.69-.8-.23-.08-.39-.12-.55.12-.16.25-.63.8-.78.97-.14.16-.29.18-.53.06a6.7 6.7 0 0 1-3.3-2.9c-.25-.43.25-.4.71-1.33.08-.16.04-.3-.02-.42-.06-.12-.55-1.33-.76-1.82-.2-.48-.4-.41-.55-.42h-.47a.9.9 0 0 0-.65.3 2.7 2.7 0 0 0-.85 2.02 4.7 4.7 0 0 0 1 2.5 10.8 10.8 0 0 0 4.13 3.65c1.54.66 2.14.72 2.9.6.47-.07 1.46-.6 1.66-1.17.2-.58.2-1.07.15-1.17-.07-.1-.23-.16-.47-.28z"/></symbol>
<symbol id="i-arrow" viewBox="0 0 24 24"><path fill="none" stroke="currentColor" stroke-width="1.9" stroke-linecap="round" stroke-linejoin="round" d="M19 12H5m5-5l-5 5 5 5"/></symbol>
<symbol id="i-down" viewBox="0 0 24 24"><path fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" d="M6 9l6 6 6-6"/></symbol>
<symbol id="i-check" viewBox="0 0 24 24"><circle cx="12" cy="12" r="10" fill="none" stroke="currentColor" stroke-width="1.6"/><path fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" d="M7.5 12.3l3 3 6-6.3"/></symbol>
<symbol id="i-plus" viewBox="0 0 24 24"><path fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" d="M12 5v14M5 12h14"/></symbol>
<symbol id="i-spark" viewBox="0 0 18 18"><path d="M9 0Q9 9 18 9Q9 9 9 18Q9 9 0 9Q9 9 9 0Z"/></symbol>
<symbol id="i-menu" viewBox="0 0 24 24"><path fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" d="M4 7h16M4 12h16M4 17h10"/></symbol>
<symbol id="i-x" viewBox="0 0 24 24"><path fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" d="M6 6l12 12M18 6L6 18"/></symbol>
<symbol id="i-pin" viewBox="0 0 24 24"><path fill="none" stroke="currentColor" stroke-width="2" stroke-linejoin="round" d="M12 21s-7-6.2-7-11.5a7 7 0 0 1 14 0C19 14.8 12 21 12 21z"/><circle cx="12" cy="9.5" r="2.4" fill="none" stroke="currentColor" stroke-width="2"/></symbol>
<symbol id="i-drag" viewBox="0 0 24 24"><path fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" d="M9 7l-5 5 5 5M15 7l5 5-5 5"/></symbol>
<symbol id="i-roof" viewBox="0 0 40 28"><path d="M3 25 L20 6 L37 25" fill="none" stroke-width="5" style="stroke:var(--roof-1)"/><path d="M11 26 L20 16 L29 26" fill="none" stroke-width="2.6" style="stroke:var(--roof-2)"/></symbol>
</svg>"""

FAVICON = "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 40 40'%3E%3Cpath d='M4 30 L20 12 L36 30' fill='none' stroke='%231b2552' stroke-width='6'/%3E%3Cpath d='M12 31 L20 22 L28 31' fill='none' stroke='%23c9962e' stroke-width='3.5'/%3E%3Cpath d='M33 2 Q33 9 40 9 Q33 9 33 16 Q33 9 26 9 Q33 9 33 2Z' fill='%23c9962e'/%3E%3C/svg%3E"

A11Y_BOOT = "(function(){try{var p=JSON.parse(localStorage.getItem('jc_a11y_v1'));if(!p||p.v!==1)return;var c=document.documentElement.classList;[115,130,150].forEach(function(t){c.toggle('a11y-text-'+t,p.text===t)});[16,20].forEach(function(l){c.toggle('a11y-lines-'+l,p.lines===l)});['high','invert','mono'].forEach(function(k){c.toggle('a11y-contrast-'+k,p.contrast===k)});['links','heads','font','cursor','motion'].forEach(function(k){c.toggle('a11y-'+k,!!p[k])})}catch(e){}})()"

A11Y_PANEL = """<button class="a11y-trigger" id="a11y-trigger" type="button" aria-expanded="false" aria-controls="a11y-panel" aria-keyshortcuts="Alt+A"><svg aria-hidden="true" viewBox="0 0 24 24"><circle cx="12" cy="4.2" r="2.2" fill="currentColor"/><path fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" d="M4.5 8.5l7.5 1.5 7.5-1.5M12 10v5m0 0l-3.5 6.5M12 15l3.5 6.5"/></svg><span class="sr">תפריט נגישות (Alt+A)</span></button>
<div class="a11y-panel" id="a11y-panel" role="dialog" aria-modal="true" aria-labelledby="a11y-title" hidden>
  <div class="a11y-head"><p id="a11y-title">התאמות נגישות</p><button class="icon-btn" type="button" data-a11y-close><svg aria-hidden="true"><use href="#i-x"/></svg><span class="sr">סגירת תפריט נגישות</span></button></div>
  <div class="a11y-grid"></div>
  <div class="a11y-foot"><button class="btn btn-line" type="button" data-a11y-reset>איפוס הגדרות</button><a class="link" href="__PRE__hatzharat-negishut/">הצהרת נגישות</a></div>
</div>
<div class="sr" id="a11y-live" role="status" aria-live="polite"></div>"""

def esc(s):
    return html.escape(s, quote=True)

def head(title, desc, url, pre, preload, ld):
    return f"""<!doctype html>
<html lang="he" dir="rtl">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(title)}</title>
<meta name="description" content="{esc(desc)}">
<meta name="theme-color" content="#141a33">
<link rel="canonical" href="{url}">
<meta property="og:title" content="{esc(title)}">
<meta property="og:description" content="{esc(desc)}">
<meta property="og:image" content="{SITE}/assets/og.jpg">
<meta property="og:url" content="{url}">
<meta property="og:type" content="website">
<meta property="og:site_name" content="ג'מבו קלין Jumbo Clean">
<meta property="og:locale" content="he_IL">
<meta name="twitter:card" content="summary_large_image">
<link rel="icon" href="{FAVICON}">
{"" if not preload else f'''<link rel="preload" as="image" href="{pre}assets/img/{preload}-1200.webp" imagesrcset="{pre}assets/img/{preload}-640.webp 640w, {pre}assets/img/{preload}-1200.webp 1200w, {pre}assets/img/{preload}-1800.webp 1800w" imagesizes="(max-width: 900px) 100vw, 50vw" fetchpriority="high">'''}
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Karantina:wght@400;700&family=Miriam+Libre:wght@400;700&display=swap" rel="stylesheet">
<link rel="stylesheet" href="{pre}site.css">
<script>document.documentElement.classList.add('js');{A11Y_BOOT}</script>
<script type="application/ld+json">{json.dumps(ld, ensure_ascii=False)}</script>
</head>
<body>
<a class="skip" href="#main">דילוג לתוכן הראשי</a>
{ICONS}"""

CUR = ' aria-current="page"'

def nav(pre, current=None):
    def col(group, label):
        items = "".join(
            f'<a href="{pre}{s["slug"]}/"{CUR if s["slug"]==current else ""}><b>{s["name"]}</b><span>{s["menu"]}</span></a>'
            for s in SERVICES if s["group"] == group)
        return f'<div class="mega-col"><p class="menu-h">{label}</p>{items}</div>'
    sheet_links = "".join(f'<a href="{pre}{s["slug"]}/">{s["name"]}</a>' for s in SERVICES)
    home = "./" if pre == "" else pre
    return f"""<header class="nav">
  <div class="nav-bar">
    <a class="mark" href="{home}" aria-label="ג׳מבו קלין, דף הבית"><svg viewBox="0 0 40 28" aria-hidden="true"><use href="#i-roof"/></svg><span class="mark-t"><b>ג׳מבו קלין</b><small>מהשיפוץ ועד הברק</small></span></a>
    <nav class="nav-links" aria-label="ראשי">
      <details><summary>שירותים</summary>
        <div class="mega">{col("reno","שיפוצים")}{col("clean","ניקיון ופוליש")}</div>
      </details>
      <a href="{pre}mesir-avnit/" class="nav-new">מסיר אבנית <span>חדש</span></a>
      <a href="{home}#process">איך עובדים</a>
      <a href="{home}#faq">שאלות</a>
      <a href="#contact">צור קשר</a>
    </nav>
    <button class="icon-btn nav-menu" type="button" data-sheet aria-expanded="false" aria-controls="sheet"><svg aria-hidden="true"><use href="#i-menu"/></svg><span class="sr">תפריט</span></button>
    <a class="btn btn-gold btn-call" href="tel:0528580800" aria-label="התקשרו {PHONE}"><svg aria-hidden="true"><use href="#i-phone"/></svg><span class="num">{PHONE}</span></a>
  </div>
</header>
<div class="sheet" id="sheet" role="dialog" aria-modal="true" aria-label="תפריט" hidden>
  <button class="icon-btn sheet-close" type="button" data-sheet><svg aria-hidden="true"><use href="#i-x"/></svg><span class="sr">סגירה</span></button>
  <p class="menu-h">שירותים</p>{sheet_links}
  <p class="menu-h">מוצרים</p><a href="{pre}mesir-avnit/">מסיר אבנית למקלחונים</a>
  <p class="menu-h">עוד</p><a href="{home}#process">איך עובדים</a><a href="{home}#faq">שאלות</a><a href="#contact">צור קשר</a>
</div>"""

def marquee(pre):
    items = "".join(f'<a href="{pre}{s["slug"]}/">{s["name"]}<svg aria-hidden="true"><use href="#i-spark"/></svg></a>' for s in SERVICES)
    return f"""<div class="marquee" role="region" aria-label="השירותים שלנו">
  <button class="marquee-pause" type="button" aria-pressed="false"><span class="sr">עצירת הפס הנע</span><svg class="i-pause" aria-hidden="true" viewBox="0 0 24 24"><path d="M8 5h3v14H8zM13 5h3v14h-3z" fill="currentColor"/></svg><svg class="i-play" aria-hidden="true" viewBox="0 0 24 24"><path d="M16 5L5 12l11 7z" fill="currentColor"/></svg></button>
  <div class="marquee-track"><div>{items}</div><div aria-hidden="true">{items.replace('<a ', '<a tabindex="-1" ')}</div></div>
</div>"""

def card(s, pre, cls="", sizes="(max-width: 980px) 100vw, 33vw", kicker=None):
    k = kicker or ("שיפוצים" if s["group"] == "reno" else "ניקיון ופוליש")
    return f"""<a class="card {cls}" href="{pre}{s["slug"]}/" data-reveal>
  {img(s["img"], s["name"], pre, sizes)}
  <div class="card-body"><span class="kicker">{k}</span><h3>{s["name"]}</h3><p>{s["card"]}</p><span class="go">לפרטים</span></div>
</a>"""

def ba_block(key, pre, heading, text):
    b, a, lb, la, alt = BA[key]
    return f"""<div class="ba-wrap">
  <div class="ba" data-reveal>
    {img(b, alt + ", לפני", pre, "(max-width: 900px) 100vw, 60vw")}
    {img(a, alt + ", אחרי", pre, "(max-width: 900px) 100vw, 60vw", cls="ba-after")}
    <span class="ba-line" aria-hidden="true"></span>
    <span class="ba-knob" aria-hidden="true"><i></i><i></i><i></i></span>
    <span class="ba-label l">{lb}</span><span class="ba-label r">{la}</span>
    <span class="ba-done" aria-hidden="true">מבריק.</span>
    <input type="range" min="0" max="100" value="50" aria-label="השוואה: {alt}">
  </div>
  <div class="ba-copy">
    <h2 data-split>{heading}</h2>
    <p class="lead" data-words>{text}</p>
  </div>
</div>"""

def steps(items):
    return '<ol class="steps" style="list-style:none;margin:0;padding:0">' + "".join(
        f'<li class="step" data-reveal style="--d:{i}"><span class="n">{i+1}</span><h3>{t}</h3><p>{d}</p></li>' for i, (t, d) in enumerate(items)) + "</ol>"

def faq(items):
    return '<div class="faq">' + "".join(
        f'<details data-reveal><summary>{q}<svg aria-hidden="true"><use href="#i-plus"/></svg></summary><p>{a}</p></details>' for q, a in items) + "</div>"

def contact(pre, service=None):
    opts = "".join(f'<option{" selected" if s["slug"]==service else ""}>{s["name"]}</option>' for s in SERVICES)
    opts += '<option>כמה שירותים / לא בטוח</option>'
    return f"""<section class="section night" id="contact">
  <div class="wrap contact">
    <div>
      <h2 data-split>מה <em>מתכננים</em><br>אצלכם?</h2>
      <p>ספרו לנו בכמה מילים מה צריך, אפשר לצרף תמונות בוואטסאפ, ונחזור אליכם עם הצעה. עובדים בכל הארץ, ללקוחות פרטיים ועסקיים.</p>
      <a class="phone-big num" href="tel:0528580800">{PHONE}</a>
      <div class="cta-row"><a class="btn btn-ghost" href="{WA}" target="_blank" rel="noopener"><svg aria-hidden="true"><use href="#i-wa"/></svg>שליחת תמונות בוואטסאפ</a></div>
    </div>
    <form class="form" id="lead" novalidate>
      <label>שם<input name="name" autocomplete="name"></label>
      <label>טלפון (חובה)<input name="phone" type="tel" inputmode="tel" autocomplete="tel" dir="ltr" required aria-required="true" aria-describedby="phone-err" placeholder="05X-XXXXXXX"><span class="err" id="phone-err" role="alert"></span></label>
      <label>שירות<select name="service">{opts}</select></label>
      <label>עיר<input name="city" autocomplete="address-level2"></label>
      <label class="full">מה צריך?<textarea name="msg" placeholder="לדוגמה: דירת 4 חדרים, שיפוץ אמבטיה וניקיון לפני כניסה"></textarea></label>
      <button class="btn btn-ink" type="submit" data-magnet>שליחה בוואטסאפ</button>
      <p class="note">הטופס פותח וואטסאפ עם הפרטים שמילאתם, והם נשלחים אלינו רק כשתלחצו שליחה בוואטסאפ. האתר עצמו לא שומר אותם. <a class="link" href="{pre}privacy/">מדיניות פרטיות</a></p>
    </form>
  </div>
</section>"""

def footer(pre):
    col = lambda g: "".join(f'<li><a href="{pre}{s["slug"]}/">{s["name"]}</a></li>' for s in SERVICES if s["group"] == g)
    return f"""<footer class="night foot">
  <div class="wrap">
    <p class="statement">צוות <em>אחד</em> לכל הנכס.</p>
    <div class="foot-grid">
      <div><a class="mark" href="{pre or './'}"><svg viewBox="0 0 40 28" aria-hidden="true"><use href="#i-roof"/></svg><span class="mark-t"><b>ג׳מבו קלין</b><small>מהשיפוץ ועד הברק</small></span></a>
        <ul style="margin-top:1rem"><li><a class="num" href="tel:0528580800">{PHONE}</a></li><li><a href="{WA}" target="_blank" rel="noopener">וואטסאפ</a></li><li><a href="{pre}#regions">עובדים בכל הארץ</a></li><li><a href="{pre}hatzharat-negishut/">הצהרת נגישות</a></li><li><a href="{pre}privacy/">מדיניות פרטיות</a></li></ul></div>
      <div><p class="menu-h">שיפוצים</p><ul>{col("reno")}</ul></div>
      <div><p class="menu-h">ניקיון ופוליש</p><ul>{col("clean")}</ul><p class="menu-h" style="margin-top:1.25rem">מוצרים</p><ul><li><a href="{pre}mesir-avnit/">מסיר אבנית למקלחונים</a></li></ul></div>
    </div>
    <small>© {date.today().year} ג׳מבו קלין (ג'מבו קלין, גמבו קלין, Jumbo Clean). שיפוצים, ניקיון ופוליש בכל הארץ. התמונות באתר להמחשה</small>
  </div>
</footer>
<nav class="dock" aria-label="יצירת קשר מהירה">
  <a class="btn btn-gold" href="tel:0528580800"><svg aria-hidden="true"><use href="#i-phone"/></svg>התקשרו</a>
  <a class="btn btn-ghost" href="{WA}" target="_blank" rel="noopener"><svg aria-hidden="true"><use href="#i-wa"/></svg>וואטסאפ</a>
</nav>
{A11Y_PANEL.replace("__PRE__", pre)}
<script src="{pre}site.js" defer></script>
<script src="{pre}a11y.js" defer></script>
</body>
</html>
"""

def regions_band():
    lis = "".join(f'<li>{r}</li>' for r in REGIONS)
    return f"""<section class="section night" id="regions">
  <div class="wrap region-band">
    <div><h2 data-split>עובדים <em>בכל</em><br>הארץ.</h2>
      <p>מהצפון ועד הדרום. ספרו לנו איפה הנכס ונתאם צוות, סיור ותאריך.</p></div>
    <ul class="regions" data-reveal>{lis}</ul>
  </div>
</section>"""

BUSINESS = {
  "@type": "HomeAndConstructionBusiness", "@id": f"{SITE}/#business", "name": "ג׳מבו קלין", "alternateName": ["Jumbo Clean", "ג'מבו קלין", "גמבו קלין", "ג'מבו קלין שיפוצים", "ג׳מבו קלין שיפוצים"],
  "url": f"{SITE}/", "telephone": PHONE_INTL, "image": f"{SITE}/assets/og.jpg", "logo": f"{SITE}/assets/logo-480.webp",
  "description": "שיפוצים לדירות ולמשרדים: צבע, בנייה וטיח ואינסטלציה, וגם ניקיון לפני אכלוס, פוליש קריסטל, פוליש לגרניט פורצלן וחידוש רצפות. בכל הארץ.",
  "areaServed": {"@type": "Country", "name": "ישראל"}, "knowsLanguage": "he",
}

def faq_ld(items):
    return {"@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in items]}

# ---------- home ----------
def home():
    pre = ""
    reno = [s for s in SERVICES if s["group"] == "reno"]
    clean = [s for s in SERVICES if s["group"] == "clean"]
    bento = (card(reno[0], pre, "b-xl", "(max-width: 980px) 100vw, 66vw") + card(reno[1], pre, "b-l") +
             card(reno[2], pre, "b-w", "(max-width: 980px) 100vw, 50vw") + card(reno[3], pre, "b-w", "(max-width: 980px) 100vw, 50vw"))
    bento2 = (card(clean[0], pre, "b-l") + card(clean[1], pre, "b-xl", "(max-width: 980px) 100vw, 66vw") +
              card(clean[2], pre, "b-m") + card(clean[3], pre, "b-m") + card(clean[4], pre, "b-m"))
    ld = {"@context": "https://schema.org", "@graph": [BUSINESS, faq_ld(HOME_FAQ),
          {"@type": "ItemList", "name": "השירותים של ג׳מבו קלין", "itemListElement": [
              {"@type": "ListItem", "position": i + 1, "url": f"{SITE}/{s['slug']}/", "name": s["name"]} for i, s in enumerate(SERVICES)]}]}
    house = f"""<figure class="house" data-reveal>
  <svg class="frame" viewBox="0 0 520 600" role="img" aria-label="דירה משופצת ומבריקה, מוכנה למסירה">
    <defs>
      <clipPath id="hc"><path d="M40 250 L260 70 L480 250 L480 580 Q480 590 470 590 L50 590 Q40 590 40 580Z"/></clipPath>
      <linearGradient id="sg" x1="0" x2="1"><stop offset="0" stop-color="white" stop-opacity="0"/><stop offset=".5" stop-color="white" stop-opacity=".55"/><stop offset="1" stop-color="white" stop-opacity="0"/></linearGradient>
    </defs>
    <g clip-path="url(#hc)">
      <image href="assets/img/home-done-1200.webp" x="-120" y="70" width="780" height="520" preserveAspectRatio="xMidYMid slice"/>
      <rect class="sheen-bar" x="0" y="380" width="160" height="230" fill="url(#sg)" style="mix-blend-mode:soft-light"/>
    </g>
    <path class="roof-1" d="M14 262 L260 52 L506 262" fill="none" stroke-width="22" stroke-linejoin="miter"/>
    <path class="roof-2" d="M120 300 L260 182 L400 300" fill="none" stroke-width="9"/>
    <path class="spark" d="M462 70 Q462 104 496 104 Q462 104 462 138 Q462 104 428 104 Q462 104 462 70Z"/>
    <path class="spark" style="animation-delay:-1.4s" d="M410 30 Q410 44 424 44 Q410 44 410 58 Q410 44 396 44 Q410 44 410 30Z"/>
  </svg>
</figure>"""
    body = f"""{head("ג'מבו קלין Jumbo Clean | שיפוצים, ניקיון לפני אכלוס ופוליש בכל הארץ",
                "ג'מבו קלין (גמבו קלין, Jumbo Clean): שיפוצים לדירות ולמשרדים: צבע, בנייה, טיח ואינסטלציה. ואחרי השיפוץ, ניקיון לפני אכלוס, פוליש קריסטל, פוליש לפורצלן וחידוש רצפות. בכל הארץ. 052-858-0800",
                f"{SITE}/", pre, "home-done", ld)}
{nav(pre)}
<main id="main" tabindex="-1">
<section class="hero night">
  <div class="grainient" aria-hidden="true"></div>
  <div class="wrap hero-grid">
    <div>
      <span class="tag"><svg aria-hidden="true"><use href="#i-pin"/></svg>שיפוצים, ניקיון ופוליש בכל הארץ</span>
      <h1 data-split>משפצים,<br>מנקים,<br><em>מוסרים</em> מוכן.</h1>
      <p class="lead" data-words>צוות אחד לכל הנכס: בנייה, טיח, אינסטלציה וצבע, ואחר כך ניקיון לפני אכלוס, פוליש וחידוש רצפות. לדירות, לבתים ולמשרדים.</p>
      <div class="cta-row">
        <a class="btn btn-gold" href="tel:0528580800" data-magnet><svg aria-hidden="true"><use href="#i-phone"/></svg><span class="num">{PHONE}</span></a>
        <a class="btn btn-ghost" href="#contact"><svg aria-hidden="true"><use href="#i-wa"/></svg>הצעת מחיר בוואטסאפ</a>
      </div>
    </div>
    {house}
  </div>
</section>
{marquee(pre)}
<section class="section paper" id="services">
  <div class="wrap">
    <div class="head"><h2 data-split>קודם <em>משפצים</em>.</h2><p class="lead" data-words>שיפוץ מלא או חלקי, לדירה או למשרד. מנהלים את כל בעלי המקצוע בעצמנו, ואתם מדברים עם כתובת אחת.</p></div>
    <div class="bento">{bento}</div>
    <div class="head" style="margin-top:clamp(4rem,8vw,6rem)"><h2 data-split>ואז <em>מבריקים</em>.</h2><p class="lead" data-words>ניקיון לפני אכלוס, פוליש לשיש ולפורצלן, חידוש רצפות ישנות וניקיון יסודי לבתים ולמשרדים.</p></div>
    <div class="bento">{bento2}</div>
  </div>
</section>
<section class="section alt paper">
  <div class="wrap">{ba_block("reno", pre, "גררו. <em>תראו</em><br>את ההבדל.", "אותו חדר, לפני ואחרי: קירות, ריצוף, חלון וניקיון סופי. משכו את הידית שמאלה עד הסוף.")}</div>
</section>
{product_teaser(pre)}
<section class="section paper" id="process">
  <div class="wrap">
    <div class="head"><h2 data-split>מהשיחה ועד<br><em>המפתח</em>.</h2><p class="lead" data-words>ארבעה שלבים פשוטים. בכל שלב אתם יודעים מה קורה, מי בשטח ומתי מסיימים.</p></div>
    {steps([("שיחה ותמונות", "מתקשרים או שולחים תמונות בוואטסאפ ומספרים מה צריך."), ("סיור והצעה", "מגיעים לנכס, מודדים ונותנים הצעה מפורטת ולוח זמנים."), ("עבודה", "צוות קבוע בשטח: שיפוץ, ואחריו ניקיון ופוליש."), ("מסירה", "עוברים יחד על כל חדר ומוסרים נכס מוכן לכניסה.")])}
  </div>
</section>
{regions_band()}
<section class="section paper" id="faq">
  <div class="wrap">
    <div class="head"><h2 data-split>שאלות <em>ששואלים</em><br>אותנו.</h2><p>לא מצאתם תשובה? <a class="link" href="tel:0528580800">התקשרו</a> או <a class="link" href="{WA}" target="_blank" rel="noopener">כתבו בוואטסאפ</a>.</p></div>
    {faq(HOME_FAQ)}
  </div>
</section>
{contact(pre)}
</main>
{footer(pre)}"""
    write("index.html", body)

# ---------- service page ----------
def service(s):
    pre = "../"
    url = f"{SITE}/{s['slug']}/"
    ld = {"@context": "https://schema.org", "@graph": [
        {"@type": "Service", "name": s["name"], "serviceType": s["name"], "description": s["desc"], "url": url,
         "provider": {"@id": f"{SITE}/#business"}, "areaServed": {"@type": "Country", "name": "ישראל"}, "image": f"{SITE}/assets/img/{s['img']}-1200.webp"},
        {**BUSINESS},
        faq_ld(s["faq"]),
        {"@type": "BreadcrumbList", "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "ראשי", "item": f"{SITE}/"},
            {"@type": "ListItem", "position": 2, "name": s["name"], "item": url}]}]}
    checks = "".join(f'<li data-reveal style="--d:{i%2}"><svg aria-hidden="true"><use href="#i-check"/></svg>{x}</li>' for i, x in enumerate(s["includes"]))
    fit = "".join(f'<li><svg aria-hidden="true"><use href="#i-spark"/></svg>{x}</li>' for x in s["fit"])
    group = "שיפוצים" if s["group"] == "reno" else "ניקיון ופוליש"
    extra = ""
    if s.get("ba"):
        heads = {"reno": ("גררו. <em>תראו</em><br>את ההבדל.", "אותו חדר לפני השיפוץ ואחריו. משכו את הידית שמאלה עד הסוף."),
                 "crystal": ("לפני. <em>אחרי</em>.", "אותה רצפת שיש לפני פוליש קריסטל ואחריו. משכו את הידית שמאלה עד הסוף ותראו איך הרצפה מתחילה להחזיר את החלון."),
                 "porcelain": ("עמום. <em>מבריק</em>.", "אותה רצפת פורצלן לפני ניקוי עומק ופוליש ואחריו. משכו את הידית שמאלה עד הסוף.")}
        h, t = heads[s["ba"]]
        extra = f'<section class="section alt paper"><div class="wrap">{ba_block(s["ba"], pre, h, t)}</div></section>'
    elif s.get("img2"):
        extra = f"""<section class="section alt paper"><div class="wrap ba-wrap">
  <div class="s-photo" data-reveal style="aspect-ratio:3/2">{img(s["img2"], "ניקיון משרדים בערב", pre, "(max-width: 900px) 100vw, 60vw")}</div>
  <div class="ba-copy"><h2 data-split>גם <em>למשרדים</em>.</h2><p class="lead" data-words>מנקים משרדים, קליניקות וחנויות אחרי שעות העבודה, חד פעמי או בתדירות קבועה, כדי שבבוקר יחכה לכם מקום נקי.</p></div>
</div></section>"""
    else:
        extra = f"""<section class="section alt paper"><div class="wrap ba-wrap">
  <div class="s-photo" data-reveal style="aspect-ratio:3/2">{img(s["img"], s["name"] + ", בתהליך", pre, "(max-width: 900px) 100vw, 60vw")}</div>
  <div class="ba-copy"><h2 data-split>רואים את <em>ההבדל</em><br>כבר תוך כדי.</h2><p class="lead" data-words>{s["card"]} כל עבודה מתחילה בבדיקה בשטח, כדי שתדעו מראש מה עושים ולמה.</p></div>
</div></section>"""
    rel = "".join(card(BY_SLUG[r], pre) for r in s["related"])
    body = f"""{head(s["title"], s["desc"], url, pre, s["img"], ld)}
{nav(pre, s["slug"])}
<main id="main" tabindex="-1">
<section class="s-hero night">
  <div class="grainient" aria-hidden="true"></div>
  <div class="wrap s-hero-grid">
    <div>
      <nav class="crumbs" aria-label="פירורי לחם"><a href="../">ראשי</a><span aria-hidden="true">/</span><span>{group}</span><span aria-hidden="true">/</span><span aria-current="page">{s["name"]}</span></nav>
      <span class="tag" style="margin-top:1rem"><svg aria-hidden="true"><use href="#i-pin"/></svg>{s["name"]} בכל הארץ</span>
      <h1 data-split>{s["h1"]}</h1>
      <p class="lead" data-words>{s["lead"]}</p>
      <div class="cta-row">
        <a class="btn btn-gold" href="tel:0528580800" data-magnet><svg aria-hidden="true"><use href="#i-phone"/></svg><span class="num">{PHONE}</span></a>
        <a class="btn btn-ghost" href="#contact"><svg aria-hidden="true"><use href="#i-wa"/></svg>הצעת מחיר</a>
      </div>
    </div>
    <div class="s-photo">{img(s["img"], s["name"], pre, eager=True)}</div>
  </div>
</section>
{marquee(pre)}
<section class="section paper">
  <div class="wrap">
    <div class="head"><h2 data-split>מה <em>כולל</em><br>השירות.</h2><p class="lead" data-words>זו רשימת הבסיס. בסיור בנכס נתאים אותה בדיוק למה שאתם צריכים.</p></div>
    <div class="incl">
      <ul class="checks">{checks}</ul>
      <div class="side-card" data-reveal><h3>מתאים במיוחד ל־</h3><ul>{fit}</ul>
        <p>לקוחות פרטיים ועסקיים, בכל הארץ.</p>
        <div class="cta-row"><a class="btn btn-gold" href="#contact" data-magnet>לקבלת הצעה</a></div></div>
    </div>
  </div>
</section>
{extra}
<section class="section paper">
  <div class="wrap">
    <div class="head"><h2 data-split>איך זה <em>עובד</em>.</h2><p class="lead" data-words>ארבעה שלבים, בלי הפתעות. בכל שלב אתם יודעים מה קורה.</p></div>
    {steps(s["steps"])}
  </div>
</section>
{regions_band()}
<section class="section paper" id="faq">
  <div class="wrap">
    <div class="head"><h2 data-split>שאלות על<br><em>{s["name"]}</em>.</h2><p>עוד שאלה? <a class="link" href="tel:0528580800">התקשרו</a> או <a class="link" href="{WA}" target="_blank" rel="noopener">כתבו בוואטסאפ</a>.</p></div>
    {faq(s["faq"])}
  </div>
</section>
<section class="section alt paper">
  <div class="wrap">
    <div class="head"><h2 data-split>שירותים <em>שהולכים</em><br>יחד.</h2><p>הרבה לקוחות משלבים כמה שירותים בהצעה אחת וחוסכים תיאומים.</p></div>
    <div class="related">{rel}</div>
  </div>
</section>
{contact(pre, s["slug"])}
</main>
{footer(pre)}"""
    write(f"{s['slug']}/index.html", body)

NEWWIN = '<span class="sr"> (נפתח בחלון חדש)</span>'

def write(rel, text):
    if rel.endswith(".html"):
        text = re.sub(r'(<a [^>]*target="_blank"[^>]*>)(.*?)</a>', lambda m: m.group(1) + m.group(2) + NEWWIN + "</a>", text, flags=re.S)
    p = os.path.join(ROOT, rel)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, "w", encoding="utf-8", newline="\n") as f:
        f.write(text)

def sitemap():
    urls = [f"{SITE}/"] + [f"{SITE}/{s['slug']}/" for s in SERVICES] + [f"{SITE}/mesir-avnit/", f"{SITE}/hatzharat-negishut/", f"{SITE}/privacy/"]
    xml = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + "".join(
        f"  <url><loc>{u}</loc><lastmod>{TODAY}</lastmod></url>\n" for u in urls) + "</urlset>\n"
    write("sitemap.xml", xml)
    write("robots.txt", f"User-agent: *\nAllow: /\n\nSitemap: {SITE}/sitemap.xml\n")

AUDIT_DATE = "16.11.2026"

def legal_page(slug, title, desc, h1, body_html):
    pre = "../"
    url = f"{SITE}/{slug}/"
    ld = {"@context": "https://schema.org", "@type": "WebPage", "name": title, "url": url, "inLanguage": "he"}
    page = f"""{head(title, desc, url, pre, None, ld)}
{nav(pre)}
<main id="main" tabindex="-1">
<section class="s-hero night legal-hero">
  <div class="wrap">
    <nav class="crumbs" aria-label="פירורי לחם"><a href="../">ראשי</a><span aria-hidden="true">/</span><span aria-current="page">{h1}</span></nav>
    <h1>{h1}</h1>
  </div>
</section>
<section class="section paper">
  <div class="wrap legal">{body_html}</div>
</section>
</main>
{footer(pre)}"""
    write(f"{slug}/index.html", page)

P_PRICE = "19.90"

P_FEATURES = [
    ("מסיר אבנית קשה ומהר", "מפרק שכבות אבנית ושאריות סבון על הזכוכית, הברזים והאריחים."),
    ("ברק בלי סימנים", "הזכוכית נשארת שקופה ומבריקה, בלי פסים ובלי כתמי מים."),
    ("מגן לאורך זמן", "שומר על המקלחון במראה חדש לאורך זמן."),
    ("לכל סוגי המקלחונים", "חומר מקצועי שמתאים לכל סוגי המקלחונים."),
]
P_FAQ = [
    ("כמה זה עולה?", f"המחיר המומלץ לצרכן הוא {P_PRICE} ₪ כולל מע״מ."),
    ("איך מזמינים?", "שלחו לנו הודעה בוואטסאפ או התקשרו, ונגיד לכם איך להשיג את המוצר."),
    ("איך משתמשים?", "מרססים על המשטח, ממתינים מעט ומנגבים במטלית לחה. לפני השימוש קראו את הוראות השימוש והאזהרות שעל התווית."),
    ("מי עומד מאחורי המוצר?", "ג׳מבו קלין, החברה שמנקה דירות לפני אכלוס ומבצעת פוליש לרצפות. רצינו שגם בבית יהיה לכם חומר ברמה מקצועית."),
]

def product_teaser(pre):
    return f"""<section class="section night prod-teaser">
  <div class="wrap prod-split">
    <div class="prod-shot" data-reveal>{img("product-studio", "בקבוק ג׳מבו קלין מסיר אבנית עוצמתי למקלחונים", pre, "(max-width: 900px) 100vw, 45vw", w=1800, h=1800)}</div>
    <div>
      <span class="tag tag-new">חדש מג׳מבו קלין</span>
      <h2 data-split>מסיר אבנית<br><em>עוצמתי</em> למקלחונים.</h2>
      <p class="lead" data-words>החומר המקצועי של ג׳מבו קלין, עכשיו גם לבית. מסיר אבנית קשה, משאיר ברק בלי סימנים ומתאים לכל סוגי המקלחונים.</p>
      <div class="cta-row"><a class="btn btn-gold" href="{pre}mesir-avnit/" data-magnet>להכיר את המוצר</a></div>
    </div>
  </div>
</section>"""

def product():
    pre = "../"
    url = f"{SITE}/mesir-avnit/"
    name = "ג׳מבו קלין מסיר אבנית עוצמתי למקלחונים"
    desc = "מסיר אבנית עוצמתי למקלחונים מבית ג׳מבו קלין: חומר מקצועי שמסיר אבנית קשה, משאיר ברק בלי סימנים ומתאים לכל סוגי המקלחונים. להזמנה: 052-858-0800"
    wa_order = WA + "?text=" + quote("שלום ג׳מבו קלין, אשמח לפרטים על מסיר האבנית למקלחונים")
    ld = {"@context": "https://schema.org", "@graph": [
        {"@type": "Product", "name": name, "description": desc, "url": url,
         "brand": {"@type": "Brand", "name": "ג׳מבו קלין"},
         "image": [f"{SITE}/assets/img/product-studio-1200.webp", f"{SITE}/assets/img/product-spray-1200.webp", f"{SITE}/assets/img/product-bath-1200.webp"],
         "category": "חומרי ניקוי",
         "offers": {"@type": "Offer", "price": P_PRICE, "priceCurrency": "ILS", "url": url, "seller": {"@id": f"{SITE}/#business"}}},
        faq_ld(P_FAQ),
        {"@type": "BreadcrumbList", "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "ראשי", "item": f"{SITE}/"},
            {"@type": "ListItem", "position": 2, "name": "מסיר אבנית למקלחונים", "item": url}]}]}
    icons = {
        0: '<path d="M12 3l7 3v5c0 4.6-3 8.3-7 10-4-1.7-7-5.4-7-10V6z" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linejoin="round"/><path d="M9 12.5l2 2 4-4.5" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/>',
        1: '<path d="M7 4h10l4 5-9 11L3 9z M3 9h18 M9.5 4L8 9l4 11 4-11-1.5-5" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linejoin="round"/>',
        2: '<path d="M3 8c2-1.6 4-1.6 6 0s4 1.6 6 0 4-1.6 6 0 M3 13c2-1.6 4-1.6 6 0s4 1.6 6 0 4-1.6 6 0 M3 18c2-1.6 4-1.6 6 0s4 1.6 6 0 4-1.6 6 0" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"/>',
        3: '<path d="M6 21V8a4 4 0 0 1 8 0 M10 8h8a1 1 0 0 1 0 2h-8z" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/><path d="M12 13v1.5M15 13v2M18 13v1.5M13.5 17v1.5M16.5 17v1.5" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"/>',
    }
    feats = "".join(
        f'<li class="pf" data-reveal style="--d:{i}"><span class="pf-ico"><svg viewBox="0 0 24 24" aria-hidden="true">{icons[i]}</svg></span><h3>{t}</h3><p>{d}</p></li>'
        for i, (t, d) in enumerate(P_FEATURES))
    order_btn = f'<a class="btn btn-volt" href="{wa_order}" target="_blank" rel="noopener" data-magnet><svg aria-hidden="true"><use href="#i-wa"/></svg>להזמנה בוואטסאפ</a>'
    phone_btn = f'<a class="btn btn-ghost" href="tel:0528580800"><svg aria-hidden="true"><use href="#i-phone"/></svg><span class="num">{PHONE}</span></a>'
    bubbles = '<div class="bubbles" aria-hidden="true">' + "".join(f'<i style="--x:{x}%;--s:{s}px;--t:{t}s;--d:{d}s"></i>' for x, s, t, d in [(8,14,11,0),(18,8,9,3),(27,20,14,1),(41,10,10,5),(55,16,13,2),(66,7,8,6),(74,22,15,4),(86,12,11,1),(93,9,9,7)]) + '</div>'
    sparks = '<svg class="p-spark s1" viewBox="0 0 18 18" aria-hidden="true"><use href="#i-spark"/></svg><svg class="p-spark s2" viewBox="0 0 18 18" aria-hidden="true"><use href="#i-spark"/></svg><svg class="p-spark s3" viewBox="0 0 18 18" aria-hidden="true"><use href="#i-spark"/></svg>'
    body = f"""{head("מסיר אבנית עוצמתי למקלחונים | ג'מבו קלין Jumbo Clean", desc, url, pre, "product-studio", ld)}
{nav(pre)}
<main id="main" tabindex="-1" class="pp">
<section class="pp-hero">
  {bubbles}
  <div class="wrap pp-hero-grid">
    <div class="pp-copy">
      <nav class="crumbs" aria-label="פירורי לחם"><a href="../">ראשי</a><span aria-hidden="true">/</span><span>מוצרים</span><span aria-hidden="true">/</span><span aria-current="page">מסיר אבנית</span></nav>
      <img class="pp-logo" src="../assets/product-logo-720.webp" srcset="../assets/product-logo-360.webp 360w, ../assets/product-logo-720.webp 720w" sizes="260px" width="720" height="478" alt="ג׳מבו קלין">
      <p class="pp-new"><span>חדש</span></p>
      <h1 data-split>מסיר אבנית<br><em>עוצמתי</em><br>למקלחונים</h1>
      <p class="lead" data-words>חומר ניקוי מקצועי מבית ג׳מבו קלין. מסיר אבנית קשה מהזכוכית, מהברזים ומהאריחים, ומשאיר את המקלחון מבריק בלי סימנים.</p>
      <div class="cta-row">{order_btn}{phone_btn}</div>
      <p class="pp-price"><span class="pp-price-tag"><small>מחיר מומלץ לצרכן</small><b><span class="num">{P_PRICE}</span> ₪</b></span><span class="pp-price-note">כולל מע״מ</span></p>
      <p class="pp-grade">חומר מקצועי <span dir="ltr" lang="en">PROFESSIONAL GRADE</span></p>
    </div>
    <div class="pp-bottle">
      <div class="pp-glow" aria-hidden="true"></div>
      {img("product-studio", name, pre, "(max-width: 900px) 100vw, 50vw", eager=True, w=1800, h=1800)}
      {sparks}
    </div>
  </div>
</section>
<div class="pp-strip" aria-hidden="true"><span>ניקיון עוצמתי</span><svg viewBox="0 0 18 18"><use href="#i-spark"/></svg><span>תוצאות מיידיות</span><svg viewBox="0 0 18 18"><use href="#i-spark"/></svg><span>ברק בלי סימנים</span><svg viewBox="0 0 18 18"><use href="#i-spark"/></svg><span>לכל סוגי המקלחונים</span></div>
<section class="section pp-sec">
  <div class="wrap">
    <div class="pp-head"><h2 data-split>מה הוא <em>עושה</em>.</h2><p class="lead" data-words>הניסיון שלנו בניקיון דירות לפני אכלוס, בבקבוק אחד לבית.</p></div>
    <ul class="pp-feats">{feats}</ul>
  </div>
</section>
<section class="section pp-sec pp-use">
  <div class="wrap pp-use-grid">
    <figure class="pp-photo pp-tall" data-reveal>{img("product-spray", "ריסוס מסיר האבנית על זכוכית של מקלחון", pre, "(max-width: 900px) 100vw, 50vw", w=1800, h=2250)}</figure>
    <div>
      <h2 data-split>מרססים.<br>מנגבים.<br><em>מבריק.</em></h2>
      <ol class="pp-steps">
        <li data-reveal style="--d:0"><b>1</b><span>מרססים על הזכוכית, הברזים או האריחים.</span></li>
        <li data-reveal style="--d:1"><b>2</b><span>ממתינים מעט, שהחומר יפרק את האבנית.</span></li>
        <li data-reveal style="--d:2"><b>3</b><span>מנגבים במטלית לחה ושוטפים במים.</span></li>
      </ol>
      <p class="pp-note">לפני השימוש קראו את הוראות השימוש והאזהרות שעל התווית.</p>
    </div>
  </div>
</section>
<section class="pp-home">
  <figure class="pp-home-img">{img("product-bath", "בקבוק מסיר האבנית על דופן אמבטיה ליד מקלחון זכוכית", pre, "100vw", w=1800, h=2250)}</figure>
  <div class="wrap pp-home-copy">
    <div class="pp-seal" aria-hidden="true"><span>מתאים<br>לכל סוגי<br>המקלחונים</span></div>
    <h2 data-split>מקצועי.<br>אבל <em>לבית</em>.</h2>
    <p class="lead" data-words>אותה רמת ניקיון שהצוות שלנו מביא לדירות לפני אכלוס, במקלחון שלכם כל שבוע.</p>
  </div>
</section>
<section class="section pp-sec" id="faq">
  <div class="wrap">
    <div class="pp-head"><h2 data-split>שאלות על <em>המוצר</em>.</h2><p>עוד שאלה? <a class="link" href="tel:0528580800">התקשרו</a> או <a class="link" href="{wa_order}" target="_blank" rel="noopener">כתבו בוואטסאפ</a>.</p></div>
    {faq(P_FAQ)}
  </div>
</section>
<section class="pp-cta">
  {bubbles}
  <div class="wrap pp-cta-in">
    <img src="../assets/product-logo-360.webp" width="360" height="239" alt="" class="pp-cta-logo" loading="lazy">
    <h2 data-split>מקלחון <em>מבריק</em>.<br>בלי מאמץ.</h2>
    <p class="pp-price pp-price-c"><span class="pp-price-tag"><small>מחיר מומלץ לצרכן</small><b><span class="num">{P_PRICE}</span> ₪</b></span><span class="pp-price-note">כולל מע״מ</span></p>
    <div class="cta-row">{order_btn}{phone_btn}</div>
    <p>צריכים ניקיון מקצועי לכל הבית? <a class="link" href="../nikayon-klali/">לשירותי הניקיון שלנו</a></p>
  </div>
</section>
</main>
{footer(pre)}"""
    body = body.replace("<body>", '<body class="prod-page">', 1)
    body = body.replace("family=Karantina:wght@400;700&", "family=Karantina:wght@400;700&family=Rubik:wght@800;900&", 1)
    body = body.replace('<link rel="stylesheet" href="../site.css">', '<link rel="stylesheet" href="../site.css"><link rel="stylesheet" href="../product.css">', 1)
    write("mesir-avnit/index.html", body)

def legal():
    wa = f'<a class="link" href="{WA}" target="_blank" rel="noopener">וואטסאפ</a>'
    tel = f'<a class="link num" href="tel:0528580800">{PHONE}</a>'
    a11y = f"""
<p>ג׳מבו קלין רואה חשיבות רבה במתן שירות שוויוני לכל הלקוחות, ובכללם אנשים עם מוגבלות. השקענו בהנגשת האתר כדי שכל אחד יוכל לגלוש בו, לקרוא על השירותים וליצור איתנו קשר בנוחות.</p>
<h2>רמת הנגישות</h2>
<p>האתר הותאם להוראות תקנות שוויון זכויות לאנשים עם מוגבלות (התאמות נגישות לשירות), התשע״ג 2013, ולתקן הישראלי ת״י 5568 המבוסס על הנחיות WCAG 2.0, ברמה AA. האתר נבדק בדפדפנים Chrome, Edge, Firefox ו־Safari, במחשב ובטלפון נייד.</p>
<h2>מה עשינו באתר</h2>
<ul class="legal-list">
<li>ניווט מלא באמצעות המקלדת: Tab למעבר בין רכיבים, Enter להפעלה, Esc לסגירת תפריטים.</li>
<li>קישור "דילוג לתוכן הראשי" בתחילת כל עמוד.</li>
<li>מבנה כותרות היררכי וסימון אזורים (כותרת, ניווט, תוכן ראשי, תחתית) לקוראי מסך.</li>
<li>טקסט חלופי לכל התמונות שמעבירות מידע.</li>
<li>ניגודיות צבעים של 4.5:1 לפחות בין טקסט לרקע.</li>
<li>שדות הטופס מקושרים לתוויות, ושדה חובה מסומן. הודעת שגיאה מוקראת בעברית.</li>
<li>הפס הנע עם שמות השירותים ניתן לעצירה בכפתור, ונעצר גם במעבר עכבר.</li>
<li>האתר מכבד את הגדרת "הפחתת תנועה" במערכת ההפעלה.</li>
<li>קישורים שנפתחים בחלון חדש מסומנים לקוראי מסך.</li>
<li>האתר מותאם לתצוגה בטלפון נייד ולהגדלת תצוגה עד 200% בלי לאבד תוכן.</li>
</ul>
<h2>תפריט הנגישות</h2>
<p>בכל עמוד יש כפתור נגישות בפינת המסך, שאפשר לפתוח גם בקיצור Alt+A. בתפריט אפשר להגדיל טקסט, להגדיל ריווח שורות, לשנות ניגודיות (גבוהה, צבעים הפוכים, שחור לבן), להדגיש קישורים וכותרות, לעבור לגופן קריא, להגדיל את הסמן ולעצור אנימציות. ההגדרות נשמרות בדפדפן שלכם בלבד.</p>
<p>התפריט הוא כלי נוחות בלבד. הוא לא משנה את תוכן האתר, והנגישות נבנתה בקוד האתר עצמו.</p>
<h2>מגבלות נגישות ידועות</h2>
<ul class="legal-list">
<li>שליחת הטופס פותחת את אפליקציית וואטסאפ, שהנגישות שלה באחריות החברה המפעילה אותה. אפשר תמיד ליצור קשר גם בטלפון.</li>
<li>התמונות באתר הן תמונות המחשה ולא צילומים מעבודות ספציפיות.</li>
</ul>
<p>אם נתקלתם ברכיב שאינו נגיש, נשמח לדעת ונתקן בהקדם.</p>
<h2>הסדרי נגישות במתן השירות</h2>
<p>השירות שלנו ניתן בבית הלקוח או בעסק שלו, ואין לנו קבלת קהל במשרד. אם אתם זקוקים להתאמה בזמן התיאום או בזמן העבודה, למשל תיאום בהודעות כתובות במקום בשיחה, אמרו לנו ונתאים את עצמנו.</p>
<h2>פנייה בנושא נגישות</h2>
<p>לכל שאלה, בקשה או תלונה בנושא נגישות אפשר לפנות אלינו:</p>
<ul class="legal-list">
<li>טלפון: {tel}</li>
<li>הודעה ב{wa}</li>
</ul>
<p>נחזור אליכם בהקדם.</p>
<p class="legal-meta">תאריך בדיקת הנגישות האחרונה: {AUDIT_DATE}<br>תאריך עדכון ההצהרה: {AUDIT_DATE}</p>"""
    legal_page("hatzharat-negishut", "הצהרת נגישות | ג'מבו קלין Jumbo Clean",
               "הצהרת הנגישות של אתר ג׳מבו קלין: רמת הנגישות, ההתאמות שבוצעו באתר, תפריט הנגישות ופרטי פנייה בנושא נגישות.",
               "הצהרת נגישות", a11y)
    priv = f"""
<p>מדיניות זו מסבירה איזה מידע נאסף כשאתם משתמשים באתר jumbo-clean.co.il, למה הוא משמש ומה הזכויות שלכם, בהתאם לחוק הגנת הפרטיות, התשמ״א 1981.</p>
<h2>מי אנחנו</h2>
<p>האתר שייך לג׳מבו קלין, עסק לשיפוצים, ניקיון ופוליש. ליצירת קשר: {tel} או ב{wa}.</p>
<h2>איזה מידע אנחנו מקבלים</h2>
<ul class="legal-list">
<li><b>פרטים שאתם שולחים לנו:</b> כשאתם ממלאים את הטופס, הפרטים (שם, טלפון, שירות, עיר ותיאור העבודה) מועברים לוואטסאפ במכשיר שלכם. הם מגיעים אלינו רק אם תלחצו "שליחה" בוואטסאפ. האתר עצמו לא שומר אותם ולא מעביר אותם לאף גורם אחר.</li>
<li><b>שיחות והודעות:</b> כשאתם מתקשרים או כותבים לנו, נקבל את מספר הטלפון ואת מה שתספרו לנו.</li>
<li><b>מידע טכני:</b> שרת האחסון (Vercel) רושם באופן אוטומטי נתונים טכניים כמו כתובת IP וסוג דפדפן, לצורכי אבטחה ותפעול. הגופנים באתר נטענים מ־Google Fonts, ולכן הדפדפן שלכם פונה לשרתי Google.</li>
</ul>
<h2>למה אנחנו משתמשים במידע</h2>
<p>רק כדי לחזור אליכם, לתת הצעת מחיר, לתאם עבודה ולתת שירות. לא נמכור את הפרטים שלכם ולא נשלח לכם פרסומות בלי הסכמה.</p>
<h2>עוגיות ושמירה בדפדפן</h2>
<p>האתר לא משתמש בעוגיות מעקב, בכלי סטטיסטיקה או בפרסום ממוקד. אם תשנו הגדרות בתפריט הנגישות, הן יישמרו בדפדפן שלכם בלבד (localStorage) כדי שלא תצטרכו להגדיר אותן שוב.</p>
<h2>שמירה ואבטחה</h2>
<p>פניות שמגיעות אלינו נשמרות בטלפון של העסק רק כל עוד הן נחוצות לטיפול בעבודה. האתר מוגש בחיבור מאובטח (HTTPS).</p>
<h2>הזכויות שלכם</h2>
<p>אתם רשאים לבקש לעיין במידע שלכם שנמצא אצלנו, לתקן אותו או למחוק אותו. פנו אלינו בטלפון או בוואטסאפ ונטפל בבקשה.</p>
<p class="legal-meta">עדכון אחרון: {AUDIT_DATE}</p>"""
    legal_page("privacy", "מדיניות פרטיות | ג'מבו קלין Jumbo Clean",
               "מדיניות הפרטיות של אתר ג׳מבו קלין: איזה מידע נאסף, למה הוא משמש והזכויות שלכם.",
               "מדיניות פרטיות", priv)

if __name__ == "__main__":
    build_images()
    home()
    for s in SERVICES:
        service(s)
    legal()
    product()
    sitemap()
    print("built", 4 + len(SERVICES), "pages")
