"""Alerta zilnica: garsoniere noi in Brasov si Sanpetru (max 55.000 EUR).

Verifica OLX, Storia si Imobiliare, compara cu anunturile deja vazute
(seen.json) si trimite cate o notificare ntfy pentru fiecare anunt nou,
cu link direct. Suprafata (mp) apare prima in titlul notificarii.
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

try:  # imita amprenta TLS a unui Chrome real (OLX/Imobiliare blocheaza clientii simpli)
    from curl_cffi import requests as cffi_requests
except ImportError:
    cffi_requests = None

MAX_EUR = 55000
MIN_EUR = 10000  # sub asta e aproape sigur pret de inchiriere sau eroare
EUR_RON = float(os.environ.get("EUR_RON", "5.1"))
NTFY_TOPIC = os.environ.get("NTFY_TOPIC", "")
NTFY_SERVER = os.environ.get("NTFY_SERVER", "https://ntfy.sh")
STATE_FILE = Path(os.environ.get("STATE_FILE", "seen.json"))
DEBUG_DIR = os.environ.get("DEBUG_DIR")  # daca e setat, salveaza HTML brut
DRY_RUN = os.environ.get("DRY_RUN") == "1"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/130.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "ro-RO,ro;q=0.9,en;q=0.8",
}

if cffi_requests:
    SESSION = cffi_requests.Session(impersonate="chrome")
else:
    SESSION = requests.Session()
    SESSION.headers.update(HEADERS)


class _Last:
    url = ""


LAST = _Last()


def log(*a):
    print(*a, flush=True)


def fetch(url, tag):
    r = SESSION.get(url, timeout=30)
    log(f"[{tag}] GET {url} -> {r.status_code}, {len(r.text)} bytes")
    if DEBUG_DIR:
        Path(DEBUG_DIR).mkdir(parents=True, exist_ok=True)
        safe = re.sub(r"[^a-z0-9]+", "_", tag.lower())
        (Path(DEBUG_DIR) / f"{safe}.html").write_text(r.text, encoding="utf-8")
        if r.status_code >= 400:
            log(f"[{tag}] body: {re.sub(r'\s+', ' ', r.text[:400])}")
    LAST.url = str(r.url)
    r.raise_for_status()
    return r.text


def to_float(x):
    if x is None:
        return None
    if isinstance(x, (int, float)):
        return float(x)
    m = re.search(r"\d+(?:[.,]\d+)?", str(x).replace(" ", ""))
    return float(m.group(0).replace(",", ".")) if m else None


def price_eur(value, currency):
    v = to_float(value)
    if v is None:
        return None
    cur = (currency or "EUR").upper()
    if cur in ("RON", "LEI"):
        return v / EUR_RON
    return v


# ---------------------------------------------------------------- OLX
# API-ul public folosit de site-ul OLX. category 907 = apartamente si garsoniere
# de vanzare, region 4 = judetul Brasov; filtram pe 1 camera (garsoniera).

OLX_CITIES = {"Brasov": 26711, "Sanpetru": 28445}


def olx_param(ad, key):
    for p in ad.get("params") or []:
        if p.get("key") == key:
            return p.get("value") or {}
    return {}


def olx_listings():
    out = []
    for city, city_id in OLX_CITIES.items():
        for offset in (0, 50):
            url = (
                "https://www.olx.ro/api/v1/offers/?limit=50"
                f"&offset={offset}&category_id=907&region_id=4&city_id={city_id}"
                "&sort_by=created_at:desc&currency=EUR"
                "&filter_enum_rooms%5B0%5D=one"
                f"&filter_float_price:to={MAX_EUR}"
            )
            try:
                data = json.loads(fetch(url, f"olx_{city}_{offset}"))
            except Exception as e:
                log(f"[olx] eroare {city}: {e}")
                break
            ads = data.get("data") or []
            log(f"[olx] {city} offset {offset}: {len(ads)} anunturi")
            for ad in ads:
                pr = olx_param(ad, "price")
                area = olx_param(ad, "m")
                loc = ad.get("location") or {}
                out.append({
                    "id": f"olx:{ad.get('id')}",
                    "site": "OLX",
                    "title": (ad.get("title") or "").strip(),
                    "url": ad.get("url"),
                    "price_eur": price_eur(pr.get("value"), pr.get("currency")),
                    "area": to_float(area.get("key") or area.get("label")),
                    "where": ", ".join(x for x in [(loc.get("city") or {}).get("name"),
                                                    (loc.get("district") or {}).get("name")] if x) or city,
                })
            if len(ads) < 50:
                break
    return out


# ------------------------------------------------------------- STORIA

STORIA_LOCS = {"Brasov": "brasov/brasov", "Sanpetru": "brasov/sanpetru"}


def storia_listings():
    out = []
    for city, path in STORIA_LOCS.items():
        url = (
            f"https://www.storia.ro/ro/rezultate/vanzare/garsoniere/{path}"
            f"?priceMax={MAX_EUR}&by=LATEST&direction=DESC&limit=72"
        )
        try:
            html = fetch(url, f"storia_{city}")
        except Exception as e:
            log(f"[storia] eroare {city}: {e}")
            continue
        m = re.search(r'<script id="__NEXT_DATA__"[^>]*>(.*?)</script>', html, re.S)
        if not m:
            log(f"[storia] {city}: nu am gasit __NEXT_DATA__")
            continue
        data = json.loads(m.group(1))
        items = (
            data.get("props", {}).get("pageProps", {}).get("data", {})
            .get("searchAds", {}).get("items", [])
        ) or []
        log(f"[storia] {city}: {len(items)} anunturi in pagina")
        for it in items:
            tp = it.get("totalPrice") or {}
            addr = ((it.get("location") or {}).get("address") or {})
            cname = (addr.get("city") or {}).get("name") or city
            slug = it.get("slug") or ""
            out.append({
                "id": f"storia:{it.get('id')}",
                "site": "Storia",
                "title": (it.get("title") or "").strip(),
                "url": f"https://www.storia.ro/ro/oferta/{slug}",
                "price_eur": price_eur(tp.get("value"), tp.get("currency")),
                "area": to_float(it.get("areaInSquareMeters")),
                "where": cname,
            })
    return out


# --------------------------------------------------------- IMOBILIARE

IMOB_LOCS = {"Brasov": "brasov", "Sanpetru": "judetul-brasov/sanpetru"}


def walk(obj):
    if isinstance(obj, dict):
        yield obj
        for v in obj.values():
            yield from walk(v)
    elif isinstance(obj, list):
        for v in obj:
            yield from walk(v)


def imobiliare_listings():
    out = []
    for city, path in IMOB_LOCS.items():
        url = f"https://www.imobiliare.ro/vanzare-garsoniere/{path}?pret-max={MAX_EUR}&ordine=noi"
        try:
            html = fetch(url, f"imobiliare_{city}")
        except Exception as e:
            log(f"[imobiliare] eroare {city}: {e}")
            continue
        found = parse_imobiliare(html, city)
        log(f"[imobiliare] {city}: {len(found)} anunturi in pagina")
        out.extend(found)
    return out


def parse_imobiliare(html, city):
    found = {}
    # 1) JSON-LD (schema.org) daca exista
    for block in re.findall(r'<script[^>]*application/ld\+json[^>]*>(.*?)</script>', html, re.S):
        try:
            data = json.loads(block)
        except Exception:
            continue
        for d in walk(data):
            u = d.get("url") or ""
            if "imobiliare.ro/oferta/" in u or "/oferta/" in u:
                offers = d.get("offers") or {}
                if isinstance(offers, list):
                    offers = offers[0] if offers else {}
                area = None
                fs = d.get("floorSize") or (d.get("itemOffered") or {}).get("floorSize")
                if isinstance(fs, dict):
                    area = to_float(fs.get("value"))
                found[u] = {
                    "id": "imob:" + u.rstrip("/").split("/")[-1],
                    "site": "Imobiliare",
                    "title": (d.get("name") or "").strip(),
                    "url": u if u.startswith("http") else "https://www.imobiliare.ro" + u,
                    "price_eur": price_eur(offers.get("price"), offers.get("priceCurrency")),
                    "area": area,
                    "where": city,
                }
    return list(found.values())


# ---------------------------------------------------------- PIPELINE

def in_area(item):
    w = (item.get("where") or "").lower()
    return "bra" in w or "sanpetru" in w or "sânpetru" in w


EXCLUDE = re.compile(r"\b(boxa|boxă|parcare|garaj|spatiu comercial|spațiu comercial|regim hotelier|teren)\b", re.I)


def ok(item):
    if not item.get("url") or not item.get("id"):
        return False
    if EXCLUDE.search(item.get("title") or ""):
        return False
    p = item.get("price_eur")
    if p is not None and (p > MAX_EUR * 1.001 or p < MIN_EUR):
        return False
    return in_area(item)


def fmt_price(p):
    return "pret ?" if p is None else f"{p:,.0f}€".replace(",", ".")


def fmt_area(a):
    return "? mp" if a is None else f"{a:g} mp"


def ntfy(title, body, url=None, priority=3, tags="house"):
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


def should_run():
    """Cron-ul ruleaza la 06:34 si 07:34 UTC; pastram doar cel care e 09:34 la Brasov."""
    sched = os.environ.get("SCHEDULE", "")
    if not sched:
        return True  # rulare manuala
    off = datetime.now(ZoneInfo("Europe/Bucharest")).utcoffset().total_seconds() / 3600
    wanted = {2: "34 7 * * *", 3: "34 6 * * *"}[int(off)]
    if sched != wanted:
        log(f"Sar peste: cron '{sched}', ora Romaniei e UTC+{off:g}")
        return False
    return True


def main():
    if not should_run():
        return 0

    state = json.loads(STATE_FILE.read_text()) if STATE_FILE.exists() else {}
    seen = set(state.get("seen", []))
    first_run = not state

    items, errors = [], []
    for name, fn in (("OLX", olx_listings), ("Storia", storia_listings), ("Imobiliare", imobiliare_listings)):
        try:
            got = fn()
            if not got:
                errors.append(name)
            items.extend(got)
        except Exception as e:
            log(f"[{name}] eroare: {e}")
            errors.append(name)

    if DEBUG_DIR:
        for i in items:
            log("[item]", json.dumps({k: i[k] for k in ("site", "area", "price_eur", "where", "title", "url")}, ensure_ascii=False))
    items = [i for i in items if ok(i)]
    uniq = {i["id"]: i for i in items}
    items = sorted(uniq.values(), key=lambda i: -(i["area"] or 0))
    new = [i for i in items if i["id"] not in seen]
    log(f"Total valide: {len(items)}, noi: {len(new)}, surse fara rezultate: {errors}")

    if first_run:
        top = items[:5]
        body = "\n".join(f"{fmt_area(i['area'])} · {fmt_price(i['price_eur'])} · {i['where']} ({i['site']})"
                         for i in top)
        ntfy(f"Monitorizare pornita: {len(items)} garsoniere existente",
             "Cele mai mari acum:\n" + body + "\n\nDe maine primesti doar anunturile noi.",
             url=top[0]["url"] if top else None, tags="white_check_mark")
    else:
        for i in new[:25]:
            ntfy(f"{fmt_area(i['area'])} · {fmt_price(i['price_eur'])} · {i['where']}",
                 f"{i['title']}\n{i['site']}: {i['url']}", url=i["url"], priority=4)
        if len(new) > 25:
            ntfy(f"+{len(new) - 25} garsoniere noi", "Prea multe pentru notificari individuale; verifica site-urile.")

    if errors and len(errors) == 3:
        ntfy("Alerta garsoniere: nicio sursa nu a raspuns", "Verifica GitHub Actions.", tags="warning")

    seen |= {i["id"] for i in items}
    state = {"seen": sorted(seen), "last_run": datetime.now(timezone.utc).isoformat(timespec="seconds")}
    STATE_FILE.write_text(json.dumps(state, indent=1, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
