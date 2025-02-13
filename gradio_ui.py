import gradio as gr
from main import get_llm_response
from websearch import get_llm_web_response_vectorstore


def stream_llm_response(query, history=None):
    response = ""
    for chunk in get_llm_response(query, history):
        response+=chunk
        yield response
        if response.find("Frage leider nicht beantworten") != -1:
            response = "Ich werde im Internet suchen...\n"
            yield response
            break
    if response == "Ich werde im Internet suchen...\n":
        for chunk_web in get_llm_web_response_vectorstore(query, history):
            response += chunk_web
            yield response





demo = gr.ChatInterface(
    stream_llm_response,
    type="messages",
    flagging_mode="never",
    save_history=True,
)

if __name__ == "__main__":
    demo.launch()