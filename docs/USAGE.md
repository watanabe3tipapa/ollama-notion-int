# Ollama Notion Int

## 概要

Ollamaで生成したテキストをNotionに保存するためのWeb UIアプリケーション。

MCP（Model Context Protocol）ではありません。
単なる HTTP API 直接呼び出しです。

## 技術スタック

- **Backend**: Python 3.x
- **Web Framework**: Gradio 6.x
- **HTTP Client**: httpx
- **LLM**: Ollama (ローカル)

## 前提条件

1. **Ollama** が localhost:11434 で起動していること
2. **Python 3.10以上**
3. オプション: Notion統合（後述）

## セットアップ

```bash
# uvがインストールされていない場合
brew install uv

# 仮想環境作成
uv venv

# 依存インストール
uv pip install -r requirements.txt

# 起動
uv run python app.py
```

http://localhost:7860 でアクセス可能

## 使い方

### 基本的な流れ

1. プロンプトを入力
2. モデルを選択（ドロップダウン）
3. 「送信」をクリック
4. 出力プレビューで確認
5. 「コピー」「保存」でファイル保存

### モデル選択

- ドロップダウンからモデルを選択
- 🔄 ボタンでモデル一覧を更新

---

# Notion 連携設定

## 手順1: 統合（Integration）を作成

1. [Notion My Integrations](https://www.notion.so/my-integrations) にアクセス
2. `+ New integration` をクリック
3. 名前を入力（例: `Ollama MCP`）
4. `Submit` で作成

## 手順2: APIトークンを取得

作成後画面（またはIntegrations一覧から選択）の「Configuration」タブで：
- **Internal Integration Secret** をコピー
- 例: `secret_xxxxxxxxxxxxxxxxxxxxx`

## 手順3: アクセス許可を設定

Notion側でアクセスを許可したいページまたはデータベースで：

1. ページの右上 `...` （三点メニュー）をクリック
2. 「Connect to」を選択
3. 作成した統合（例: `Ollama MCP`）を選択

## 手順4: ページIDを確認

アクセスしたいページのURLからIDを取得：
```
https://notion.so/{workspace_name}/{page_id}?v=...
```

例: `https://notion.so/workspace/My-Page-1234567890abcdef` の場合、ページIDは `1234567890abcdef`

## アプリでの使用方法

1. 「Notionアクション」で以下を選択：
   - `append` → 既存ページに内容を追加
   - `create` → 新規ページを作成
2. 「Notion Page/Database ID」にページIDを入力
3. 「Notion API Key」に `secret_xxx...` を入力
4. 「Notionに保存」をクリック

### 毎回入力不要にする方法

環境変数を設定すると、API KeyとページIDが自動的に入力されます：

```bash
# 起動前に実行
export NOTION_API_KEY="secret_xxxxxxxxxxxxxxxxxxxxx"
export NOTION_PAGE_ID="1234567890abcdef"

# アプリ起動
python app.py
```

または `.env` ファイルを作成：
```bash
NOTION_API_KEY=secret_xxxxxxxxxxxxxxxxxxxxx
NOTION_PAGE_ID=1234567890abcdef
```

※ `.env` を使用する場合、`python-dotenv` をインストールする必要があります：
```bash
pip install python-dotenv
```

起動前に環境変数を設定することで、UIに入力不要になります：

```bash
export NOTION_API_KEY="secret_xxxxxxxxxxxxxxxxxxxxx"
export NOTION_PAGE_ID="1234567890abcdef"
```

または `.env` ファイルを作成：
```bash
NOTION_API_KEY=secret_xxxxxxxxxxxxxxxxxxxxx
NOTION_PAGE_ID=1234567890abcdef
```

## 許可するCapability

統合作成時に以下を選択してください：
- ✅ Read content
- ✅ Insert content

---

# ファイル構成

```
ollama-notion-mcp/
├── app.py          # メインアプリケーション
├── USAGE.md        # このファイル
├── requirements.txt # Python依存
└── venv/           # 仮想環境
```

---

# API

### Ollama

- モデル一覧: `GET http://localhost:11434/api/tags`
- テキスト生成: `POST http://localhost:11434/api/generate`

### Gradio

- UI: `http://localhost:7860`
- API: `http://localhost:7860/gradio_api/`


このリポジトリに戻る
