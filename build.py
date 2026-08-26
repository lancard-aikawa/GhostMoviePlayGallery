"""`videos.py` から一覧と 1 本ぶんのページを吐く.

    python build.py

出るもの (全部コミットする —— GitHub Pages はビルドしないので、
配信されるのはここで出来たファイルそのもの):

    index.html          一覧
    v/<slug>.html       1 本ぶんのページ (「この動画を見て」で渡す URL)
    videos/<slug>.jpg   サムネ (OGP の og:image と <video poster>)

**尺とサムネは mp4 から取る。** 手で書くと、動画を差し替えたときに黙って嘘になる
(本体の「同じ数え方を 2 か所に書かない」と同じ理由)。ffmpeg / ffprobe が要る。

**style.css は生成しない。** データではないので手で直す。
"""

from __future__ import annotations

import html
import re
import subprocess
import sys
from pathlib import Path

import videos as data

ROOT = Path(__file__).resolve().parent
VIDEO_DIR = ROOT / "videos"
PAGE_DIR = ROOT / "v"

FAVICON = ("data:image/svg+xml,%3Csvg%20xmlns='http://www.w3.org/2000/svg'%20"
           "viewBox='0%200%2032%2032'%3E%3Crect%20width='32'%20height='32'%20rx='7'%20"
           "fill='%231d6ae5'/%3E%3Cpath%20d='M13%2010.5L22%2016l-9%205.5z'%20fill='%23fff'/%3E%3C/svg%3E")


def _run(args: list[str]) -> str:
    done = subprocess.run(args, capture_output=True, text=True)
    if done.returncode != 0:
        raise SystemExit(f"失敗しました: {' '.join(args[:2])}\n{done.stderr.strip()}")
    return done.stdout.strip()


def seconds_of(path: Path) -> float:
    return float(_run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                       "-of", "csv=p=0", str(path)]))


def make_poster(mp4: Path, at: float, out: Path, crop: str | None = None) -> None:
    """サムネを 1 枚抜く. **毎回撮り直す** —— mp4 を差し替えたのに古い絵が残るほうが困る.

    `crop` は ffmpeg の crop 式。**映したくないものを外すため**にある
    (GlossPop はアプリの上端に既定フォルダのフルパスを出すので、ユーザー名が入る)。
    動画そのものは切らない —— ここで切れるのはサムネだけ。
    """
    chain = f"{crop}," if crop else ""
    _run(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
          "-ss", f"{at:.2f}", "-i", str(mp4), "-frames:v", "1",
          "-vf", f"{chain}scale=1280:-2", "-q:v", "4", str(out)])


def plain(fragment: str) -> str:
    """HTML の断片から、meta タグに入れられる素の文にする."""
    return html.unescape(re.sub(r"<[^>]+>", "", fragment)).strip()


def head(title: str, description: str, url: str, image: str, prefix: str,
         video: str | None = None, seconds: float | None = None,
         og_title: str | None = None) -> str:
    """<head>. **og:image と og:url は絶対 URL** (相対だと展開されない).

    `og_title` はプレビューの見出し。タブに出す `title` と違って
    サイト名を足さない (og:site_name が別に出るので二重になる)。
    """
    tags = [
        '<meta charset="utf-8">',
        '<meta name="viewport" content="width=device-width, initial-scale=1">',
        f"<title>{html.escape(title)}</title>",
        f'<link rel="icon" href="{FAVICON}">',
        f'<link rel="stylesheet" href="{prefix}style.css">',
        f'<meta name="description" content="{html.escape(description)}">',
        f'<meta property="og:title" content="{html.escape(og_title or title)}">',
        f'<meta property="og:description" content="{html.escape(description)}">',
        f'<meta property="og:url" content="{url}">',
        f'<meta property="og:image" content="{image}">',
        f'<meta property="og:site_name" content="{html.escape(data.SITE_TITLE)}">',
        '<meta property="og:locale" content="ja_JP">',
        '<meta name="twitter:card" content="summary_large_image">',
    ]
    if video:
        tags += [
            '<meta property="og:type" content="video.other">',
            f'<meta property="og:video" content="{video}">',
            f'<meta property="og:video:secure_url" content="{video}">',
            '<meta property="og:video:type" content="video/mp4">',
        ]
        if seconds:
            tags.append(f'<meta property="video:duration" content="{round(seconds)}">')
    else:
        tags.append('<meta property="og:type" content="website">')
    return "\n".join(tags)


def meta_rows(item: dict, seconds: float) -> str:
    rows = [("尺", f"約 {round(seconds)} 秒"),
            ("収録対象", item["target"]),
            ("素材", item["source"]),
            ("再現", item["repro"])]
    return "\n".join(f"      <dt>{name}</dt><dd>{value}</dd>" for name, value in rows)


def index_page(items: list[tuple[dict, float]]) -> str:
    cards = []
    for item, seconds in items:
        slug = item["slug"]
        cards.append(f"""
  <article class="card" id="{slug}">
    <h2><a href="v/{slug}.html">{html.escape(item["title"])}</a></h2>
    <p>{item["lede"]}</p>
    <video controls playsinline preload="metadata" poster="videos/{slug}.jpg" src="videos/{slug}.mp4"></video>
    <dl class="meta">
{meta_rows(item, seconds)}
    </dl>
    <p class="more"><a href="v/{slug}.html">この動画だけのページ →</a></p>
  </article>
""")
    assisted = sum(1 for item, _ in items if "支援収録" in item["repro"])
    return f"""<!doctype html>
<html lang="ja">
<head>
{head(data.SITE_TITLE, data.SITE_DESCRIPTION, data.BASE,
      data.BASE + f"videos/{items[0][0]['slug']}.jpg", "")}
</head>
<body>
<div class="wrap">

<header>
  <h1>{html.escape(data.SITE_TITLE)}</h1>
  <p class="lede">
    AI がアプリやゲームを実際に操作し、<strong>失敗例とその理由、そして正解ルートまでを字幕付きで解説する動画</strong>を作るパイプライン
    —— <a href="{data.GMP}">GhostMoviePlay</a> で実際に出力した動画を並べています。
  </p>
  <p class="lede muted">
    録画と書き出しは決定論的なので、素材を clone して同じコマンドを打てば同じものが出ます。
    各動画に、それを再現するコマンドと素材の場所を添えてあります。
    <strong>{assisted} 本は例外です</strong> —— 自動操作が届かないアプリは人が操作して撮るので、
    clone しても撮り直しが要ります（そのカードに書いてあります）。
  </p>
  <p class="toplinks">
    <a href="{data.GMP}">本体リポジトリ</a>
    <a href="https://github.com/lancard-aikawa/GhostMoviePlayGallery">このページのリポジトリ</a>
  </p>
</header>

<main>
{"".join(cards)}</main>

<footer>
  <p>{html.escape(data.CREDIT)}</p>
</footer>

</div>
</body>
</html>
"""


def video_page(item: dict, seconds: float) -> str:
    slug = item["slug"]
    title = f'{item["title"]} | {data.SITE_TITLE}'
    return f"""<!doctype html>
<html lang="ja">
<head>
{head(title, plain(item["lede"]), f"{data.BASE}v/{slug}.html",
      f"{data.BASE}videos/{slug}.jpg", "../",
      video=f"{data.BASE}videos/{slug}.mp4", seconds=seconds,
      og_title=item["title"])}
</head>
<body>
<div class="wrap">

<header>
  <p class="back"><a href="../">← {html.escape(data.SITE_TITLE)}</a></p>
  <h1>{html.escape(item["title"])}</h1>
  <p class="lede">{item["lede"]}</p>
</header>

<main>
  <article class="card">
    <video controls playsinline preload="metadata" poster="../videos/{slug}.jpg" src="../videos/{slug}.mp4"></video>
    <dl class="meta">
{meta_rows(item, seconds)}
    </dl>
  </article>
</main>

<footer>
  <p>{html.escape(data.CREDIT)}</p>
  <p><a href="../">ほかの動画を見る</a></p>
</footer>

</div>
</body>
</html>
"""


def main() -> int:
    PAGE_DIR.mkdir(exist_ok=True)
    items = []
    for item in data.VIDEOS:
        mp4 = VIDEO_DIR / f"{item['slug']}.mp4"
        if not mp4.is_file():
            raise SystemExit(f"mp4 がありません: {mp4}")
        seconds = seconds_of(mp4)
        make_poster(mp4, item["poster_at"], VIDEO_DIR / f"{item['slug']}.jpg",
                    item.get("poster_crop"))
        items.append((item, seconds))

    (ROOT / "index.html").write_text(index_page(items), encoding="utf-8", newline="\n")
    for item, seconds in items:
        (PAGE_DIR / f"{item['slug']}.html").write_text(
            video_page(item, seconds), encoding="utf-8", newline="\n")

    print(f"index.html と v/*.html を {len(items)} 本ぶん書きました")
    for item, seconds in items:
        print(f"  {item['slug']:<14} 約 {round(seconds)} 秒  -> v/{item['slug']}.html")
    return 0


if __name__ == "__main__":
    sys.exit(main())
