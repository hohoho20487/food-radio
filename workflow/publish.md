# GitHubアップロード手順（自動）

## 目的
1エピソード分の生成物（台本・音声・ナレッジ）を、フローの最後に確認なしで commit & push する。

## リモート
- origin（main を追跡）。push 先は origin/main。

## 対象ファイル

### エピソード生成時のcommit（このワークフローが対象とするもの）
- scripts/YYYYMMDD_ep###_テーマ.md（台本）
- scripts/YYYYMMDD_ep###_テーマ.wav（音声）
- knowledge/〇〇.md（その回で新規作成・更新したナレッジ）

他回の生成物はこのcommitに含めない。`git add -A` や `git add .` は使わず、必ずパス指定で add すること。

### 設定ファイルの扱い
CLAUDE.md / tts.py / workflow/ / characters/ / docs/ / README.md などの設定・構成ファイルは GitHub 上に存在する（リポジトリの一部）。
ただしエピソード生成のたびに commit するものではなく、**内容を変更したときだけ別途 commit する**。

## 手順（確認なしで実行）
1. 対象ファイルだけをステージング
   ```
   git add "scripts/YYYYMMDD_ep###_テーマ.md" "scripts/YYYYMMDD_ep###_テーマ.wav" "knowledge/〇〇.md"
   ```
2. コミット（メッセージ例）
   ```
   git commit -m "Add ep### script, audio, and knowledge: テーマ"
   ```
3. プッシュ
   ```
   git push origin main
   ```

## 注意
- 修正版（v2 など）の場合も、その版のファイル名をそのまま対象にする。
- 失敗時（認証エラー・コンフリクト・push 拒否など）は中断してユーザーに報告する。
- `git push --force` は使わない。コンフリクトは握りつぶさず原因を報告する。
- 秘密情報を含むファイル（.env など）は絶対に add しない。
