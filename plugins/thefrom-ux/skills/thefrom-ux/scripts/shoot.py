#!/usr/bin/env python3
"""프로토타입 화면을 375×812로 캡처하고 콘솔 오류를 보고한다 — 크리틱 루프용.

기본: 모든 화면(.screen[data-screen])을 go()로 열어 한 장씩 찍는다.
    python3 shoot.py proto/B.html shots/B-r1
    python3 shoot.py proto/final.html shots/wire  --mode wire    # G6① 무채색 와이어
    python3 shoot.py proto/final.html shots/still --mode still   # G6② 정지 화면

조작 중인 상태를 찍으려면 --steps 로 동작 목록(JSON)을 준다. 이때는 목록에 적은 것만 찍는다.
    python3 shoot.py proto/B.html shots/B-states --steps steps.json

steps.json 예:
    [
      {"go": "quiz"},
      {"click": "#opt-2"}, {"wait": 400},
      {"click": "text=다음"},
      {"shot": "quiz-q2"},
      {"eval": "openSheet()"}, {"wait": 500}, {"shot": "sheet"},
      {"fill": ["#comment", "좋아요"]}, {"press": "Enter"}, {"shot": "comment-sent"}
    ]
동작: go(화면 id) · click(CSS 선택자 또는 text=문구) · fill([선택자, 값]) · press(키)
      · wait(ms) · eval(JS) · mode(normal|wire|still) · shot(파일 이름)

proto-base.html 구조(.screen[data-screen], go(), 판정 키트 모드)를 전제로 한다.
Playwright가 없으면: pip install playwright (브라우저가 이미 있으면 install 생략)
"""
import sys, os, json, argparse, asyncio, pathlib

async def set_mode(pg, mode):
    await pg.evaluate(f"document.querySelector('[data-set-mode=\"{mode}\"]')?.click()")

async def main(a):
    from playwright.async_api import async_playwright
    out = pathlib.Path(a.out); out.mkdir(parents=True, exist_ok=True)
    url = pathlib.Path(a.html).resolve().as_uri()
    errors, shots = [], 0
    async with async_playwright() as p:
        exe = os.environ.get("CHROMIUM_PATH") or "/opt/pw-browsers/chromium"
        try:
            b = await p.chromium.launch(**({"executable_path": exe} if os.path.isfile(exe) else {}))
        except Exception:
            b = await p.chromium.launch()
        pg = await b.new_page(viewport={"width": 420, "height": 900}, device_scale_factor=2)
        pg.on("pageerror", lambda e: errors.append(f"pageerror: {e}"))
        pg.on("console", lambda m: errors.append(f"console.{m.type}: {m.text}") if m.type == "error" else None)
        await pg.goto(url); await pg.wait_for_timeout(400)
        if a.mode != "normal":
            await set_mode(pg, a.mode)

        async def shot(name):
            nonlocal shots
            shots += 1
            frame = await pg.query_selector(".frame")
            await (frame or pg).screenshot(path=str(out / f"{shots:02d}_{name}.png"))

        if a.steps:
            steps = json.loads(pathlib.Path(a.steps).read_text(encoding="utf-8"))
            for i, st in enumerate(steps, 1):
                try:
                    if "go" in st:      await pg.evaluate(f"go({st['go']!r})"); await pg.wait_for_timeout(a.wait)
                    elif "click" in st: await pg.click(st["click"], timeout=3000)
                    elif "fill" in st:  await pg.fill(st["fill"][0], st["fill"][1], timeout=3000)
                    elif "press" in st: await pg.keyboard.press(st["press"])
                    elif "wait" in st:  await pg.wait_for_timeout(int(st["wait"]))
                    elif "eval" in st:  await pg.evaluate(st["eval"])
                    elif "mode" in st:  await set_mode(pg, st["mode"])
                    elif "shot" in st:  await shot(st["shot"])
                except Exception as e:
                    errors.append(f"step {i} {st}: {e}")
        else:
            ids = await pg.evaluate("[...document.querySelectorAll('.screen')].map(s=>s.dataset.screen)")
            for sid in ids:
                await pg.evaluate(f"go({sid!r})"); await pg.wait_for_timeout(a.wait)
                await shot(sid)
        await b.close()
    print(f"{shots}장 → {out}")
    print("오류 없음" if not errors else "오류:\n  " + "\n  ".join(errors))
    sys.exit(1 if errors else 0)

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("html"); ap.add_argument("out")
    ap.add_argument("--mode", default="normal", choices=["normal", "wire", "still"])
    ap.add_argument("--steps", help="동작 목록 JSON 파일")
    ap.add_argument("--wait", type=int, default=600, help="화면 진입 후 대기 ms")
    asyncio.run(main(ap.parse_args()))
