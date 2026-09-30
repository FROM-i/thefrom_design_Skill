#!/usr/bin/env python3
"""method/ 의 방법론 원본에서 스킬의 references/ 를 다시 만든다.

방법론을 고칠 때는 method/ 만 고치고 이 스크립트를 실행한다.
references/ 를 직접 고치지 않는다 — 다음 빌드에서 덮어써진다.

    python3 scripts/build_references.py          # 다시 만들기
    python3 scripts/build_references.py --check  # 원본과 어긋났는지 확인만 (CI용)
"""
import re, sys, pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
SRC = ROOT / "method"
DST = ROOT / "plugins" / "thefrom-ux" / "skills" / "thefrom-ux" / "references"

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


def page(title, body, src):
    return f"# {title}\n\n" + NOTE.format(src=src) + toc(body) + body


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


def main():
    files = build()
    if "--check" in sys.argv:
        stale = [n for n, t in files.items()
                 if not (DST / n).exists() or (DST / n).read_text(encoding="utf-8") != t]
        if stale:
            print("references/ 가 method/ 와 어긋났습니다:", ", ".join(stale))
            print("python3 scripts/build_references.py 를 실행하고 커밋하세요.")
            sys.exit(1)
        print("references/ 최신 상태입니다.")
        return
    DST.mkdir(parents=True, exist_ok=True)
    for n, t in files.items():
        (DST / n).write_text(t, encoding="utf-8")
        print(f"  {n}  {len(t.splitlines())}줄")
    print("완료. 방법론을 바꿨다면 plugin.json 의 version 을 올리세요.")


if __name__ == "__main__":
    main()
