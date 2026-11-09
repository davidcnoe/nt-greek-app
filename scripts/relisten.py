"""Write a short review page holding only the clips David asked to hear again (David, 2026-11-05:
"when you repopulate chrome, only give the relistens not whole list").

    python relisten.py ../audio/clips/take_NN 1004 1012 ...

Reads the take's review.html (written by split_audio.py), keeps the rows with those line numbers,
and writes relisten.html beside it, with the same player. Run after re-cutting the take.
"""
import json
import re
import sys
from pathlib import Path


def main():
    if len(sys.argv) < 3:
        sys.exit(__doc__)
    folder, wanted = Path(sys.argv[1]), set(sys.argv[2:])
    page = (folder / "review.html").read_text(encoding="utf-8")
    m = re.search(r"const items = (\[.*?\]);", page, re.S)
    items = [it for it in json.loads(m.group(1)) if it.get("n") in wanted]
    missing = wanted - {it["n"] for it in items}
    if missing:
        sys.exit(f"not in this take: {', '.join(sorted(missing))}")
    page = page[: m.start(1)] + json.dumps(items, ensure_ascii=False) + page[m.end(1):]
    page = page.replace("<h1>Tertius audio: clip review</h1>", "<h1>Tertius audio: clips to hear again</h1>")
    page = re.sub(r'<div class="how">.*?</div></div>',
                  f'<div class="how"><div>{len(items)} clip{"s" if len(items) != 1 else ""} changed since your last listen. '
                  'Press <b>Play all</b>, or click a row.</div></div>', page, count=1, flags=re.S)
    (folder / "relisten.html").write_text(page, encoding="utf-8")
    print(f"{len(items)} clips in {folder / 'relisten.html'}")


if __name__ == "__main__":
    main()
