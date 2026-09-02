"""展示する動画。**1 本ぶんの情報はここにしか書かない。**

`build.py` がこれを読んで、一覧 (`index.html`) と 1 本ぶんのページ (`v/<slug>.html`) を
両方吐く。**尺とサムネは書かない** —— mp4 から測って抜くので、書くと二重になる。

値は HTML の断片。リンクや `<code>` をそのまま書いてよい (`lede` だけは
リンクを貼らないこと —— OGP の説明文にタグを落として使うため)。

`bundle_note` は **束をどこに置けば動くか**。`app.cwd` がフォルダ自身を指している
1 本はどこでも動くが、プロジェクトのルートを指している 1 本は元の場所に戻さないと
開けない。**そこを書かないと、落とした人が「動かない」で終わる。**

`bundle` は **その動画を撮った設定一式の在り処**。`build.py` が `git archive` で
zip にして `bundles/<slug>.zip` に置く。**隣に clone してあることが前提**なので、
無ければ build がそこで止まる (黙って古い zip を配らない)。

## 1 本足す

1. `videos/<slug>.mp4` を置く
2. ここに 1 ブロック足す
3. `python build.py`
4. 出来た `index.html` / `v/<slug>.html` / `videos/<slug>.jpg` ごとコミットする
"""

BASE = "https://lancard-aikawa.github.io/GhostMoviePlayGallery/"
GMP = "https://github.com/lancard-aikawa/GhostMoviePlay"

SITE_TITLE = "GhostMoviePlay Gallery"
SITE_DESCRIPTION = (
    "GhostMoviePlay で作った実演解説動画の実例集。"
    "素材はすべて公開されていて、clone すれば同じ動画が出ます。"
)
CREDIT = "音声合成: VOICEVOX:ずんだもん —— 各動画にも同じクレジットを焼き込んでいます。"

VIDEOS = [
    {
        "slug": "gmp",
        "title": "GhostMoviePlay の紹介",
        "lede": "ツール自身の説明ページを操作しながら、3 段構成（plan → record → render）が"
                "何を分けているのかを見せる 1 本。",
        "poster_at": 30.0,
        "bundle": {"repo": "../GhostMoviePlay", "path": "docs/video/intro"},
        "bundle_note": "このフォルダは <strong>GhostMoviePlay の <code>docs/video/intro/</code> に戻して</strong>"
                       "使います —— <code>app.start</code> がこのパスの <code>site/</code>"
                       "（収録対象の説明ページ。<strong>同梱してあります</strong>）を簡易サーバで"
                       "配信するので、置き場所が変わると開けません。",
        "target": "同梱の説明ページ（<code>docs/video/intro/site/index.html</code>）",
        "source": f'<a href="{GMP}/tree/main/docs/video/intro">docs/video/intro/</a>'
                  "（構成・台本とも公開）",
        "repro": "<code>uv run gmp build docs/video/intro/plan.json --voice</code>",
    },
    {
        "slug": "glosspop",
        "title": "GlossPop —— 登録する語は「短いほど危ない」",
        "lede": "選択したテキストを AI が辞書化して以後の表示で自動リンクするビューア。"
                "短く一般的な語を登録すると本文がリンクだらけになるところを実演し、"
                "日本語には語境界が無く部分文字列で照合しているからだと説明して、"
                "用語名を直して 1 箇所に収めるまで。",
        "poster_at": 48.0,
        "bundle": {"repo": "../GlossPop", "path": "docs/video/gloss-scope"},
        "bundle_note": "このフォルダは <strong>GlossPop の <code>docs/video/gloss-scope/</code> に戻して</strong>"
                       "使います —— <code>app.cwd</code> が GlossPop のルートを指していて、"
                       "<code>serve.py</code> が向こうの <code>content/</code> を読みます。"
                       "<strong>撮る対象そのものは入っていません</strong>（別リポジトリです）。",
        "target": '<a href="https://github.com/lancard-aikawa/GlossPop">GlossPop</a>'
                  "（収録用の使い捨てデータルートを <code>serve.py</code> が立てるので、実辞書は触らない）",
        "source": '<a href="https://github.com/lancard-aikawa/GlossPop/tree/main/docs/video/gloss-scope">'
                  "GlossPop/docs/video/gloss-scope/</a>",
        "repro": "<code>uv run gmp build ../GlossPop/docs/video/gloss-scope/plan.json --voice</code>"
                 "（GhostMoviePlay 側で実行）",
    },
    {
        "slug": "assist-7zip",
        "title": "7-Zip —— パスワード付き zip は、ファイル名を隠さない",
        "lede": "機密ファイル 4 つを、いちばん強い AES-256 のパスワード付き zip にする。"
                "ところが出来た書庫を開くとパスワードを訊かれず、中のファイル名が全部読める。"
                "zip はファイル名の一覧を暗号化しない仕様で、<strong>暗号の強さとは関係が無い</strong>と説明し、"
                "7z 形式の「ファイル名を暗号化」で隠せるところまで。",
        "poster_at": 27.0,
        "bundle": {"repo": "../GhostMoviePlay", "path": "docs/video/assist-7zip"},
        "bundle_note": "<strong>どこに置いても動きます</strong> —— <code>app.cwd</code> はこのフォルダ自身で、"
                       "仕込みが撮影用のダミーを作ります（<code>C:\\gmp\\sample</code>。後片付けで消えます）。",
        "target": "7-Zip File Manager（<code>winget install 7zip.7zip</code>。"
                  "撮影用のダミーは仕込みが作り、後片付けで消える）",
        "source": f'<a href="{GMP}/tree/main/docs/video/assist-7zip">docs/video/assist-7zip/</a>',
        "repro": "<code>uv run gmp build docs/video/assist-7zip/plan.json --voice</code>"
                 "（Windows のみ。7-Zip が要ります）<br>"
                 "<strong>機械が 7-Zip を操作して撮ります。</strong> UI Automation には"
                 "ウィンドウの枠しか出さないアプリですが、Win32 のウィンドウツリーからは"
                 "一覧もダイアログも掴めるので、一覧の行を"
                 "<code>row=給与明細_2026-07.pdf</code> のように"
                 "<strong>名前で指して</strong>操作しています —— 同じ台本から 2 回撮って"
                 "9 枚のショットが byte 一致します。"
                 "<strong>撮っている間はマウスとキーボードに触らないでください</strong>"
                 "（本物の入力を送るので、前に出たウィンドウに入ります）。",
    },
    {
        "slug": "assist-krita",
        "title": "Krita —— 描けなくなったら、選択範囲を疑う",
        "lede": "図形の片方を矩形選択して塗ったあと、解除を忘れたまま別の場所へ筆を走らせると、"
                "なぞっても線が一本も残らない。エラーも音も出ないのでブラシやレイヤーを疑って"
                "しまうが、原因は<strong>離れたところに残った選択範囲</strong>で、その外側は描けないように"
                "保護されている。解除して同じブラシ・同じ場所に描けるところまで。",
        "poster_at": 48.0,
        "bundle": {"repo": "../GhostMoviePlay", "path": "docs/video/assist-krita"},
        "bundle_note": "<strong>どこに置いても動きます</strong> —— <code>app.cwd</code> はこのフォルダ自身で、"
                       "仕込みが撮影用のダミーを作ります。撮るのは人なので <code>gmp shoot</code> から。",
        "target": "Krita（<code>winget install KDE.Krita</code>。"
                  "撮影用の白いキャンバスは仕込みが作り、後片付けで消える）",
        "source": f'<a href="{GMP}/tree/main/docs/video/assist-krita">docs/video/assist-krita/</a>',
        "repro": "<strong>この 1 本もコマンド 1 つでは出ません。</strong> "
                 "キャンバスは Krita が自分で描いていて UI Automation からは原理的に見えないので、"
                 f'<a href="{GMP}/blob/main/README_WINAPP.md">支援収録</a>で人が操作して撮っています。'
                 "筆を走らせるところは静止画では伝わらないため、10 ビートのうち 5 つは"
                 "<strong>録画</strong>で撮りました。"
                 "<code>uv run gmp shoot docs/video/assist-krita/plan.json</code> で画面を開き、"
                 "ビートごとの指示どおりに操作して撮ったあと <code>gmp record</code> → "
                 "<code>gmp render</code>。",
    },
]
