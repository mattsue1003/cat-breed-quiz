# 每個品種找額外照片候選：Commons 搜尋，篩授權（CC BY/BY-SA/CC0/PD）、尺寸、排除插畫標本等
# 用法: python3 -I tools/cands.py tools/cats.tsv outdir
import json, sys, re, subprocess, html, os, time
UA = "CatBreedQuizBuilder/1.0 (educational teaching page)"
OK = re.compile(r"^(CC BY(-SA)? [0-9.]+|CC0|Public domain|PD.*)$", re.I)
BAD = re.compile(r"skull|skelet|museum|taxiderm|stuffed|illustr|drawing|_map|stamp|coin|logo|diagram|sketch|painting|statue|sculpture|toy|plush|poster|cartoon|show_ring|cage|x-ray|surgery|dead", re.I)
rows = [l.rstrip("\n").split("\t") for l in open(sys.argv[1], encoding="utf-8")]
out = sys.argv[2]; os.makedirs(out, exist_ok=True)
res = {}
for key, name, qs, cur in rows:
    seen = {cur.replace(" ", "_")}; picks = []
    for q in qs.split("|"):
        args = ["curl", "-s", "-A", UA, "-G", "https://commons.wikimedia.org/w/api.php",
                "--data-urlencode", "gsrsearch=" + q + " filetype:bitmap",
                "-d", "action=query", "-d", "generator=search", "-d", "gsrnamespace=6", "-d", "gsrlimit=40",
                "-d", "prop=imageinfo", "-d", "iiprop=url|extmetadata|size", "-d", "iiurlwidth=1000", "-d", "format=json"]
        d = {}
        for t in range(4):
            r = subprocess.run(args, capture_output=True, text=True).stdout
            try: d = json.loads(r); break
            except Exception: time.sleep(6)
        for p in sorted(d.get("query", {}).get("pages", {}).values(), key=lambda p: p.get("index", 0)):
            ii = p["imageinfo"][0]; m = ii.get("extmetadata", {})
            g = lambda k: re.sub("<[^>]+>", "", html.unescape(m.get(k, {}).get("value", ""))).strip()
            fn = p["title"][5:].replace(" ", "_")
            if fn in seen or BAD.search(fn) or not fn.lower().endswith((".jpg", ".jpeg")): continue
            if min(ii["width"], ii["height"]) < 700: continue
            lic = g("LicenseShortName")
            if not OK.match(lic): continue
            seen.add(fn)
            picks.append(dict(file=fn, thumb=ii["thumburl"], w=ii["width"], h=ii["height"], author=g("Artist")[:60] or "Unknown",
                              lic=lic, licurl=m.get("LicenseUrl", {}).get("value", ""), page=ii["descriptionurl"]))
        time.sleep(1.5)
        if len(picks) >= 12: break
    res[key] = picks[:12]
    print(key, len(res[key]), flush=True)
json.dump(res, open(os.path.join(out, "cands.json"), "w"), ensure_ascii=False, indent=1)
