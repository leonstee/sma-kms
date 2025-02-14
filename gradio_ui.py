import gradio as gr

from load_data import load_all_data_and_save_to_vectorstore
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









# Gradio Interface mit Button
with gr.Blocks(fill_height=True) as demo:
    chatbot = gr.ChatInterface(stream_llm_response, type="messages", flagging_mode="never", save_history=True, fill_height=True)
    with gr.Accordion(label="Erweitere Optionen", open=False):
        btn = gr.Button("vorhandene Dateien einlesen - kann zu Duplikation führen", size="sm")
        btn.click(fn=load_all_data_and_save_to_vectorstore)
#    btn.click()



if __name__ == "__main__":
    demo.launch(pwa=True)