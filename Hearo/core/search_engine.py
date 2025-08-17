# keyword_info_service_v3.py
from __future__ import annotations
import asyncio, html, urllib.parse, datetime as dt, re, atexit, sys
from typing import Dict, Any, List, Optional, Tuple
from threading import Thread
import aiohttp
from cachetools import TTLCache
import feedparser

try:
    # tăng độ chính xác so khớp tiếng Việt & unicode
    from unidecode import unidecode
except Exception:
    def unidecode(x): return x  # fallback nếu chưa cài

# =======================
# Config
# =======================
DEFAULT_LANG = "en"          # 'vi' nếu muốn mặc định tiếng Việt
DEFAULT_NEWS_HL = "en"
DEFAULT_NEWS_GL = "US"
DEFAULT_NEWS_CEID = "US:en"
NEWS_WINDOW_DAYS = 14

CACHE_TTL = 600
cache = TTLCache(maxsize=4096, ttl=CACHE_TTL)

UA = "KeywordInfoService/3.0 (+https://example.com)"

OPENVERSE_ENDPOINT = "https://api.openverse.engineering/v1/images"
WIKI_SUMMARY       = "https://{lang}.wikipedia.org/api/rest_v1/page/summary/{title}"
WIKI_SEARCH        = "https://{lang}.wikipedia.org/w/rest.php/v1/search/page?q={q}&limit=1"
WIKI_PAGEIMAGES    = "https://{lang}.wikipedia.org/w/api.php?action=query&format=json&prop=pageimages&titles={title}&pithumbsize=600&origin=*"
COMMONS_MEDIASEARCH= "https://commons.wikimedia.org/w/api.php?action=query&format=json&generator=search&gsrnamespace=6&gsrlimit={n}&gsrsearch={q}&prop=imageinfo&iiprop=url|mime&iiurlwidth=600&origin=*"
WIKIDATA_SEARCH    = "https://www.wikidata.org/w/api.php?action=wbsearchentities&format=json&language={lang}&search={q}&limit=1&origin=*"

GOOGLE_NEWS_RSS    = "https://news.google.com/rss/search?q={q}&hl={hl}&gl={gl}&ceid={ceid}"
DDG_IA             = "https://api.duckduckgo.com/?q={q}&format=json&no_html=1&skip_disambig=1"
WIKT_DEF           = "https://en.wiktionary.org/api/rest_v1/page/definition/{term}"

# =======================
# Utils
# =======================
def _now_iso() -> str:
    return dt.datetime.utcnow().replace(microsecond=0).isoformat() + "Z"

def _norm_kw(kw: str) -> str:
    return (kw or "").strip()

def _cache_key(prefix: str, *parts: str) -> str:
    return prefix + "::" + "||".join(parts)

def _quote(s: str) -> str:
    return urllib.parse.quote(s)

def _normalize_text(s: str) -> str:
    s = unidecode(s or "").lower()
    s = re.sub(r"[^a-z0-9\s\-_/\.]", " ", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s

def _tokenize(s: str) -> List[str]:
    s = _normalize_text(s)
    return [t for t in s.split() if len(t) >= 2]

def _jaccard(a: List[str], b: List[str]) -> float:
    sa, sb = set(a), set(b)
    if not sa or not sb: return 0.0
    return len(sa & sb) / len(sa | sb)

def _pick_first(items: List[Dict[str, Any]], n: int) -> List[Dict[str, Any]]:
    out, seen = [], set()
    for it in items:
        key = (it.get("url") or "") + "|" + (it.get("thumbnail") or "")
        if not key or key in seen: 
            continue
        out.append(it)
        seen.add(key)
        if len(out) >= n: break
    return out

# Robust HTTP
async def _get_json(session: aiohttp.ClientSession, url: str, **kw) -> Optional[Dict[str, Any]]:
    try:
        async with session.get(url, timeout=10, **kw) as r:
            if r.status == 200:
                return await r.json()
    except Exception:
        return None
    return None

async def _get_text(session: aiohttp.ClientSession, url: str, **kw) -> Optional[str]:
    try:
        async with session.get(url, timeout=10, **kw) as r:
            if r.status == 200:
                return await r.text()
    except Exception:
        return None
    return None

# =======================
# Definitions (multi-fallback)
# =======================
async def fetch_wikipedia_summary(session: aiohttp.ClientSession, keyword: str, lang: str) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
    """Trả (summary, canonical_title) hoặc (None, None). Nếu miss, thử search để lấy title chuẩn."""
    # attempt direct
    url = WIKI_SUMMARY.format(lang=lang, title=_quote(keyword.replace(" ", "_")))
    data = await _get_json(session, url)
    if data and data.get("title"):
        return ({
            "title": data.get("title"),
            "extract": data.get("extract") or data.get("description"),
            "url": (data.get("content_urls") or {}).get("desktop", {}).get("page"),
            "thumbnail": (data.get("thumbnail") or {}).get("source"),
        }, data.get("title"))
    # search then summary
    s_url = WIKI_SEARCH.format(lang=lang, q=_quote(keyword))
    s = await _get_json(session, s_url)
    lst = (s or {}).get("pages") or (s or {}).get("results") or []
    if lst:
        title = lst[0].get("title") or lst[0].get("key")
        if title:
            url2 = WIKI_SUMMARY.format(lang=lang, title=_quote(title.replace(" ", "_")))
            d2 = await _get_json(session, url2)
            if d2 and d2.get("title"):
                return ({
                    "title": d2.get("title"),
                    "extract": d2.get("extract") or d2.get("description"),
                    "url": (d2.get("content_urls") or {}).get("desktop", {}).get("page"),
                    "thumbnail": (d2.get("thumbnail") or {}).get("source"),
                }, d2.get("title"))
            return None, title
    return None, None

async def fetch_wikidata_desc(session: aiohttp.ClientSession, keyword: str, lang: str) -> Optional[Dict[str, Any]]:
    url = WIKIDATA_SEARCH.format(lang=lang, q=_quote(keyword))
    d = await _get_json(session, url)
    try:
        s = (d or {}).get("search", [])
        if s:
            itm = s[0]
            lbl = itm.get("label") or keyword
            desc = itm.get("description")
            page = f"https://www.wikidata.org/wiki/{itm.get('id')}" if itm.get("id") else None
            if desc or page:
                return {"title": lbl, "extract": desc, "url": page}
    except Exception:
        pass
    return None

async def fetch_wiktionary_definition(session: aiohttp.ClientSession, term: str) -> Optional[Dict[str, Any]]:
    url = WIKT_DEF.format(term=_quote(term))
    data = await _get_json(session, url)
    try:
        senses = (data or {}).get("en") or []
        defs = []
        for s in senses:
            for d in s.get("definitions", []):
                if d.get("definition"):
                    defs.append(d["definition"])
        if defs:
            return {"title": term, "extract": "; ".join(defs[:3]), "url": f"https://en.wiktionary.org/wiki/{_quote(term)}"}
    except Exception:
        pass
    return None

async def fetch_ddg_instant_answer(session: aiohttp.ClientSession, keyword: str) -> Optional[Dict[str, Any]]:
    url = DDG_IA.format(q=_quote(keyword))
    data = await _get_json(session, url)
    if not data: return None
    abstract = data.get("AbstractText") or data.get("Abstract")
    link = data.get("AbstractURL") or data.get("Redirect")
    img = data.get("Image")
    if abstract or link or img:
        return {"title": data.get("Heading") or keyword, "extract": abstract, "url": link, "thumbnail": img}
    return None

# =======================
# Images (relevance-first + scoring)
# =======================
async def fetch_wikipedia_images(session: aiohttp.ClientSession, canonical_title: str, lang: str, max_images: int) -> List[Dict[str, Any]]:
    out: List[Dict[str, Any]] = []

    # a) page thumbnail
    pi_url = WIKI_PAGEIMAGES.format(lang=lang, title=_quote(canonical_title.replace(" ", "_")))
    pi = await _get_json(session, pi_url)
    try:
        pages = (pi or {}).get("query", {}).get("pages", {}) or {}
        for _, pg in pages.items():
            t = (pg.get("thumbnail") or {}).get("source")
            if t:
                out.append({"thumbnail": t, "url": t, "title": canonical_title, "source": "wikipedia"})
    except Exception:
        pass

    # b) Commons search
    cms_url = COMMONS_MEDIASEARCH.format(n=max_images, q=_quote(canonical_title))
    cms = await _get_json(session, cms_url)
    try:
        pages = (cms or {}).get("query", {}).get("pages", {}) or {}
        for _, pg in pages.items():
            info = (pg.get("imageinfo") or [{}])[0]
            thumb = info.get("thumburl")
            url = info.get("url")
            title = pg.get("title") or canonical_title
            if thumb or url:
                out.append({"thumbnail": thumb or url, "url": url or thumb, "title": title, "source": "commons"})
    except Exception:
        pass

    return _pick_first(out, max_images)

def _score_image(keyword: str, cand: Dict[str, Any]) -> float:
    kw_norm = _normalize_text(keyword)
    kw_tokens = _tokenize(keyword)
    title = cand.get("title") or ""
    title_norm = _normalize_text(title)

    score = 0.0
    if kw_norm and title_norm:
        if kw_norm == title_norm: score += 3.0
        if f" {kw_norm} " in f" {title_norm} ": score += 2.0
        score += 2.5 * _jaccard(kw_tokens, _tokenize(title))
    # ưu tiên nguồn đáng tin
    src = (cand.get("source") or "").lower()
    if "wikipedia" in src or "wikimedia" in src or "commons" in src:
        score += 1.5
    if "flickr" in src:
        score += 0.5
    return score

async def fetch_openverse_images(session: aiohttp.ClientSession, keyword: str, max_images: int) -> List[Dict[str, Any]]:
    headers = {"User-Agent": UA}
    out: List[Dict[str, Any]] = []

    async def call(params):
        j = await _get_json(session, OPENVERSE_ENDPOINT, params=params, headers=headers)
        res = []
        if j and j.get("results"):
            for it in j["results"]:
                res.append({
                    "thumbnail": it.get("thumbnail"),
                    "url": it.get("url"),
                    "title": it.get("title") or "",
                    "source": it.get("source") or "openverse",
                })
        return res

    # 1) title=
    out.extend(await call({"title": keyword, "mature": "false", "page_size": max_images}))
    # 2) q="keyword"
    if len(out) < max_images:
        out.extend(await call({"q": f"\"{keyword}\"", "mature": "false", "page_size": max_images}))
    # 3) q=keyword
    if len(out) < max_images:
        out.extend(await call({"q": keyword, "mature": "false", "page_size": max_images}))

    # chấm điểm + lọc theo ngưỡng
    scored = []
    for it in out:
        if not it.get("thumbnail"): 
            continue
        sc = _score_image(keyword, it)
        it["relevance"] = sc
        scored.append(it)

    scored.sort(key=lambda x: x["relevance"], reverse=True)
    # Ngưỡng tối thiểu; nếu keyword quá hiếm, vẫn trả vài ảnh đầu
    filtered = [x for x in scored if x["relevance"] >= 1.5] or scored[:max_images]
    return _pick_first(filtered, max_images)

# =======================
# News (time-bounded & exact)
# =======================
async def fetch_google_news(session: aiohttp.ClientSession, keyword: str, *, max_items: int,
                            hl: str, gl: str, ceid: str, window_days: int = NEWS_WINDOW_DAYS) -> List[Dict[str, Any]]:
    key = _cache_key("news", keyword.lower(), str(max_items), hl, gl, ceid, str(window_days))
    if key in cache: 
        return cache[key]
    q = f"\"{keyword}\" when:{window_days}d"
    url = GOOGLE_NEWS_RSS.format(q=_quote(q), hl=hl, gl=gl, ceid=ceid)
    try:
        async with session.get(url, timeout=10, headers={"User-Agent": UA}) as r:
            if r.status != 200: return []
            xml = await r.text()
    except Exception:
        return []
    feed = await asyncio.to_thread(feedparser.parse, xml)
    out = []
    for e in feed.entries[:max_items]:
        out.append({
            "title": e.get("title"),
            "url": e.get("link"),
            "published": e.get("published"),
            "source": (e.get("source") or {}).get("title") if isinstance(e.get("source"), dict) else None
        })
    cache[key] = out
    return out

# =======================
# Aggregator
# =======================
async def fetch_keyword_info(keyword: str, *, lang: str = DEFAULT_LANG,
                             max_images: int = 6, max_news: int = 6) -> Dict[str, Any]:
    kw = _norm_kw(keyword)
    if not kw:
        return {"keyword": keyword, "lang": lang, "fetched_at": _now_iso(), "definition": None, "images": [], "news": []}

    async with aiohttp.ClientSession(headers={"User-Agent": UA}) as session:
        # Definitions (song song)
        wiki_task = fetch_wikipedia_summary(session, kw, lang=lang)
        ddg_task  = fetch_ddg_instant_answer(session, kw)
        wikt_task = fetch_wiktionary_definition(session, kw)
        wd_task   = fetch_wikidata_desc(session, kw, lang=lang)

        (definition, canonical), ddg, wikt, wd = await asyncio.gather(
            wiki_task, ddg_task, wikt_task, wd_task, return_exceptions=True
        )
        if isinstance(definition, Exception): definition, canonical = None, None
        if isinstance(ddg, Exception): ddg = None
        if isinstance(wikt, Exception): wikt = None
        if isinstance(wd, Exception): wd = None

        # Ưu tiên: Wikipedia → Wikidata → DuckDuckGo → Wiktionary
        final_def = definition or wd or ddg or wikt
        canonical_title = canonical or (final_def.get("title") if final_def else None)

        # Images
        images: List[Dict[str, Any]] = []
        if canonical_title:
            imgs_wp = await fetch_wikipedia_images(session, canonical_title, lang, max_images)
            images.extend(imgs_wp)
        if len(images) < max_images:
            imgs_ov = await fetch_openverse_images(session, canonical_title or kw, max_images)
            images.extend(imgs_ov)
        images = _pick_first(images, max_images)

        # News
        news = await fetch_google_news(
            session, kw, max_items=max_news,
            hl=("vi" if lang.startswith("vi") else DEFAULT_NEWS_HL),
            gl=("VN" if lang.startswith("vi") else DEFAULT_NEWS_GL),
            ceid=("VN:vi" if lang.startswith("vi") else DEFAULT_NEWS_CEID),
            window_days=NEWS_WINDOW_DAYS
        )

        return {
            "keyword": kw,
            "lang": lang,
            "fetched_at": _now_iso(),
            "definition": final_def,
            "images": images,
            "news": news,
            "meta": {"canonical_title": canonical_title}
        }

# =======================
# HTML renderer
# =======================
def render_keyword_html(payload: Dict[str, Any]) -> str:
    kw = html.escape(payload.get("keyword", ""))
    defn = payload.get("definition") or {}
    images = payload.get("images") or []
    news = payload.get("news") or []

    if not defn and not images and not news:
        return f"""
        <div style='display: flex; flex-direction: column; align-items: center; justify-content: center; height: 100%; font-family: Segoe UI, sans-serif; color: #DCDDDE; text-align: center; padding: 20px;'>
            <p style='font-size: 48px; margin: 0;'>🤔</p>
            <h3 style='margin-top: 15px;'>Không tìm thấy thông tin</h3>
            <p style='color: #B9BBBE;'>Chúng tôi không thể tìm thấy bất kỳ kết quả nào cho "<b>{kw}</b>".<br>Vui lòng thử một từ khóa khác đầy đủ và rõ ràng hơn.</p>
        </div>
        """

    img_html = "".join(
        f'<a href="{html.escape(i.get("url") or "#")}" target="_blank" rel="noopener">'
        f'<img src="{html.escape(i.get("thumbnail") or "")}" alt="{html.escape(i.get("title") or kw)}" '
        f'style="width:120px;height:120px;object-fit:cover;border-radius:8px;margin:4px;"/></a>'
        for i in images if i.get("thumbnail")
    )
    news_html = "".join(
        f'<li><a href="{html.escape(n.get("url") or "#")}" target="_blank" rel="noopener">{html.escape(n.get("title") or "")}</a>'
        + (f' <span style="color:#777;font-size:12px;">({html.escape(n.get("published") or "")})</span>' if n.get("published") else "")
        + "</li>"
        for n in news
    )

    defn_block = (
        f'<div class="definition"><p>{html.escape(defn.get("extract") or "No definition found.")}</p>'
        + (f'<p><a href="{html.escape(defn.get("url") or "#")}" target="_blank" rel="noopener">Source</a></p>' if defn.get("url") else "")
        + "</div>"
    )

    html_out = f"""
    <div class="kw-info">
      <h3>Results for <span class="keyword">{kw}</span></h3>
      {defn_block}
      {'<h4>Images</h4><div class="images" style="display:flex;flex-wrap:wrap;">'+img_html+'</div>' if img_html else '<p><i>No images found.</i></p>'}
      {'<h4>Latest News</h4><ul class="news">'+news_html+'</ul>' if news_html else '<p><i>No recent news.</i></p>'}
      <hr>
      <small>Fetched at {html.escape(payload.get("fetched_at",""))}</small>
    </div>
    """
    return html_out

# =======================
# Async & Sync API
# =======================
async def aget_info_for_keyword(keyword: str, lang: str = DEFAULT_LANG) -> str:
    data = await fetch_keyword_info(keyword, lang=lang)
    return render_keyword_html(data)

# ---- Robust sync runner (fix Windows "Event loop is closed") ----
class _AsyncLoopRunner:
    def __init__(self):
        # Khuyến nghị dùng Selector loop để tránh Proactor warning
        if sys.platform.startswith("win"):
            try:
                asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())  # type: ignore[attr-defined]
            except Exception:
                pass
        self.loop = asyncio.new_event_loop()
        self.thread = Thread(target=self.loop.run_forever, daemon=True)
        self.thread.start()
        atexit.register(self.close)

    def run(self, coro):
        fut = asyncio.run_coroutine_threadsafe(coro, self.loop)
        return fut.result()  # block sync thread đến khi xong

    def close(self):
        try:
            if self.loop.is_running():
                self.loop.call_soon_threadsafe(self.loop.stop)
            if self.thread.is_alive():
                self.thread.join(timeout=1.0)
            if not self.loop.is_closed():
                self.loop.close()
        except Exception:
            pass

_runner = _AsyncLoopRunner()

def get_info_for_keyword(keyword: str, lang: str = DEFAULT_LANG) -> str:
    """
    Sync wrapper an toàn:
    - Không tạo/đóng event loop mỗi lần (tránh 'Event loop is closed' trên Windows)
    - Thread nền giữ loop chạy, dùng run_coroutine_threadsafe.
    - Trong môi trường async (FastAPI), hãy gọi aget_info_for_keyword(...) và await.
    """
    return _runner.run(aget_info_for_keyword(keyword, lang=lang))