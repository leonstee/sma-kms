import time
import gradio as gr
from main import get_llm_response

def stream_llm_response(query, history=None):
    response = ""
    for chunk in get_llm_response(query, history):
        response+=chunk
        yield response


demo = gr.ChatInterface(
    stream_llm_response,
    type="messages",
    flagging_mode="never",
    save_history=True,
)

if __name__ == "__main__":
    demo.launch()