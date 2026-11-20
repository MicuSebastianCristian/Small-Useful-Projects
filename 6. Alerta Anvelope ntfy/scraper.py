"""Alerta: anvelope de iarna 225/50 R17 pe OLX, in Brasov si imprejurimi (50 km).

Ruleaza din ora in ora (07:00 - 22:00 ora Romaniei) din GitHub Actions,
compara cu anunturile deja vazute (seen.json) si trimite cate o notificare
ntfy pentru fiecare anunt nou, cu link direct.
"""

import json
import os
import re
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

import requests

try:  # imita amprenta TLS a unui Chrome real (OLX blocheaza clientii simpli)
    from curl_cffi import requests as cffi_requests
except ImportError:
    cffi_requests = None

WIDTH, PROFILE, RIM = 225, 50, 17
MAX_LEI = int(os.environ.get("MAX_LEI", "1500"))  # pret maxim afisat in anunt
NTFY_TOPIC = os.environ.get("NTFY_TOPIC", "")
NTFY_SERVER = os.environ.get("NTFY_SERVER", "https://ntfy.sh")
STATE_FILE = Path(os.environ.get("STATE_FILE", "seen.json"))
DRY_RUN = os.environ.get("DRY_RUN") == "1"
FULL_LIST = os.environ.get("FULL_LIST") == "true"
VERBOSE = os.environ.get("VERBOSE") == "1"

if cffi_requests:
    SESSION = cffi_requests.Session(impersonate="chrome")
else:
    SESSION = requests.Session()
    SESSION.headers.update({
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                      "(KHTML, like Gecko) Chrome/130.0 Safari/537.36",
        "Accept-Language": "ro-RO,ro;q=0.9,en;q=0.8",
    })


def log(*a):
    print(*a, flush=True)


# ---------------------------------------------------------------- OLX
# Categoria 3792 = Anvelope. region 4 = judetul Brasov, oras Brasov + 50 km.
OLX_BASE = ("https://www.olx.ro/api/v1/offers/?limit=50&category_id=3792"
            "&region_id=4&city_id=26711&distance=50&sort_by=created_at:desc")
SEARCHES = {
    # anunturile care au completat dimensiunile in filtre
    "filtre": f"&filter_enum_tyres_width[0]=parts-tyres-width-{WIDTH}"
              f"&filter_enum_tyres_inches[0]=parts-tyres-inches-{RIM}",
    # anunturile care au dimensiunea doar in titlu
    "text": f"&query={WIDTH}%20{PROFILE}%20{RIM}",
}


def olx_param(ad, key):
    for p in ad.get("params") or []:
        if p.get("key") == key:
            return p.get("value") or {}
    return {}


def fetch_json(url, tag):
    r = SESSION.get(url, timeout=30)
    log(f"[{tag}] GET -> {r.status_code}, {len(r.text)} bytes")
    r.raise_for_status()
    return r.json()


def olx_ads():
    ads = {}
    for name, extra in SEARCHES.items():
        for offset in (0, 50, 100):
            try:
                data = fetch_json(f"{OLX_BASE}{extra}&offset={offset}", f"olx_{name}_{offset}")
            except Exception as e:
                log(f"[olx] eroare {name}: {e}")
                break
            page = data.get("data") or []
            for ad in page:
                ads[ad.get("id")] = ad
            if len(page) < 50:
                break
    return list(ads.values())


# ---------------------------------------------------------- FILTRE

SIZE_RE = re.compile(rf"\b{WIDTH}\s*[/.\-\s]\s*{PROFILE}\s*[/.\-\s]?\s*z?r?\s*{RIM}\b", re.I)
WINTER_RE = re.compile(
    r"iarn|winter|m\s*\+\s*s|snow|zapad|zăpad|alpin|sottozero|blizzak|ultra\s*grip|polaris"
    r"|hakka|wintrac|krisalp|snowprox|i\s*cept|frigo|nordic|lm\s*0|\bice\b|3pmsf", re.I)
SUMMER_RE = re.compile(r"\bvar[aă]\b|summer", re.I)
ALLSEASON_RE = re.compile(r"all\s*-?\s*season|allseason|mixt|4\s*season|quattrac|cross\s*climate"
                          r"|vara\s*-\s*iarna|vară\s*-\s*iarnă|weather\s*control", re.I)
EXCLUDE_RE = re.compile(r"\bjant[ae]\b|\bjenti\b|capace|lanturi|lanțuri|\bcamera\b|vulcanizare"
                        r"|cumpar|cumpăr", re.I)


def text_of(ad):
    desc = re.sub(r"<[^>]+>", " ", ad.get("description") or "")
    return f"{ad.get('title') or ''}\n{desc}"


def size_ok(ad):
    if SIZE_RE.search(ad.get("title") or ""):
        return True
    w = olx_param(ad, "tyres_width").get("key") or ""
    p = olx_param(ad, "tyres_profile").get("key") or ""
    i = olx_param(ad, "tyres_inches").get("key") or ""
    if w.endswith(f"-{WIDTH}") and p.endswith(f"-{PROFILE}") and i.endswith(f"-{RIM}"):
        return True
    # titlu fara dimensiune completa (ex. "Anvelope iarna Dunlop"): cautam in descriere
    return bool(SIZE_RE.search(text_of(ad))) and not re.search(r"\b\d{3}\s*[/.\-\s]\s*\d{2}", ad.get("title") or "")


def season_ok(ad):
    season = olx_param(ad, "season").get("key")
    title = ad.get("title") or ""
    if season == "zimni":
        return True
    if season in ("letni", "vsesezonni"):
        return False
    if ALLSEASON_RE.search(title):
        return False
    if WINTER_RE.search(title):
        return True
    if SUMMER_RE.search(title):
        return False
    body = text_of(ad)
    return bool(WINTER_RE.search(body)) and not ALLSEASON_RE.search(body)


def price_lei(ad):
    pr = olx_param(ad, "price")
    v = pr.get("value")
    if v is None:
        m = re.search(r"[\d .]+", str(pr.get("label") or ""))
        v = float(m.group(0).replace(" ", "").replace(".", "")) if m else None
    if v is None:
        return None
    if (pr.get("currency") or "RON").upper() == "EUR":
        v *= float(os.environ.get("EUR_RON", "5.1"))
    return float(v)


def param_text(ad, key):
    v = olx_param(ad, key)
    x = v.get("label") or v.get("key")
    if isinstance(x, list):
        x = x[0] if x else None
    return str(x) if x not in (None, "") else None


def to_item(ad):
    tread = param_text(ad, "tread_depth")
    year = param_text(ad, "year_of_manufacture")
    if not year:
        m = re.search(r"dot\s*'?\s*(?:\d{2})?(20\d{2}|\d{2}(?=\D|$))", text_of(ad), re.I)
        if m:
            y = m.group(1)
            year = y if len(y) == 4 else f"20{y}"
    loc = ad.get("location") or {}
    return {
        "id": f"olx:{ad.get('id')}",
        "title": (ad.get("title") or "").strip(),
        "url": (ad.get("url") or "").split("?")[0],
        "price": price_lei(ad),
        "city": (loc.get("city") or {}).get("name") or "?",
        "year": year,
        "tread": tread,
    }


def fmt_price(p):
    return "pret ?" if p is None else f"{p:,.0f} lei".replace(",", ".")


def details(i):
    bits = [fmt_price(i["price"]), i["city"]]
    if i["year"]:
        bits.append(f"DOT {i['year']}")
    if i["tread"]:
        bits.append(f"{i['tread']} mm")
    return " · ".join(bits)


# ---------------------------------------------------------- NTFY

def ntfy(title, body, url=None, priority=3, tags="snowflake"):
    if DRY_RUN or not NTFY_TOPIC:
        log(f"[ntfy dry] {title} | {body} | {url}")
        return
    headers = {"Title": title.encode("utf-8"), "Priority": str(priority), "Tags": tags}
    if url:
        headers["Click"] = url
        headers["Actions"] = f"view, Deschide anuntul, {url}"
    r = requests.post(f"{NTFY_SERVER}/{NTFY_TOPIC}", data=body.encode("utf-8"),
                      headers=headers, timeout=20)
    log(f"[ntfy] {r.status_code} {title}")
    time.sleep(1)


def send_list(items, label):
    lines = [f"{details(i)}\n{i['title'][:70]}\n{i['url']}" for i in items]
    chunks, cur = [], []
    for ln in lines:
        if cur and (len(cur) == 10 or len("\n\n".join(cur + [ln]).encode()) > 3500):
            chunks.append(cur)
            cur = []
        cur.append(ln)
    if cur:
        chunks.append(cur)
    for n, ch in enumerate(chunks, 1):
        ntfy(f"{label} ({n}/{len(chunks)})", "\n\n".join(ch), tags="clipboard")


# ---------------------------------------------------------- PIPELINE

def should_run():
    """Cron-ul ruleaza din ora in ora; sarim peste orele de noapte (ora Romaniei)."""
    if not os.environ.get("SCHEDULE"):
        return True  # rulare manuala
    h = datetime.now(ZoneInfo("Europe/Bucharest")).hour
    if h < 7 or h > 22:
        log(f"Sar peste: e ora {h} in Romania")
        return False
    return True


def main():
    if not should_run():
        return 0

    state = json.loads(STATE_FILE.read_text()) if STATE_FILE.exists() else {}
    seen = set(state.get("seen", []))
    first_run = not state

    ads = olx_ads()
    log(f"[olx] {len(ads)} anunturi unice gasite")
    items = []
    for ad in ads:
        reason = None
        if EXCLUDE_RE.search(ad.get("title") or ""):
            reason = "exclus (jante/accesorii)"
        elif not size_ok(ad):
            reason = "alta dimensiune"
        elif not season_ok(ad):
            reason = "nu e de iarna"
        else:
            it = to_item(ad)
            if it["price"] is not None and it["price"] > MAX_LEI:
                reason = f"prea scump ({fmt_price(it['price'])})"
            else:
                items.append(it)
        if VERBOSE:
            log(f"  {'OK ' if not reason else '-- '}{ad.get('title')!r} {reason or ''}")

    items.sort(key=lambda i: i["price"] if i["price"] is not None else 1e9)
    new = [i for i in items if i["id"] not in seen]
    log(f"Potrivite: {len(items)}, noi: {len(new)}")

    if first_run or FULL_LIST:
        if items:
            send_list(items, f"{len(items)} anunturi {WIDTH}/{PROFILE} R{RIM} iarna, dupa pret")
        else:
            ntfy("Alerta anvelope pornita", f"Momentan nu e niciun anunt {WIDTH}/{PROFILE} R{RIM} de iarna. "
                 "Te anunt cand apare unul.")
    else:
        for i in new[:10]:
            ntfy(f"{details(i)}", f"{i['title']}\n{i['url']}", url=i["url"], priority=4)
        if len(new) > 10:
            send_list(new[10:], f"Inca {len(new) - 10} anunturi noi")

    if not ads:
        ntfy("Alerta anvelope: OLX nu a raspuns", "Verifica GitHub Actions.", tags="warning")

    seen |= {i["id"] for i in items}
    state = {"seen": sorted(seen), "last_run": datetime.now(timezone.utc).isoformat(timespec="seconds")}
    STATE_FILE.write_text(json.dumps(state, indent=1, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
