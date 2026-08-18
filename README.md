# GhostMoviePlay Gallery

[GhostMoviePlay](https://github.com/lancard-aikawa/GhostMoviePlay) で実際に出力した動画の展示。
GitHub Pages で公開している → **https://lancard-aikawa.github.io/GhostMoviePlayGallery/**

ここが持つのは **mp4 と説明だけ**。構成 (`video.md`) と台本 (`plan.json`) と収録対象は
それぞれのプロジェクトに置いたままで、ページからリンクする。録画と書き出しは決定論的なので、
素材を clone して同じコマンドを打てば同じ動画が出る —— それが確かめられる形を崩さないこと。

## 1本足す

```bash
# 1. 対象プロジェクトで撮る
uv run gmp build <パス>/plan.json --voice
uv run gmp where <パス>/plan.json          # output.mp4 の場所

# 2. mp4 を持ってくる (名前は英数字。ページの src と揃える)
cp "<出力先>/output.mp4" videos/<名前>.mp4

# 3. index.html の <!-- 1本足すときは… --> のブロックをコピーして埋める
#    尺・収録対象・素材の URL・再現コマンドの 4 つ

git add videos/<名前>.mp4 index.html && git commit && git push
```

**素材が公開されていない動画は載せない。** 再現できない動画が 1 本混ざると、
「clone すれば同じものが出る」というページ全体の主張が嘘になる。

## 踏みやすいところ

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
数十秒で上の URL が生きる。ビルドは無く、`index.html` がそのまま配信される。
