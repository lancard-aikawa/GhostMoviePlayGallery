"""`videos.py` から一覧と 1 本ぶんのページを吐く.

    python build.py

出るもの (全部コミットする —— GitHub Pages はビルドしないので、
配信されるのはここで出来たファイルそのもの):

    index.html          一覧
    v/<slug>.html       1 本ぶんのページ (「この動画を見て」で渡す URL)
    videos/<slug>.jpg   サムネ (OGP の og:image と <video poster>)
    bundles/<slug>.zip  その動画を撮った設定一式 (構成・台本・仕込み)

**尺とサムネは mp4 から取る。** 手で書くと、動画を差し替えたときに黙って嘘になる
(本体の「同じ数え方を 2 か所に書かない」と同じ理由)。ffmpeg / ffprobe が要る。

**設定の zip は `git archive` で作る。** 作業ツリーから拾うと追跡していないもの
(`__pycache__`、撮ったショット) が混ざるし、**どのコミットの中身かを言えない**。

**上げる前に止める。** 束の中にユーザー名を含むパスがあったら、ページを吐かずに
落ちる。出す口は漏らす口でもあり、実際に動画・サムネ・ドキュメントの画像で
3 回踏んでいる (本体の `docs/ideas/bundle.md`)。

**style.css は生成しない。** データではないので手で直す。
"""

from __future__ import annotations

import datetime
import getpass
import html
import re
import subprocess
import sys
import zipfile
from pathlib import Path

import videos as data

ROOT = Path(__file__).resolve().parent
VIDEO_DIR = ROOT / "videos"
PAGE_DIR = ROOT / "v"
BUNDLE_DIR = ROOT / "bundles"

# **束に入っていてはいけないもの。** 見つけたら止める (警告にしない —— 3 回とも
# 人が見落としている)。ドライブ直下の使い捨て (C:\gmp-sample) は意図して入れている
LEAKS = [
    (re.compile(r"[A-Za-z]:[\\/]Users[\\/]", re.I), "ユーザーフォルダの絶対パス"),
    (re.compile(re.escape(getpass.getuser()), re.I), "この機械のユーザー名"),
]
TEXT_SUFFIXES = {".md", ".json", ".py", ".toml", ".txt", ".html", ".css", ".js", ".yaml", ".yml"}

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


def git(repo: Path, *args: str) -> str:
    return _run(["git", "-C", str(repo), *args])


def make_bundle(item: dict) -> dict | None:
    """その動画を撮った設定一式を zip にする. 戻り値は表に出す情報.

    **`git archive` で取る。** 作業ツリーを歩くと追跡外のもの (`__pycache__`、
    撮ったショット) が混ざるし、**どのコミットの中身かを言えない**。
    """
    spec = item.get("bundle")
    if not spec:
        return None
    repo = (ROOT / spec["repo"]).resolve()
    if not (repo / ".git").exists():
        raise SystemExit(f"束ねる元が見つかりません: {repo}\n"
                         f"  ({item['slug']} は隣に置いた {spec['repo']} から取ります)")

    commit = git(repo, "rev-parse", "--short", "HEAD")
    dirty = git(repo, "status", "--porcelain", "--", spec["path"])
    blob = subprocess.run(
        ["git", "-C", str(repo), "archive", "--format=zip",
         f"--prefix={item['slug']}/", f"HEAD:{spec['path']}"],
        capture_output=True)
    if blob.returncode != 0:
        raise SystemExit(f"git archive に失敗しました ({item['slug']}): "
                         f"{blob.stderr.decode('utf-8', 'replace').strip()}")

    BUNDLE_DIR.mkdir(exist_ok=True)
    out = BUNDLE_DIR / f"{item['slug']}.zip"
    out.write_bytes(blob.stdout)

    names = check_bundle(out, item["slug"])
    with zipfile.ZipFile(out, "a", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr(f"{item['slug']}/BUNDLE.md", bundle_readme(item, spec, commit, names))
    return {"bytes": out.stat().st_size, "commit": commit,
            "dirty": bool(dirty), "files": len(names)}


def check_bundle(path: Path, slug: str) -> list[str]:
    """**上げる前に止める。** 束の中にユーザー名が入っていたら落とす."""
    names = []
    with zipfile.ZipFile(path) as zf:
        for info in zf.infolist():
            if info.is_dir():
                continue
            names.append(info.filename)
            if Path(info.filename).suffix.lower() not in TEXT_SUFFIXES:
                continue
            text = zf.read(info).decode("utf-8", "replace")
            for line_no, line in enumerate(text.splitlines(), 1):
                for pattern, why in LEAKS:
                    if pattern.search(line):
                        raise SystemExit(
                            f"束に {why} が入っています: {slug}.zip\n"
                            f"  {info.filename}:{line_no}: {line.strip()[:100]}\n"
                            f"  **配る前に直す。** 出す口は漏らす口でもあります")
    return names


def bundle_readme(item: dict, spec: dict, commit: str, names: list[str]) -> str:
    """束の中に置く出所書き。**どこから来たか**が無い束は追えない."""
    listed = "\n".join(f"- `{n.split('/', 1)[1]}`" for n in sorted(names) if "/" in n)
    today = datetime.date.today().isoformat()
    return f"""# {item["title"]}

{plain(item["lede"])}

この zip は **その動画を撮った設定一式**です。動画は
{data.BASE}v/{item["slug"]}.html にあります。

## 出所

- リポジトリ: `{spec["repo"].lstrip("./")}` の `{spec["path"]}`
- コミット: `{commit}`
- 束ねた日: {today}

## 入っているもの

{listed}

生成物 (ショット・音声・mp4) は入っていません。**手元で作れるもの**なので、
配るのは入力だけです。

## 置き場所

{plain(item.get("bundle_note", "対象プロジェクトの `docs/video/<名前>/` に置きます。"))}

## 使う

[GhostMoviePlay]({data.GMP}) を入れてから:

```
uv run gmp doctor            # 足りない前提を言う
uv run gmp ui --run          # 画面から。撮る面で段を上から押す
uv run gmp build plan.json --voice
```

**手引きは [README_BUNDLE.md]({data.GMP}/blob/main/README_BUNDLE.md)。**
落としてから撮るまでを Claude Code にやらせる頼み方も、そこに貼れる形で置いてあります。

## 走らせる前に読む

**`plan.json` の `app.setup` / `app.start` / `app.teardown` は、あなたの機械で
走るコマンドです。** 束を開いたら、まずそこを読んでください。この束のものは
撮影用のダミーを作って片付けるだけですが、**確かめるのは受け取った側の仕事**です。
"""


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


def meta_rows(item: dict, seconds: float, bundle: dict | None, prefix: str) -> str:
    rows = [("尺", f"約 {round(seconds)} 秒"),
            ("収録対象", item["target"]),
            ("素材", item["source"])]
    if bundle:
        # **落とせば同じことが手元で出来る**、が一目で分かる行。
        # 走るコマンドが入っていることも、開く前に言う
        rows.append(("設定", (
            f'<a href="{prefix}bundles/{item["slug"]}.zip" download>{item["slug"]}.zip</a>'
            f'（{bundle["bytes"] // 1024 + 1} KB / {bundle["files"]} ファイル / '
            f'出所 <code>{bundle["commit"]}</code>）<br>'
            "構成・台本・仕込みの一式。生成物は入っていません。"
            f'{item.get("bundle_note", "")}<br>'
            "<strong>開いたらまず <code>app.setup</code> / <code>app.start</code> を"
            "読んでください</strong>（あなたの機械で走るコマンドです）。"
            f'手引き → <a href="{data.GMP}/blob/main/README_BUNDLE.md">README_BUNDLE.md</a>')))
    rows.append(("再現", item["repro"]))
    return "\n".join(f"      <dt>{name}</dt><dd>{value}</dd>" for name, value in rows)


def index_page(items: list[tuple[dict, float, dict | None]]) -> str:
    cards = []
    for item, seconds, bundle in items:
        slug = item["slug"]
        cards.append(f"""
  <article class="card" id="{slug}">
    <h2><a href="v/{slug}.html">{html.escape(item["title"])}</a></h2>
    <p>{item["lede"]}</p>
    <video controls playsinline preload="metadata" poster="videos/{slug}.jpg" src="videos/{slug}.mp4"></video>
    <dl class="meta">
{meta_rows(item, seconds, bundle, '')}
    </dl>
    <p class="more"><a href="v/{slug}.html">この動画だけのページ →</a></p>
  </article>
""")
    assisted = sum(1 for item, _, _ in items if "支援収録" in item["repro"])
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


def video_page(item: dict, seconds: float, bundle: dict | None) -> str:
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
{meta_rows(item, seconds, bundle, '../')}
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
        items.append((item, seconds, make_bundle(item)))

    (ROOT / "index.html").write_text(index_page(items), encoding="utf-8", newline="\n")
    for item, seconds, bundle in items:
        (PAGE_DIR / f"{item['slug']}.html").write_text(
            video_page(item, seconds, bundle), encoding="utf-8", newline="\n")

    print(f"index.html と v/*.html を {len(items)} 本ぶん書きました")
    for item, seconds, bundle in items:
        note = ""
        if bundle:
            note = f"  設定 {bundle['bytes'] // 1024 + 1}KB ({bundle['commit']})"
            if bundle["dirty"]:
                note += "  ! 束ねる元に未コミットの変更あり (zip は HEAD の中身)"
        print(f"  {item['slug']:<14} 約 {round(seconds)} 秒"
              f"  -> v/{item['slug']}.html{note}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
