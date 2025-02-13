from os import getenv

from googlesearch import search
from curl_cffi import requests
from datetime import datetime

from langchain.retrievers import ContextualCompressionRetriever
from langchain.retrievers.document_compressors import CrossEncoderReranker
from langchain_community.cross_encoders import HuggingFaceCrossEncoder
from langchain_core.documents import Document
from langchain_ollama import OllamaEmbeddings
from langchain_qdrant import QdrantVectorStore

from unstructured.partition.html import partition_html

from ollama import Client

embed_model = OllamaEmbeddings(model=getenv("EMBEDDING_MODEL"))




def get_urls(query, result_num=1): # result_num: Das wievielte Ergebnis wird zurückgegeben --> Nur eins
    urls = search(query, lang="de", region="de", num_results=5, start_num=1)
    return urls

def generate_documents_from_html(html, url):
    elements = partition_html(text=html, skip_headers_and_footers=True, chunking_strategy="by_title")
    documents = []
    for el in elements:
        documents.append(Document(page_content=el.text, metadata={"source": url}))
    return documents

def store_documents_in_vector_store(documents):
    unstructured_chunk_vectorstore = QdrantVectorStore.from_documents(
                location = ":memory:",
                documents=documents,
                embedding=embed_model,
                prefer_grpc=False,
                collection_name="tmp_collection",
            )
    return unstructured_chunk_vectorstore





def prettify_html(html, url = ""):
    elements = partition_html(text=html, skip_headers_and_footers=True, chunking_strategy="by_title")
    pretty_text = "\n".join([str(el) for el in elements])
    pretty_text += f"\n\nQuelle: {url}, Zugriff am {datetime.today().strftime('%d.%m.%Y')}."
    return pretty_text

def scrape_website_html(url):
    html = requests.get(url).text
    return html

def websearch(query):
    urls = get_urls(query, 1)
    output = ""
    for url in urls: # hier nur erste URL
        try:
            html = scrape_website_html(url)
            pretty_text = prettify_html(html, url)
            output += pretty_text
            output += "\n\n--------\n\n"
        except:
            return f"Fehler beim Abrufen der Webseite {url}"
    return output


def get_llm_web_response(query, history=None):
    print("Query: " + query)
    source: str = websearch(query)
    request_template = ("Wo leben Wildschweine?")
    response_template= ("Wildschweine sind Säugetiere, die typischerweise im Wald leben. Sie bevorzugen feuchte Waldgebiete, die ihnen Schutz vor Nagetieren bieten.\n"
                        "URL: tiere-und-pfalzen.de/wildschweine/lebensraum.html, Zugriff am 11.03.2024.\n\n"
                        )




    prompt = (("Du bist ein Assistent rund um Fragen zu IT-Sicherheit und IT-Grundschutz."
              "Du beantwortest Fragen auf Basis von Website-Inhalten, die dir in der Anfrage zur Verfügung gestellt werden."
              "Gib am Ende der Antwort unbedingt die URL der Webseite an."
              "Falls du auf Basis bereitgestellten Informationen keine gute Antwort finden kannst, antworte exakt mit 'Ich kann diese Frage leider nicht beantworten'. Das ist sehr wichtig! Versuche nicht, die Frage nur schlecht oder ohne die bereitgestellten Informationen zu beantworten.\n\n"
              "Hier ist eine beispielhafte Antwort, auf die Frage '" + request_template + "', an deren Struktur du dich orientieren sollst: \n" + response_template + "\n\n" 
              "Dir wurde folgende Frage gestellt: ") + query +
              "\n\n Du hast folgenden Website-Inhalt zur Verfügung, um eine Antwort zu geben. "
              "Gib dabei auch die URL der von dir in der "
              "Antwort verwendeten Webseite an.\n\n" + source + "\n\n" +
              "Gib keine Überlegungen oder Zwischenschritte aus. Gib nur deine finale Antwort aus.")

    client = Client()
    response_stream = client.chat(
        model=getenv("LM_MODEL"),
        messages=[{"role": "user", "content": prompt}],
        stream=True
    )

    for chunk in response_stream:
        yield chunk['message']['content']




def pretty_return_docs(docs):
    return (
        f"\n{'-' * 100}\n".join(
            [f"Document {i+1}:\nQuelle: "+ d.metadata.get('source')+"\n\n" + d.page_content for i, d in enumerate(docs)]
        )
    )

def get_llm_web_response_vectorstore(query, history=None):
    print("Query: " + query)
    source: str = websearch(query)
    urls = search(query, lang="de", region="de", num_results=5, start_num=1)
    documents = []
    for url in urls:
        try:
            html = scrape_website_html(url)
            documents += generate_documents_from_html(html, url)
        except:
            pass
    temp_vector_store = store_documents_in_vector_store(documents)

    temp_chunk_retriever = temp_vector_store.as_retriever(search_kwargs={"k": 5})

    model = HuggingFaceCrossEncoder(model_name="cross-encoder/ms-marco-MiniLM-L-4-v2")
    compressor = CrossEncoderReranker(model=model, top_n=3)
    compression_temp_retriever = ContextualCompressionRetriever(
        base_compressor=compressor, base_retriever=temp_chunk_retriever
    )

    def get_chunks_for_llm(chunk_query):
        compressed_docs = compression_temp_retriever.invoke(chunk_query)
        return pretty_return_docs(compressed_docs)

    chunks = get_chunks_for_llm(query)

    request_template = ("Wo leben Wildschweine?")
    response_template = ("Wildschweine sind Säugetiere, die typischerweise im Wald leben.\n"
                         "Quelle: tiere-und-pfalzen.de/wildschweine/lebensraum.html\n\n"
                         "Wildschweine leben insbesondere gerne in feuchten Waldgebieten, die ihnen Schutz vor Nagetieren bieten.\n"
                         "Quelle: tierwelt-experte.de/blog/wildschweine-in-waeldern.html'\n\n"
                         )

    prompt = (("Du bist ein Assistent rund um Fragen zu IT-Sicherheit und IT-Grundschutz."
               "Du beantwortest Fragen auf Basis von Dokumenten, die dir in der Anfrage zur Verfügung gestellt werden."
               "Für jedes Dokument, das du zur Erstellung der Antwort verwendest, gibst du die Quelle und Seite an."
               "Falls du auf Basis der Dokumente keine gute Antwort finden kannst, antworte exakt mit 'Ich kann diese Frage leider nicht beantworten'. Das ist sehr wichtig! Versuche nicht, die Frage nur schlecht oder ohne die Dokumente zu beantworten.\n\n"
               "Sofern du jedoch relevante Informationen in den bereitgestellten Dokumenten findest, verwende auch alle relevanten Informationen und gebe diese in einer umfangreichen Antwort aus."
               "Hier ist eine beispielhafte Antwort, auf die Frage '" + request_template + "', an deren Struktur du dich orientieren sollst: \n" + response_template + "\n\n"
                                                                                                                                                                       "Dir wurde folgende Frage gestellt: ") + query +
              "\n\n Du hast folgende Dokumente zur Verfügung, um eine Antwort zu geben. "
              "Gib dabei auch die Quelle und die Seite der von dir in der "
              "Antwort verwendeten Dokumente an.\n\n" + chunks + "\n\n"
              "Verwende KEINESFALLS Wissen, welches nicht in den Dokumenten enthalten ist. Alle von dir verwendeten Begriffe"
              "müssen in den Dokumenten enthalten sein. Falls das nicht möglich ist, antworte exakt mit dem Satz 'Ich kann diese Frage leider nicht beantworten' "
              "Solltest du eines der bereitgestellten Dokumente benutzen, gib die Quelle wie im Beispiel an!"
              )

    client = Client()
    response_stream = client.chat(
        model=getenv("LM_MODEL"),
        messages=[{"role": "user", "content": prompt}],
        stream=True
    )

    for chunk in response_stream:
        yield chunk['message']['content']

