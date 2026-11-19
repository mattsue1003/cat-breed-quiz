# 依挑選結果下載每個品種的第 2、3 張照片（Commons 1000px 縮圖），寫進 data/media.js 的 more 欄位
# 用法: python3 -I tools/addmore.py <cands.json>
import json, sys, os, subprocess, time
UA = "CatBreedQuizBuilder/1.0 (educational teaching page)"
PICK = dict(mix=[4,9], american=[4,9], british=[2,8], persian=[4,9], siamese=[0,7], ragdoll=[1,3], mainecoon=[1,7],
 fold=[7,10], russian=[5,8], bengal=[2,6], sphynx=[3,5], munchkin=[0,7], abyssinian=[0,2], norwegian=[2,5],
 exotic=[4,0], bobtail=[2,4], devon=[0,4], angora=[3,9], siberian=[1,8], mau=[2,10])
c = json.load(open(sys.argv[1]))
root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
src = open(os.path.join(root, "data/media.js"), encoding="utf-8").read()
head, body = src.split("window.MEDIA=", 1)
mjson, rest = body.split("\n};", 1)
M = json.loads(mjson + "\n}")
for k, idx in PICK.items():
    more = []
    for n, i in enumerate(idx, start=2):
        p = c[k][i]; f = os.path.join(root, f"assets/img/{k}-{n}.jpg")
        for t in range(4):
            if os.path.exists(f) and os.path.getsize(f) > 5000: break
            subprocess.run(["curl", "-s", "-L", "-A", UA, "-o", f, p["thumb"]]); time.sleep(1 + 3*t)
        more.append(dict(author=p["author"], lic=p["lic"], licurl=p["licurl"], page=p["page"]))
    M[k]["more"] = more
open(os.path.join(root, "data/media.js"), "w", encoding="utf-8").write(head + "window.MEDIA=" + json.dumps(M, ensure_ascii=False, indent=1) + ";" + rest)
print("done", len(PICK))
