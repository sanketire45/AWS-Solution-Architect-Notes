#!/usr/bin/env python3
"""
inject_nav.py — add a slide-out chapter navigator to every AWS Masterclass HTML page.

- Non-destructive: it only inserts a self-contained block before </body>.
- Idempotent: re-running replaces the previous block (so you can re-run after adding pages).
- Theme-matched: the panel reuses each page's own CSS variables (--paper, --ink, --accent, --rule)
  with sensible fallbacks, so it looks native on every page.

Usage:
    python3 inject_nav.py            # inject into every .html under this folder
    python3 inject_nav.py --revert   # remove the injected nav from every page
"""
import os
import re
import sys
from pathlib import Path
from urllib.parse import quote

ROOT = Path(__file__).resolve().parent
START = "<!-- CHAPTER_NAV_START -->"
END = "<!-- CHAPTER_NAV_END -->"

# service-folder display order + friendly labels
ORDER = ["01_IAM", "02_EC2", "03_ELB_ASG", "04_RDS_Aurora_ElastiCache", "05_Route_53", "06_S3",
         "15_CloudFront_Global_Accelerator", "16_AWS_Storage_Extras",
         "17_Decoupling_SQS_SNS_Kinesis_MQ", "18_Containers_ECS_Fargate_ECR_EKS",
         "19_Serverless_Lambda_DynamoDB_APIGW_Cognito", "20_Serverless_Architecture_Patterns",
         "21_Databases_in_AWS", "22_Data_and_Analytics", "23_Machine_Learning", "24_Monitoring_CloudWatch_CloudTrail_Config", "25_IAM_Advanced", "26_Security_Encryption", "27_Networking_VPC", "28_DR_and_Migrations"]
LABELS = {
    "01_IAM": "S01 · IAM",
    "02_EC2": "S02 · EC2",
    "03_ELB_ASG": "S03 · ELB & ASG",
    "04_RDS_Aurora_ElastiCache": "S04 · RDS · Aurora · ElastiCache",
    "05_Route_53": "S05 · Route 53",
    "06_S3": "S06 · S3",
    "15_CloudFront_Global_Accelerator": "S15 · CloudFront & Global Accelerator",
    "16_AWS_Storage_Extras": "S16 · AWS Storage Extras",
    "17_Decoupling_SQS_SNS_Kinesis_MQ": "S17 · Decoupling (SQS/SNS/Kinesis/MQ)",
    "18_Containers_ECS_Fargate_ECR_EKS": "S18 · Containers (ECS/Fargate/ECR/EKS)",
    "19_Serverless_Lambda_DynamoDB_APIGW_Cognito": "S19 · Serverless (Lambda/DynamoDB/API GW/Cognito)",
    "20_Serverless_Architecture_Patterns": "S20 · Serverless Architectures",
    "21_Databases_in_AWS": "S21 · Databases in AWS",
    "22_Data_and_Analytics": "S22 · Data & Analytics",
    "23_Machine_Learning": "S23 · Machine Learning",
    "24_Monitoring_CloudWatch_CloudTrail_Config": "S24 · Monitoring & Audit",
    "25_IAM_Advanced": "S25 · IAM Advanced",
    "26_Security_Encryption": "S26 · Security & Encryption",
    "27_Networking_VPC": "S27 · Networking (VPC)",
    "28_DR_and_Migrations": "S28 · DR & Migrations",
}


def doc_name(p: Path) -> str:
    n = re.sub(r"(?i)\bcopy\b", "", p.stem)
    n = re.sub(r"^\d+[_\-\s]*", "", n)          # drop leading 01_ / 02-
    n = n.replace("_", " ").replace("-", " ")
    n = re.sub(r"\s+", " ", n).strip()
    return n or p.stem


def collect():
    files = []
    for p in sorted(ROOT.rglob("*.html")):
        if p.name == "index.html":
            continue
        if " copy" in p.name.lower():            # skip duplicate "copy" files
            continue
        files.append(p)

    groups = {}
    for p in files:
        top = p.relative_to(ROOT).parts[0]
        groups.setdefault(top, []).append(p)

    ordered = [g for g in ORDER if g in groups] + [g for g in groups if g not in ORDER]

    def order_key(p):
        # masterclass/concepts first, supplementary next, exam/cracker/crusher last
        n = p.name.lower()
        if any(k in n for k in ("exam", "cracker", "crusher")):
            pri = 2
        elif any(k in n for k in ("masterclass", "concepts")):
            pri = 0
        else:
            pri = 1
        return (pri, n)

    return [(g, sorted(groups[g], key=order_key)) for g in ordered]


CSS = """
<style id="cnav-style">
.cnav-btn{position:fixed;top:16px;left:16px;z-index:9998;display:flex;align-items:center;justify-content:center;
  font-size:19px;line-height:1;cursor:pointer;width:44px;height:44px;padding:0;
  background:var(--accent,#8B2635);color:#fff;border:none;border-radius:11px;
  box-shadow:0 3px 12px rgba(0,0,0,.18);opacity:.9;transition:opacity .15s,transform .15s;}
.cnav-btn:hover{opacity:1;transform:translateY(-1px);}
.cnav-overlay{position:fixed;inset:0;background:rgba(20,16,10,.38);opacity:0;visibility:hidden;
  transition:opacity .2s;z-index:9998;}
body.cnav-open .cnav-overlay{opacity:1;visibility:visible;}
.cnav-panel{position:fixed;top:0;left:0;height:100vh;width:312px;max-width:86vw;z-index:9999;
  background:var(--paper,#fffcf5);color:var(--ink,#1b1b26);border-right:1px solid var(--rule,#d9cdb4);
  box-shadow:6px 0 26px rgba(0,0,0,.16);transform:translateX(-100%);transition:transform .24s ease;
  overflow-y:auto;font-family:'Source Serif 4',Georgia,serif;}
body.cnav-open .cnav-panel{transform:none;}
.cnav-head{display:flex;align-items:center;justify-content:space-between;
  padding:22px 22px 16px;border-bottom:1px solid var(--rule,#d9cdb4);}
.cnav-title{font:700 19px/1.2 'Fraunces','Source Serif 4',serif;color:var(--accent,#8B2635);
  letter-spacing:.01em;}
.cnav-x{background:none;border:none;font-size:24px;line-height:1;cursor:pointer;color:var(--ink-mute,#6b6b7a);}
.cnav-x:hover{color:var(--accent,#8B2635);}
.cnav-group{padding:20px 14px 4px;}
.cnav-glabel{font:700 19px/1.2 'Fraunces','Source Serif 4',serif;letter-spacing:.01em;
  color:var(--accent,#8B2635);padding:0 10px 9px;}
.cnav-glabel.cnav-gcurrent{background:var(--bg-alt,#efe7d6);border-radius:9px;
  padding:7px 10px;margin-bottom:4px;box-shadow:inset 3px 0 0 var(--accent,#8B2635);}
.cnav-panel ul{list-style:none;margin:0;padding:0;}
.cnav-panel li{margin:1px 0;}
.cnav-panel li a{display:block;text-decoration:none;color:var(--ink-soft,#3c3c4a);
  font-size:14.5px;line-height:1.4;padding:7px 12px;border-radius:8px;border-left:3px solid transparent;
  transition:background .15s,color .15s,border-color .15s;}
.cnav-panel li a:hover{background:var(--bg-alt,#efe7d6);color:var(--accent,#8B2635);}
.cnav-panel li.cnav-current a{background:var(--accent,#8B2635);border-left-color:var(--accent,#8B2635);
  color:#fff;font-weight:700;}
.cnav-foot{padding:16px 22px 30px;color:var(--ink-mute,#6b6b7a);
  font:400 12.5px/1.4 'Inter',system-ui,sans-serif;}
</style>
"""

JS = """
<script id="cnav-js">
(function(){
  var open=function(){document.body.classList.add('cnav-open');};
  var close=function(){document.body.classList.remove('cnav-open');};
  var toggle=function(){document.body.classList.toggle('cnav-open');};
  var b=document.querySelector('.cnav-btn'); if(b)b.addEventListener('click',toggle);
  var o=document.querySelector('.cnav-overlay'); if(o)o.addEventListener('click',close);
  var x=document.querySelector('.cnav-x'); if(x)x.addEventListener('click',close);
  document.addEventListener('keydown',function(e){if(e.key==='Escape')close();
    if(e.key==='\\\\'){e.preventDefault();toggle();}});
})();
</script>
"""


def build_nav(current: Path, groups) -> str:
    parts = [
        '<button class="cnav-btn" aria-label="Chapters" title="Chapters (\\)">&#9776;</button>',
        '<div class="cnav-overlay"></div>',
        '<nav class="cnav-panel" aria-label="All chapters">',
        '<div class="cnav-head"><span class="cnav-title">AWS Masterclass</span>'
        '<button class="cnav-x" aria-label="Close">&times;</button></div>',
    ]
    total = 0
    for folder, files in groups:
        gcur = " cnav-gcurrent" if any(f == current for f in files) else ""
        parts.append('<div class="cnav-group">')
        parts.append(f'<div class="cnav-glabel{gcur}">{LABELS.get(folder, folder)}</div>')
        parts.append("<ul>")
        for f in files:
            total += 1
            rel = os.path.relpath(f, start=current.parent)
            href = quote(rel)
            cur = " cnav-current" if f == current else ""
            parts.append(f'<li class="{cur.strip()}"><a href="{href}">{doc_name(f)}</a></li>')
        parts.append("</ul></div>")
    parts.append(f'<div class="cnav-foot">{total} chapters · press \\ to toggle</div>')
    parts.append("</nav>")
    return CSS + "\n".join(parts) + JS


def strip_block(text: str) -> str:
    return re.sub(re.escape(START) + r".*?" + re.escape(END), "", text, flags=re.S).rstrip() + "\n"


def inject(path: Path, groups, revert=False):
    text = path.read_text(encoding="utf-8", errors="ignore")
    text = strip_block(text)
    if revert:
        path.write_text(text, encoding="utf-8")
        return "reverted"
    block = f"{START}\n{build_nav(path, groups)}\n{END}\n"
    if "</body>" in text:
        idx = text.rfind("</body>")
        text = text[:idx] + block + text[idx:]
    else:
        text += block
    path.write_text(text, encoding="utf-8")
    return "injected"


def main():
    revert = "--revert" in sys.argv
    groups = collect()
    targets = [p for _, fs in groups for p in fs]
    for p in targets:
        status = inject(p, groups, revert=revert)
        print(f"{status:9} {p.relative_to(ROOT)}")
    print(f"\n{'reverted' if revert else 'done'}: {len(targets)} pages")


if __name__ == "__main__":
    main()
