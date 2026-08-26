"""展示する動画。**1 本ぶんの情報はここにしか書かない。**

`build.py` がこれを読んで、一覧 (`index.html`) と 1 本ぶんのページ (`v/<slug>.html`) を
両方吐く。**尺とサムネは書かない** —— mp4 から測って抜くので、書くと二重になる。

値は HTML の断片。リンクや `<code>` をそのまま書いてよい (`lede` だけは
リンクを貼らないこと —— OGP の説明文にタグを落として使うため)。

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
        "poster_at": 24.0,
        "target": "7-Zip File Manager（<code>winget install 7zip.7zip</code>。"
                  "撮影用のダミーは仕込みが作り、後片付けで消える）",
        "source": f'<a href="{GMP}/tree/main/docs/video/assist-7zip">docs/video/assist-7zip/</a>',
        "repro": "<strong>この 1 本だけ、コマンド 1 つでは出ません。</strong> "
                 "7-Zip は UI Automation にウィンドウの枠しか出さず自動操作が原理的に届かないので、"
                 f'<a href="{GMP}/blob/main/README_WINAPP.md">支援収録</a>で人が操作して撮っています。'
                 "<code>uv run gmp shoot docs/video/assist-7zip/plan.json</code> で画面を開き、"
                 "ビートごとの指示どおりに操作して撮ったあと <code>gmp record</code> → "
                 "<code>gmp render</code>。台本と操作手順は素材に入っています。",
    },
    {
        "slug": "assist-krita",
        "title": "Krita —— 描けなくなったら、選択範囲を疑う",
        "lede": "図形の片方を矩形選択して塗ったあと、解除を忘れたまま別の場所へ筆を走らせると、"
                "なぞっても線が一本も残らない。エラーも音も出ないのでブラシやレイヤーを疑って"
                "しまうが、原因は<strong>離れたところに残った選択範囲</strong>で、その外側は描けないように"
                "保護されている。解除して同じブラシ・同じ場所に描けるところまで。",
        "poster_at": 48.0,
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
