#!/usr/bin/env python3
"""method/ 의 방법론 원본에서 스킬의 references/ 와 portable/knowledge/ 를 다시 만든다.

방법론을 고칠 때는 method/ 만 고치고 이 스크립트를 실행한다.
references/ 를 직접 고치지 않는다 — 다음 빌드에서 덮어써진다.

    python3 scripts/build_references.py          # 다시 만들기
    python3 scripts/build_references.py --check  # 원본과 어긋났는지 확인만 (CI용)
"""
import re, sys, pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
SRC = ROOT / "method"
SKILL = ROOT / "plugins" / "thefrom-ux" / "skills" / "thefrom-ux"
DST = SKILL / "references"
PORTABLE = ROOT / "portable" / "knowledge"   # GPT·Gemini 등 다른 AI에 올릴 지식 파일

NOTE = ("> **스킬 참조본 — 자동 생성 파일. 직접 고치지 말 것.** 원본: `method/{src}`. "
        "방법론을 고칠 때는 원본을 고치고 `python3 scripts/build_references.py`를 실행한다.\n\n")


def read(name):
    return (SRC / name).read_text(encoding="utf-8")


def toc(body):
    out = ["## 목차", ""]
    for line in body.splitlines():
        m = re.match(r"^(#{2,3}) (.+)$", line)
        if m and not line.startswith("## 목차"):
            out.append("  " * (len(m.group(1)) - 2) + "- " + m.group(2).strip())
    return "\n".join(out) + "\n\n---\n\n"


def neutral(text):
    """스킬은 Claude·ChatGPT·Codex 등 여러 AI에서 돈다 — 참조본에서는 특정 모델 이름을 'AI'로 바꾼다.
    원본 method/ 는 그대로 두고, 개정 이력 표(| 2026…)는 기록이므로 바꾸지 않는다."""
    return "\n".join(l if l.startswith("| 20") else l.replace("Claude", "AI")
                     for l in text.split("\n"))


def page(title, body, src):
    return f"# {title}\n\n" + NOTE.format(src=src) + toc(neutral(body)) + neutral(body)


def build():
    core = read("0_CORE_철학과_판단기준.md")
    pipe = read("1_PIPELINE_실행절차.md")
    qna = read("3_QNA_질문노드.md")
    cat = read("2_CATALOG_기성의_관점.md")
    iA, iB, iD, iC = (cat.index(k) for k in ("# PART A", "# PART B", "# PART D", "# PART C"))
    head, partA, partB, partD, partC = cat[:iA], cat[iA:iB], cat[iB:iD], cat[iD:iC], cat[iC:]
    strip = lambda t: t.split("\n", 1)[1]
    return {
        "core.md": page("L0 · CORE — 철학과 판단 기준", strip(core), "0_CORE_철학과_판단기준.md"),
        "pipeline.md": page("L1 · PIPELINE — 실행 절차", strip(pipe), "1_PIPELINE_실행절차.md"),
        "qna.md": page("L1-Q · QNA — 질문 노드", strip(qna), "3_QNA_질문노드.md"),
        "catalog-ism.md": page("L2 CATALOG · PART A — 역사적 사조 `ISM-*`", strip(head) + partA, "2_CATALOG_기성의_관점.md"),
        "catalog-form.md": page("L2 CATALOG · PART B — 조형 어휘", partB + partC, "2_CATALOG_기성의_관점.md"),
        "catalog-pattern.md": page("L2 CATALOG · PART D — UI 패턴·모션·상태", partD, "2_CATALOG_기성의_관점.md"),
    }


def portable(files):
    out = dict(files)
    out["proto-base.html"] = (SKILL / "assets" / "proto-base.html").read_text(encoding="utf-8")
    out["brief-template.md"] = (SKILL / "assets" / "brief-template.md").read_text(encoding="utf-8")
    return out


PLUGIN = ROOT / "plugins" / "thefrom-ux"
MANIFESTS = [PLUGIN / "plugin.json", PLUGIN / ".claude-plugin" / "plugin.json"]


def check_manifests():
    """범용(plugin.json)과 Claude(.claude-plugin/plugin.json) 매니페스트의 이름·버전이 같은지 본다."""
    import json
    seen = {str(m.relative_to(ROOT)): json.loads(m.read_text(encoding="utf-8")) for m in MANIFESTS}
    keys = {(d.get("name"), d.get("version")) for d in seen.values()}
    if len(keys) != 1:
        print("매니페스트 이름·버전이 어긋났습니다:", {k: (d.get("name"), d.get("version")) for k, d in seen.items()})
        return False
    return True


def main():
    files = build()
    port = portable(files)
    if "--check" in sys.argv:
        stale = [n for n, t in files.items()
                 if not (DST / n).exists() or (DST / n).read_text(encoding="utf-8") != t]
        stale += ["portable/" + n for n, t in port.items()
                  if not (PORTABLE / n).exists() or (PORTABLE / n).read_text(encoding="utf-8") != t]
        ok = check_manifests()
        if stale:
            print("references/ 가 method/ 와 어긋났습니다:", ", ".join(stale))
            print("python3 scripts/build_references.py 를 실행하고 커밋하세요.")
            sys.exit(1)
        if not ok:
            sys.exit(1)
        print("references/ 최신 상태입니다. 매니페스트 버전 일치.")
        return
    DST.mkdir(parents=True, exist_ok=True)
    for n, t in files.items():
        (DST / n).write_text(t, encoding="utf-8")
        print(f"  {n}  {len(t.splitlines())}줄")
    PORTABLE.mkdir(parents=True, exist_ok=True)
    for n, t in port.items():
        (PORTABLE / n).write_text(t, encoding="utf-8")
    print(f"  portable/knowledge/ {len(port)}개")
    print("완료. 방법론을 바꿨다면 plugin.json 두 곳(plugin.json, .claude-plugin/plugin.json)의 version 을 함께 올리세요.")


if __name__ == "__main__":
    main()
