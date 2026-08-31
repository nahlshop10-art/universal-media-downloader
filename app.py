import gradio as gr
from backend.app.main import app as fastapi_app

# Minimal Gradio dashboard mounted alongside FastAPI
def check_status(url: str):
    return f"API is active! Endpoint available for: {url}"

demo = gr.Interface(
    fn=check_status,
    inputs=gr.Textbox(label="Media URL", placeholder="https://www.youtube.com/watch?v=..."),
    outputs=gr.Textbox(label="Backend Status"),
    title="Universal Media Downloader Cloud API",
    description="FastAPI 24/7 backend engine. Connects to https://universal-media-downloader.pages.dev."
)

app = gr.mount_gradio_app(fastapi_app, demo, path="/gradio")

if __name__ == "__main__":
    import uvicorn
    import os
    port = int(os.environ.get("PORT", 7860))
    uvicorn.run(app, host="0.0.0.0", port=port)
