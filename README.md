# GhostMoviePlay Gallery

[GhostMoviePlay](https://github.com/lancard-aikawa/GhostMoviePlay) で実際に出力した動画の展示。
GitHub Pages で公開している → **https://lancard-aikawa.github.io/GhostMoviePlayGallery/**

## ファイルの役割

| | |
| --- | --- |
| `videos.py` | **1 本ぶんの情報はここにしか書かない**（タイトル・説明・収録対象・素材・再現コマンド） |
| `build.py` | それを読んで下の 3 つを吐く。`python build.py` |
| `index.html` | **生成物。手で直さない**（次の build で消える） |
| `v/<slug>.html` | **生成物。**「この動画を見て」と渡す 1 本ぶんの URL |
| `videos/<slug>.jpg` | **生成物。** サムネ（OGP のプレビュー画像と `<video poster>`） |
| `style.css` | データではないので**手で直す** |
| `videos/<slug>.mp4` | 展示する動画そのもの |

**尺とサムネは書かない。** mp4 から測って抜くので、動画を差し替えたら勝手に直る。

ここが持つのは **mp4 と説明だけ**。構成 (`video.md`) と台本 (`plan.json`) と収録対象は
それぞれのプロジェクトに置いたままで、ページからリンクする。録画と書き出しは決定論的なので、
素材を clone して同じコマンドを打てば同じ動画が出る —— それが確かめられる形を崩さないこと。

## 1本足す

```bash
# 1. 対象プロジェクトで撮る
uv run gmp build <パス>/plan.json --voice
uv run gmp where <パス>/plan.json          # output.mp4 の場所

# 2. mp4 を持ってくる (名前は英数字。videos.py の slug と揃える)
cp "<出力先>/output.mp4" videos/<slug>.mp4

# 3. videos.py に 1 ブロック足す
#    slug・タイトル・説明・サムネにする秒・収録対象・素材の URL・再現コマンド

python build.py                            # index.html / v/*.html / サムネが出来る

git add videos.py videos/ index.html v/ && git commit && git push
```

**サムネにする秒 (`poster_at`) は中身で選ぶ。** リンクを貼ったときのプレビューに
出る 1 枚なので、字幕ごとその動画の要点が写っているところにする。
**映したくないものがフレームに入るなら `poster_crop`** で落とす
(GlossPop はアプリの上端に既定フォルダのフルパスを出すので、ユーザー名が入る)。

**素材が公開されていない動画は載せない。** 再現できない動画が 1 本混ざると、
「clone すれば同じものが出る」というページ全体の主張が嘘になる。

## 踏みやすいところ

**`index.html` を手で直さない。** `build.py` が上書きするので、次に 1 本足した人が
黙って消す。直すのは `videos.py`（中身）か `style.css`（見た目）。

**`.gitignore` を本体からコピーしない。** 向こうは `*.mp4` を除外している (生成物なので正しい)。
こちらは mp4 を入れるのが目的なので、持ってくると置きたいものが置けなくなる。

**Git LFS を使わない。** GitHub Pages は LFS を展開せず、ポインタファイルをそのまま配信する
—— 再生できない動画が出来上がって、原因が分かりにくい。素の git で入れる。
1 ファイル 50MB で警告、100MB で拒否。crf 20 / 720p なら 100 秒で十数MB なので余裕がある。

**動画が本体リポジトリ側に混ざらないようにする。** 向こうに置くと、コードを clone した人が
全員 mp4 を引く。ここが別リポジトリなのはそのため。

## 撮り直しが積もったら

差し替えのたびに古い mp4 が履歴に残る。展示物しか無いリポジトリなので、
気になったら履歴ごと作り直してよい。

```bash
git checkout --orphan fresh && git add -A && git commit -m "履歴を作り直す"
git branch -M fresh main && git push -f origin main
```

## GitHub Pages の設定

リポジトリの Settings → Pages → Source = **Deploy from a branch**、Branch = `main` / `(root)`。
数十秒で上の URL が生きる。**GitHub 側にビルドは無い**（Jekyll も Actions も使わない）ので、
配信されるのはコミットしたファイルそのもの —— `build.py` の出力をコミットし忘れると、
ページだけ古いまま残る。
