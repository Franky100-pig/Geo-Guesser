#!/usr/bin/env python3
"""pin_title_mine.py — mine baidu reverse-search source pages for place names.

The v3 blind test showed the single highest-yield lever on overseas photos:
baidu reverse search finds near-duplicates on Chinese pin/stock sites
(duitang, huaban, meipian, tuchong, 699pic, veer, sohu, 163, baijiahao...),
and those pins carry the ORIGINAL photo title, which usually names the
place — even when the engine's own tag is a useless generic label.

Usage:
  python3 pin_title_mine.py <run_dir> [more_run_dirs...]
  python3 pin_title_mine.py --json <rev_baidu.json> [more.json...]
  python3 pin_title_mine.py --all /tmp/gg_v3/run_q1 /tmp/gg_v3/run_q2

Input : run dirs containing intake/rev/*_baidu.json and/or rev_vars/*_baidu.json
Output: ranked table  [places] | site | title | url   (strong matches first)

Stdlib only. Respects http_proxy/https_proxy env vars. CN sites are fetched
directly; blocked/JS-walled pages (xiaohongshu) are reported, not retried.
"""
import glob
import json
import os
import re
import sys
import urllib.error
import urllib.request

UA = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"}
TIMEOUT = 8
MAX_URLS = 30

# Pin/stock/blog sites worth fetching (others are usually useless galleries)
PIN_SITES = (
    "duitang.com", "huaban.com", "meipian.cn", "tuchong.com", "699pic.com",
    "veer.com", "hellorf.com", "vcg.com", "sohu.com", "163.com",
    "baijiahao.baidu.com", "sina.com.cn", "weibo.com", "douyin.com",
    "poco.cn", "lofter.com", "dianping.com",
)
BLOCKED_HINT = ("xiaohongshu.com", "douyin.com")

# Country tokens (zh + en). A country hit alone is strong evidence.
COUNTRIES = {
    "中国": "China", "China": "China",
    "台湾": "Taiwan (China)", "Taiwan": "Taiwan (China)", "台北": "Taiwan (China)",
    "香港": "Hong Kong (China)", "Hong Kong": "Hong Kong (China)",
    "澳门": "Macao (China)", "Macao": "Macao (China)",
    "日本": "Japan", "Japan": "Japan", "东京": "Japan", "Tokyo": "Japan", "大阪": "Japan",
    "韩国": "Korea", "Korea": "Korea", "首尔": "Korea", "Seoul": "Korea",
    "蒙古": "Mongolia", "Mongolia": "Mongolia",
    "越南": "Vietnam", "Vietnam": "Vietnam", "胡志明": "Vietnam", "Saigon": "Vietnam", "岘港": "Vietnam",
    "泰国": "Thailand", "Thailand": "Thailand", "曼谷": "Thailand", "Bangkok": "Thailand",
    "缅甸": "Myanmar", "Myanmar": "Myanmar", "Burma": "Myanmar", "仰光": "Myanmar", "茵莱湖": "Myanmar", "莱茵湖": "Myanmar",
    "老挝": "Laos", "Laos": "Laos", "柬埔寨": "Cambodia", "Cambodia": "Cambodia",
    "马来西亚": "Malaysia", "Malaysia": "Malaysia", "吉隆坡": "Malaysia", "Kuala": "Malaysia",
    "新加坡": "Singapore", "Singapore": "Singapore",
    "印尼": "Indonesia", "印度尼西亚": "Indonesia", "Indonesia": "Indonesia", "巴厘": "Indonesia", "Bali": "Indonesia",
    "菲律宾": "Philippines", "Philippines": "Philippines", "马尼拉": "Philippines", "Manila": "Philippines",
    "印度": "India", "India": "India", "孟买": "India", "德里": "India",
    "尼泊尔": "Nepal", "Nepal": "Nepal", "不丹": "Bhutan", "Bhutan": "Bhutan",
    "斯里兰卡": "Sri Lanka", "Sri Lanka": "Sri Lanka",
    "马尔代夫": "Maldives", "Maldives": "Maldives",
    "法国": "France", "France": "France", "巴黎": "France", "Paris": "France",
    "里昂": "France", "马赛": "France", "尼斯": "France",
    "意大利": "Italy", "Italy": "Italy", "罗马": "Italy", "Rome": "Italy", "威尼斯": "Italy", "Venice": "Italy", "米兰": "Italy", "佛罗伦萨": "Italy",
    "西班牙": "Spain", "Spain": "Spain", "巴塞罗那": "Spain", "Barcelona": "Spain", "马德里": "Spain", "马略卡": "Spain", "Mallorca": "Spain", "Palma": "Spain", "塞维利亚": "Spain", "格拉纳达": "Spain",
    "葡萄牙": "Portugal", "Portugal": "Portugal", "里斯本": "Portugal", "Lisbon": "Portugal",
    "德国": "Germany", "Germany": "Germany", "柏林": "Germany", "Berlin": "Germany", "慕尼黑": "Germany", "科隆": "Germany",
    "荷兰": "Netherlands", "Netherlands": "Netherlands", "阿姆斯特丹": "Netherlands", "Amsterdam": "Netherlands",
    "比利时": "Belgium", "Belgium": "Belgium", "布鲁塞尔": "Belgium",
    "瑞士": "Switzerland", "Switzerland": "Switzerland", "苏黎世": "Switzerland",
    "奥地利": "Austria", "Austria": "Austria", "维也纳": "Austria", "Vienna": "Austria",
    "希腊": "Greece", "Greece": "Greece", "雅典": "Greece", "圣托里尼": "Greece", "Santorini": "Greece",
    "土耳其": "Turkey", "Turkey": "Turkey", "伊斯坦布尔": "Turkey", "Istanbul": "Turkey", "卡帕多奇亚": "Turkey",
    "捷克": "Czechia", "布拉格": "Czechia", "Prague": "Czechia",
    "匈牙利": "Hungary", "布达佩斯": "Hungary", "Budapest": "Hungary",
    "波兰": "Poland", "Poland": "Poland", "华沙": "Poland",
    "瑞典": "Sweden", "瑞典": "Sweden", "挪威": "Norway", "Norway": "Norway",
    "丹麦": "Denmark", "Denmark": "Denmark", "芬兰": "Finland", "Finland": "Finland",
    "冰岛": "Iceland", "Iceland": "Iceland",
    "爱尔兰": "Ireland", "Ireland": "Ireland", "都柏林": "Ireland",
    "英国": "UK", "United Kingdom": "UK", "伦敦": "UK", "London": "UK", "曼彻斯特": "UK", "爱丁堡": "UK",
    "苏格兰": "UK", "英格兰": "UK",
    "美国": "USA", "United States": "USA", "纽约": "USA", "New York": "USA", "旧金山": "USA", "洛杉矶": "USA", "Chicago": "USA", "芝加哥": "USA", "西雅图": "USA", "波士顿": "USA", "迈阿密": "USA", "夏威夷": "USA", "加州": "USA", "California": "USA",
    "加拿大": "Canada", "Canada": "Canada", "多伦多": "Canada", "温哥华": "Canada", "Vancouver": "Canada", "Toronto": "Canada",
    "墨西哥": "Mexico", "Mexico": "Mexico", "墨西哥城": "Mexico",
    "古巴": "Cuba", "Cuba": "Cuba", "哈瓦那": "Cuba",
    "秘鲁": "Peru", "Peru": "Peru", "库斯科": "Peru",
    "巴西": "Brazil", "Brazil": "Brazil", "里约": "Brazil",
    "阿根廷": "Argentina", "Argentina": "Argentina", "布宜诺斯艾利斯": "Argentina",
    "智利": "Chile", "Chile": "Chile",
    "摩洛哥": "Morocco", "Morocco": "Morocco", "马拉喀什": "Morocco", "Marrakech": "Morocco",
    "埃及": "Egypt", "Egypt": "Egypt", "开罗": "Egypt",
    "南非": "South Africa", "South Africa": "South Africa", "开普敦": "South Africa",
    "肯尼亚": "Kenya", "Kenya": "Kenya", "内罗毕": "Kenya",
    "坦桑尼亚": "Tanzania", "埃塞俄比亚": "Ethiopia",
    "阿联酋": "UAE", "迪拜": "UAE", "Dubai": "UAE",
    "以色列": "Israel", "约旦": "Jordan", "Petra": "Jordan",
    "俄罗斯": "Russia", "Russia": "Russia", "莫斯科": "Russia", "圣彼得堡": "Russia",
    "乌克兰": "Ukraine", "Australia": "Australia", "澳大利亚": "Australia", "悉尼": "Australia", "墨尔本": "Australia",
    "新西兰": "New Zealand", "New Zealand": "New Zealand",
    "南极": "Antarctica", "北极": "Arctic",
}
# Notable non-country city tokens (strong-ish: city name in a photo title)
CITIES = {
    "三亚": "Sanya", "厦门": "Xiamen", "成都": "Chengdu", "重庆": "Chongqing",
    "西安": "Xi'an", "丽江": "Lijiang", "大理": "Dali", "香格里拉": "Shangri-La",
    "桂林": "Guilin", "阳朔": "Yangsho", "张家界": "Zhangjiajie", "黄山": "Huangshan",
    "杭州": "Hangzhou", "苏州": "Suzhou", "南京": "Nanjing", "北京": "Beijing",
    "上海": "Shanghai", "广州": "Guangzhou", "深圳": "Shenzhen", "潮汕": "Chaoshan",
    "泉州": "Quanzhou", "漳州": "Zhangzhou", "莆田": "Putian", "温州": "Wenzhou",
    "台州": "Taizhou", "宁波": "Ningbo", "绍兴": "Shaoxing", "金华": "Jinhua",
    "梧棲": "Wuqi, Taichung (Taiwan, China)", "梧栖": "Wuqi, Taichung (Taiwan, China)",
    "淡水": "Tamsui (Taiwan, China)", "九份": "Jiufen (Taiwan, China)",
    "垦丁": "Kenting (Taiwan, China)", "花莲": "Hualien (Taiwan, China)",
    "清迈": "Chiang Mai", "普吉": "Phuket", "甲米": "Krabi",
    "会安": "Hoi An", "芽庄": "Nha Trang", "富国岛": "Phu Quoc",
    "蒲甘": "Bagan", "曼德勒": "Mandalay", "仰光": "Yangon",
    "吴哥": "Angkor", "暹粒": "Siem Reap",
    "长滩": "Boracay", "宿务": "Cebu", "薄荷岛": "Bohol",
    "巴厘岛": "Bali", "日惹": "Yogyakarta", "龙目岛": "Lombok",
    "槟城": "Penang", "马六甲": "Malacca", "亚庇": "Kota Kinabalu",
    "哈尔施塔特": "Hallstatt", "新天鹅堡": "Neuschwanstein", "五渔村": "Cinque Terre",
    "圣家堂": "Sagrada Familia", "托莱多": "Toledo",
}
# Generic place-suffix patterns: weak hints on their own
SUFFIX = re.compile(r"(市场|渔港|鱼市|老街|小巷|古城|港口|码头|海滩|海岛|湖泊|湖|寺|教堂|广场|大道|大街|街|巷|村|镇|岛|省|市|县|区)")
GENERIC_TAGS = {"城市街道", "狭窄的街道", "老街小巷", "鱼市场", "菜市场", "菜市场摊贩", "鱼贩子", "街头"}


def collect_json(args):
    jsons = []
    for a in args:
        if a.endswith(".json"):
            jsons += [a]
        else:
            jsons += sorted(glob.glob(os.path.join(a, "intake", "rev", "*_baidu.json")))
            jsons += sorted(glob.glob(os.path.join(a, "rev_vars", "*_baidu.json")))
    return jsons


def load_sources(jsons):
    """Return ordered unique (site, url, variant) with pin sites first."""
    seen, out = set(), []
    for j in jsons:
        try:
            d = json.load(open(j))
        except Exception:
            continue
        variant = os.path.basename(j).replace("_baidu.json", "")
        for it in (d.get("similar") or []):
            url = it.get("from") or it.get("url") or ""
            site = it.get("site") or ""
            if not url or url in seen:
                continue
            seen.add(url)
            pin = any(p in site or p in url for p in PIN_SITES)
            out.append((0 if pin else 1, site, url, variant))
    out.sort(key=lambda x: x[0])
    return out[:MAX_URLS]


def fetch_title(url):
    """Fetch a page and extract its title. Returns (title, status)."""
    try:
        req = urllib.request.Request(url, headers=UA)
        with urllib.request.urlopen(req, timeout=TIMEOUT) as r:
            raw = r.read(400_000)
        for enc in ("utf-8", "gb18030"):
            try:
                html = raw.decode(enc)
                break
            except UnicodeDecodeError:
                continue
        else:
            html = raw.decode("utf-8", "ignore")
        m = (re.search(r'<meta[^>]+property=["\']og:title["\'][^>]+content=["\']([^"\']+)', html, re.I)
             or re.search(r'<meta[^>]+content=["\']([^"\']+)["\'][^>]+property=["\']og:title', html, re.I)
             or re.search(r"<title[^>]*>(.*?)</title>", html, re.S | re.I))
        if not m:
            return "", "no-title"
        title = re.sub(r"\s+", " ", m.group(1)).strip()
        return title, "ok"
    except urllib.error.HTTPError as e:
        return "", f"http-{e.code}"
    except Exception as e:
        return "", type(e).__name__


def scan_places(title):
    """Return (strong_places, weak_hits)."""
    strong, weak = [], []
    for tok, canon in {**COUNTRIES, **CITIES}.items():
        if tok in title and canon not in strong:
            strong.append(canon)
    m = SUFFIX.search(title)
    if m and not strong:
        weak.append(f"place-suffix:{m.group(1)}")
    return strong, weak


def main():
    args = sys.argv[1:]
    if args and args[0] == "--json":
        jsons = args[1:]
    else:
        jsons = collect_json(args)
    if not jsons:
        print(__doc__)
        return 1
    sources = load_sources(jsons)
    print(f"== pin_title_mine: {len(sources)} unique source pages from {len(jsons)} rev jsons ==")
    rows = []
    for _, site, url, variant in sources:
        title, status = fetch_title(url)
        if status != "ok" or not title:
            note = "BLOCKED/JS-wall" if any(b in url for b in BLOCKED_HINT) else status
            print(f"  [skip] {site:28s} {note:16s} {url[:80]}")
            continue
        strong, weak = scan_places(title)
        rows.append((strong, weak, site, title, url))
    rows.sort(key=lambda r: (not r[0], len(r[1]) == 0))
    print("\n== ranked titles ==")
    for strong, weak, site, title, url in rows:
        tag = f"[{'/'.join(strong)}]" if strong else ("[weak]" if weak else "[no-place]")
        print(f"{tag:28s} {site:22s} {title[:70]}")
        print(f"{'':30s}{url[:100]}")
    strong_rows = [r for r in rows if r[0]]
    print(f"\n== summary: {len(rows)} titles fetched, {len(strong_rows)} with place names ==")
    if strong_rows:
        print("CANDIDATE PLACES:", ", ".join(sorted({p for r in strong_rows for p in r[0]})))
    return 0


if __name__ == "__main__":
    sys.exit(main())
