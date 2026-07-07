# 音声生成手順

## 前提条件
- tts.py がプロジェクトルートにあること
- VOICEVOXは tts.py が自動起動する（未起動なら起動を試み、API応答まで待機）。手動起動は不要

## キャラクターと声の対応
- ケン → 白上虎太郎（ふつう）/ speaker ID: 12
- ハナ → 波音リツ（クイーン）/ speaker ID: 65

声を変えたい場合は tts.py の SPEAKERS の値を変更する。
利用可能なIDはVOICEVOX画面で確認するか、以下で一覧取得できる：
http://localhost:50021/speakers

## 手順

### Step 1: 音声生成コマンドを実行
```
python tts.py "scripts/YYYYMMDD_ep###_テーマ.md"
```
tts.py が起動時に VOICEVOX の起動を確認し、未起動なら自動起動してAPI応答まで待つ。
（自動起動に失敗した場合のみ、VOICEVOXを手動起動して再実行する）

### Step 2: 出力確認
- 同名の .wav ファイルが scripts/ に生成される
- 例：scripts/20260705_ep009_ラーメン体にいいの悪いの.wav
- 再生して声・間・セリフの読み上げを確認する

### Step 3: バージョン管理（台本修正後の再生成）
台本を修正して音声を再生成する場合はファイル名末尾にバージョン番号を付ける。

| 生成回 | ファイル名 |
|---|---|
| 初回 | scripts/YYYYMMDD_ep###_テーマ.wav |
| 2回目 | scripts/YYYYMMDD_ep###_テーマv2.wav |
| 3回目 | scripts/YYYYMMDD_ep###_テーマv3.wav |

手順：
```
python tts.py "scripts/YYYYMMDD_ep###_テーマ.md"
# 出力された .wav をリネームしてバージョン番号を付ける
# 例：Rename-Item "scripts/テーマ.wav" "scripts/テーマv2.wav"
```

### Step 4: 問題があった場合
- 声が合わない → tts.py の SPEAKERS の ID を変更して再実行
- セリフが読まれない → 台本の該当行のフォーマットを確認（`キャラ名：「セリフ」` の形式になっているか）
- VOICEVOXに接続できない → 自動起動に失敗している。VOICEVOXを手動起動して再実行（VOICEVOX_PATHS にインストール先が含まれているか確認）
