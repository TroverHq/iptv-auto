#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""整理 iptv.json：剔除本机代理地址(127.0.0.1) + 统一分类。原地写回 out/iptv.json"""
import sys

SRC = "out/iptv.json"

ORDER = ["央视", "卫视", "体育", "影视国际", "少儿教育", "文旅景观", "地方台", "其他"]
MAP = {
    "央视": "央视", "央视频": "央视", "央视景观": "央视", "iPanda": "央视",
    "卫视": "卫视", "体育": "体育",
    "影视": "影视国际", "国际": "影视国际", "韩国": "影视国际", "日本": "影视国际",
    "新加坡": "影视国际", "香港": "影视国际", "澳门": "影视国际", "台湾": "影视国际",
    "少儿": "少儿教育", "教育": "少儿教育", "宠物": "少儿教育",
    "文旅": "文旅景观",
}
PROV = set("""江苏 安徽 四川 辽宁 甘肃 广东 贵州 广西 福建 吉林 江西
黑龙江 海南 河南 浙江 山东 内蒙古 山西 陕西 天津 青海 宁夏 新疆 西藏
云南 上海 湖南 台湾""".split())

def bucket(g):
    g = g.strip()
    if g in MAP:
        return MAP[g]
    if g.endswith("景观") or g.endswith("风景"):
        return "文旅景观"
    if g in PROV:
        return "地方台"
    return "其他"

def main():
    lines = open(SRC, encoding="utf-8", errors="replace").read().splitlines()
    cats = {k: [] for k in ORDER}
    cur = "其他"
    kept = 0
    dropped = 0
    for ln in lines:
        ln = ln.strip()
        if not ln:
            continue
        if ln.endswith("#genre#"):
            cur = bucket(ln.replace("#genre#", "").rstrip(","))
            continue
        # 频道行的形态是 "名称,URL"：URL 在后半段，别用 startswith 判断
        if "," in ln and ("http://" in ln or "https://" in ln or "rtmp://" in ln):
            if "://127.0.0.1" in ln:
                dropped += 1
                continue
            name, url = ln.split(",", 1)
            cats[cur].append(name.strip() + "," + url.strip())
            kept += 1
    if kept == 0:
        print("::error::整理后无任何直连频道，中止推送")
        sys.exit(1)
    out = []
    for c in ORDER:
        if cats[c]:
            out.append(c + ",#genre#")
            out.extend(cats[c])
    open(SRC, "w", encoding="utf-8").write("\n".join(out) + "\n")
    used = [c for c in ORDER if cats[c]]
    print("kept=%d dropped=%d" % (kept, dropped))
    print("分类: " + ", ".join("%s=%d" % (c, len(cats[c])) for c in used))

if __name__ == "__main__":
    main()
