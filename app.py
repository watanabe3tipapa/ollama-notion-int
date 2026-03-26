import os

import gradio as gr
import httpx

OLLAMA_BASE_URL = "http://localhost:11434"
OLLAMA_API_URL = f"{OLLAMA_BASE_URL}/api/generate"
OLLAMA_TAGS_URL = f"{OLLAMA_BASE_URL}/api/tags"
DEFAULT_MODEL = "qwen3.5:latest"

NOTION_API_KEY = os.environ.get("NOTION_API_KEY", "")
NOTION_PAGE_ID = os.environ.get("NOTION_PAGE_ID", "")

NOTION_API_BASE = "https://api.notion.com/v1"


def get_ollama_models() -> list[str]:
    """Ollamaからモデル一覧を取得する"""
    try:
        timeout = httpx.Timeout(10.0, connect=5.0)
        with httpx.Client(timeout=timeout) as client:
            resp = client.get(OLLAMA_TAGS_URL)
            resp.raise_for_status()
            data = resp.json()
            models = [m["name"] for m in data.get("models", [])]
            return models if models else [DEFAULT_MODEL]
    except Exception:
        return [DEFAULT_MODEL]


async def call_ollama_async(
    prompt: str,
    model: str = None,
    max_tokens: int = 512,
    stream: bool = False,
) -> str:
    """Ollama APIを呼び出して応答を返す（非ストリーミング）"""
    if not prompt:
        return "（空の入力）"

    model = model or DEFAULT_MODEL
    body = {
        "model": model,
        "prompt": prompt,
        "max_tokens": max_tokens,
        "stream": stream,
    }

    timeout = httpx.Timeout(120.0, connect=10.0)
    async with httpx.AsyncClient(timeout=timeout) as client:
        try:
            resp = await client.post(OLLAMA_API_URL, json=body)
            resp.raise_for_status()

            if stream:
                return "（ストリーミングは現在未対応）"

            data = resp.json()
            response = data.get("response", "")
            if response:
                return response

            thinking = data.get("thinking", "")
            if thinking:
                return thinking

            return "（応答なし）"

        except httpx.HTTPStatusError as e:
            text = e.response.text if e.response is not None else ""
            return f"HTTP error: {e.response.status_code if e.response is not None else 'N/A'} - {text}"
        except httpx.RequestError as e:
            return f"Request error: {e}"
        except Exception as e:
            return f"エラー: {e}"


def refresh_models():
    """モデル一覧を更新してドロップダウンを更新"""
    models = get_ollama_models()
    return gr.update(choices=models, value=models[0] if models else DEFAULT_MODEL)


async def append_to_page(page_id: str, content: str, api_key: str):
    """Notionページにコンテンツを追加する"""
    if not api_key:
        raise Exception("Notion API Key が設定されていません")

    url = f"{NOTION_API_BASE}/blocks/{page_id}/children"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "Notion-Version": "2022-06-28",
    }
    payload = {
        "children": [
            {
                "object": "block",
                "type": "paragraph",
                "paragraph": {
                    "rich_text": [{"type": "text", "text": {"content": content}}]
                },
            }
        ]
    }

    async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
        resp = await client.patch(url, json=payload, headers=headers)
        print(f"DEBUG: status={resp.status_code}, body={resp.text[:200]}")
        resp.raise_for_status()
        return resp.json()


async def create_page_in_db(db_id: str, title: str, content: str, api_key: str):
    """Notionデータベースに新規ページを作成する"""
    if not api_key:
        raise Exception("Notion API Key が設定されていません")

    url = f"{NOTION_API_BASE}/pages"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "Notion-Version": "2022-06-28",
    }
    payload = {
        "parent": {"database_id": db_id},
        "properties": {"Name": {"title": [{"text": {"content": title}}]}},
        "children": [
            {
                "object": "block",
                "type": "paragraph",
                "paragraph": {
                    "rich_text": [{"type": "text", "text": {"content": content}}]
                },
            }
        ],
    }

    async with httpx.AsyncClient(timeout=30.0) as client:
        resp = await client.post(url, json=payload, headers=headers)
        resp.raise_for_status()
        return resp.json()


def build_ui():
    models = get_ollama_models()
    default_model = models[0] if models else DEFAULT_MODEL

    with gr.Blocks(title="Ollama Notion Integration") as demo:
        gr.Markdown("# Ollama Notion Integration")

        with gr.Row():
            with gr.Column(scale=3):
                prompt = gr.Textbox(
                    label="プロンプト", lines=4, placeholder="入力してください"
                )
            with gr.Column(scale=1):
                model = gr.Dropdown(
                    label="モデル",
                    choices=models,
                    value=default_model,
                    interactive=True,
                )
                refresh_btn = gr.Button("🔄", size="sm")

        with gr.Row():
            clear_btn = gr.Button("クリア")
            generate_btn = gr.Button("送信", variant="primary")
            stop_btn = gr.Button("停止", variant="stop")

        output_preview = gr.Textbox(label="出力プレビュー", lines=15, interactive=True)

        with gr.Row():
            with gr.Column():
                notion_action = gr.Radio(
                    ["なし", "append", "create"], label="Notionアクション", value="なし"
                )
            with gr.Column():
                notion_id = gr.Textbox(
                    label="Notion Page/Database ID", value=NOTION_PAGE_ID
                )
                notion_api_key = gr.Textbox(
                    label="Notion API Key",
                    type="password",
                    value=NOTION_API_KEY,
                )

        with gr.Row():
            save_btn = gr.Button("保存")
            copy_btn = gr.Button("コピー")
            notion_save_btn = gr.Button("Notionに保存", variant="secondary")

        status = gr.Textbox(label="ステータス", lines=2)

        async def on_send(prompt_text, model_name):
            result = await call_ollama_async(prompt_text, model=model_name)
            return result

        generate_btn.click(
            on_send,
            inputs=[prompt, model],
            outputs=output_preview,
        )

        clear_btn.click(lambda: ("", ""), inputs=[], outputs=[prompt, output_preview])

        copy_btn.click(
            None,
            inputs=[output_preview],
            js="(text) => { navigator.clipboard.writeText(text); }",
        )

        save_btn.click(
            None,
            inputs=[output_preview],
            js="(text) => { const blob = new Blob([text], {type: 'text/plain'}); const url = URL.createObjectURL(blob); const a = document.createElement('a'); a.href = url; a.download = 'response.txt'; a.click(); URL.revokeObjectURL(url); }",
        )

        def stop_server():
            import os

            os._exit(0)

        stop_btn.click(stop_server, outputs=[])

        notion_save_btn.click(
            fn=save_to_notion,
            inputs=[output_preview, notion_action, notion_id, notion_api_key, prompt],
            outputs=status,
        )

        refresh_btn.click(fn=refresh_models, outputs=model)

    return demo


async def save_to_notion(
    output: str, action: str, page_id: str, api_key: str, prompt: str
):
    api_key_to_use = api_key if api_key else NOTION_API_KEY

    if not output or action == "なし" or not page_id:
        return "出力またはアクションが空です"

    if not api_key_to_use:
        return "Notion API Key が設定されていません"

    try:
        if action == "append":
            await append_to_page(page_id, output, api_key_to_use)
            return f"ページに追加完了: {page_id}"
        elif action == "create":
            title = prompt[:40] if prompt else "Generated"
            await create_page_in_db(page_id, title, output, api_key_to_use)
            return f"ページ作成完了: {page_id}"
    except Exception as e:
        return f"エラー: {e}"


if __name__ == "__main__":
    demo = build_ui()
    demo.launch()
