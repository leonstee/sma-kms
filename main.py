from langchain_ollama import OllamaEmbeddings
from langchain_qdrant import QdrantVectorStore
from ollama import Client
from qdrant_client import QdrantClient
from langchain.retrievers import ContextualCompressionRetriever
from langchain.retrievers.document_compressors import CrossEncoderReranker
from langchain_community.cross_encoders import HuggingFaceCrossEncoder
from dotenv import load_dotenv
from os import getenv

# Setup Embedding Model
load_dotenv()

embed_model = OllamaEmbeddings(model=getenv("EMBEDDING_MODEL"))

# Connect to Vector Store
client = QdrantClient(url=getenv("QDRANT_URL"))

unstructured_chunk_vectorstore = QdrantVectorStore(
    client=client,
    collection_name=getenv("QDRANT_COLLECTION"),
    embedding=embed_model,
)


# Instantiate Retrieval Step
# Der Retriever gibt die 5 passendsten Dokumente aus der Vektordatenbank zurück
unstructured_chunk_retriever = unstructured_chunk_vectorstore.as_retriever(search_kwargs={"k" : 5})


def custom_priority_retriever(query, k=5):
    results = unstructured_chunk_retriever.invoke(query)

    # Sortiere die Ergebnisse nach Priorität (Zotero hat die höchste Priorität)
    sorted_results = sorted(results, key=lambda doc: doc.metadata.get('priority', 999))

    # Wähle die Top-k Ergebnisse nach Priorität
    return sorted_results[:k]



# Helper functions for prettifying docs
# Auch Quellen werden mit angegeben
def pretty_print_docs(docs):
    print(
        f"\n{'-' * 100}\n".join(
            [f"Document {i+1}:\nQuelle: "+ d.metadata.get('source')+", Seite "+str(d.metadata.get('page_number'))+"\n\n" + d.page_content for i, d in enumerate(docs)]
        )
    )
def pretty_return_docs(docs):
    return (
        f"\n{'-' * 100}\n".join(
            [f"Document {i+1}:\nQuelle: "+ d.metadata.get('source')+", Seite "+str(d.metadata.get('page_number'))+"\n\n" + d.page_content for i, d in enumerate(docs)]
        )
    )


# Compressor for Unstructured
# Der Compressor holt sich die 5 Dokumente vom Retriever und sortiert diese danach, mit welchen sich am ehesten die Frage beantworten lässt.
# Die drei besten Dokumente werden ausgegeben
model = HuggingFaceCrossEncoder(model_name="cross-encoder/ms-marco-MiniLM-L-4-v2")
compressor = CrossEncoderReranker(model=model, top_n=3)
compression_unstructured_retriever = ContextualCompressionRetriever(
    base_compressor=compressor, base_retriever=unstructured_chunk_retriever
)

# Methode, die den Compressor nutzt, um an die besten Dokuemente zu kommen
# und diese als formatierten Text ausgibt, sodass dieser an das LM gegeben werden kann.
# Neben Inhalt wird auch die Quelle (Dateiname & Seite) angegeben
def get_chunks_for_llm(query):
    compressed_docs = custom_priority_retriever(query)
    return pretty_return_docs(compressed_docs)


# Instanziierung des Ollama-Clients
ollama = Client(host=getenv("OLLAMA_HOST"))

# Gibt der LM die Nutzeranfrage und die dazu passenden Dokumente
# LM gibt Antwort zurück
# History/Verlauf wird derzeit nicht genutzt
def get_llm_response(query, history=None):
    chunks = get_chunks_for_llm(query)
    request_template = ("Wo leben Wildschweine?")
    response_template= ("Wildschweine sind Säugetiere, die typischerweise im Wald leben.\n"
                        "Quelle(n): tiere_und_pflanze.pdf, Seite 123\n\n"
                        "Wildschweine leben insbesondere gerne in feuchten Waldgebieten, die ihnen Schutz vor Nagetieren bieten.\n"
                        "Quelle(n): wildscheine-lebensraum.pdf, Seite 87 & Seite 89'\n\n"
                        )




    prompt = (("Du bist ein Assistent rund um Fragen zu IT-Sicherheit und IT-Grundschutz."
              "Du beantwortest Fragen auf Basis von Dokumenten, die dir in der Anfrage zur Verfügung gestellt werden."
              "Für jedes Dokument, das du zur Erstellung der Antwort verwendest, gibst du die Quelle und Seite an."
              "Falls du auf Basis der Dokumente keine Antwort finden kannst, gib einfach 'null' aus. Versuche nicht, die Frage ohne die Dokumente zu beantworten.\n\n"
              "Hier ist eine beispielhafte Antwort, auf die Frage '" + request_template + "', an deren Struktur du dich orientieren sollst: \n" + response_template + "\n\n" 
              "Dir wurde folgende Frage gestellt: ") + query +
              "\n\n Du hast folgende Dokumente zur Verfügung, um eine Antwort zu geben. "
              "Gib dabei auch die Quelle und die Seite der von dir in der "
              "Antwort verwendeten Dokumente an.\n\n" + chunks)

    client = Client()
    response_stream = client.chat(
        model=getenv("LM_MODEL"),
        messages=[{"role": "user", "content": prompt}],
        stream=True
    )

    for chunk in response_stream:
        yield chunk['message']['content']







