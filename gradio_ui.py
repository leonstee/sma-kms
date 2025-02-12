import time
import gradio as gr
from main import get_llm_response


demo = gr.ChatInterface(
    get_llm_response,
    type="messages",
    flagging_mode="never",
    save_history=True,
)

if __name__ == "__main__":
    demo.launch()