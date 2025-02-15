from langchain_ollama import OllamaEmbeddings
from langchain_qdrant import QdrantVectorStore
from ollama import Client
from qdrant_client import QdrantClient, models
from langchain.retrievers import ContextualCompressionRetriever
from langchain.retrievers.document_compressors import CrossEncoderReranker
from langchain_community.cross_encoders import HuggingFaceCrossEncoder
from dotenv import load_dotenv
from os import getenv

from config import QDRANT_COLLECTION

# Setup Embedding Model
load_dotenv()

embed_model = OllamaEmbeddings(model=getenv("EMBEDDING_MODEL"))

# Connect to Vector Store
client = QdrantClient(url=getenv("QDRANT_URL"))

def create_collection_if_not_exists():
    if not client.collection_exists(QDRANT_COLLECTION):
        vector = embed_model.embed_query("test")
        vector_size = len(vector)
        client.create_collection(
            collection_name=QDRANT_COLLECTION,
            vectors_config=models.VectorParams(size=vector_size, distance=models.Distance.COSINE),
        )
        print(f"Collection {QDRANT_COLLECTION} erstellt.")

# Beim Starten der Anwendung eine Collection anlegen, falls noch keine existiert
create_collection_if_not_exists()


unstructured_chunk_vectorstore = QdrantVectorStore(
    client=client,
    collection_name=getenv("QDRANT_COLLECTION"),
    embedding=embed_model,
)



# Instantiate Retrieval Step
# Der Retriever gibt die 5 passendsten Dokumente aus der Vektordatenbank zurück
unstructured_chunk_retriever = unstructured_chunk_vectorstore.as_retriever(search_kwargs={"k" : 5})


def custom_priority_retriever(query, k=5):
    results = compression_unstructured_retriever.invoke(query)

    # Sortiere die Ergebnisse nach Priorität
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

              "Falls du auf Basis der Dokumente keine gute Antwort finden kannst, antworte exakt mit 'Ich kann diese Frage leider nicht beantworten'. Das ist sehr wichtig! Versuche nicht, die Frage nur schlecht oder ohne die Dokumente zu beantworten.\n\n"
              "Sofern du jedoch relevante Informationen in den bereitgestellten Dokumenten findest, verwende auch alle relevanten Informationen und gebe diese in einer umfangreichen Antwort aus.\n"
               "Zitiere nicht nur Dokumente, sondern nutze sie auch, um eigene Antworten daraus zu bilden. Denke also nach und kombiniere logisch. Das ist unfassbar wichtig! Du sollst selbst nachdenken und das bereitgestellte Wissen sinnvoll nutzen. Quellen gibst du aber trotzdem an.\n"
               "Quellen gibst du mit Dateititel, Dateipfad und Seitennummer an. Nur die Nummer des Documents reicht nicht aus!"
               "Wenn du wirklich keine Antwort finden kannst, gibst du 'Ich kann diese Frage leider nicht beantworten' aus. Tue das aber wirklich nur, wenn keine sinnvolle oder gute Antwort möglich ist. Probiere zumindest, die Situation und Interessen des Nutzers zu verstehen und "
               "eine gute Antwort zu bilden. Solltest du im Laufe der Generierung merken, dass die Antwort nicht gut ist, kannst du jederzeit 'Ich kann diese Frage leider nicht beantworten' ausgeben. Das ist in Ordnung. \n\n"
               "Vergiss niemals, die Quellen mit Dateipfad und Seite anzugeben!"

              "Hier ist eine beispielhafte Antwort, auf die Frage '" + request_template + "', an deren Struktur du dich orientieren sollst: \n" + response_template + "\n\n" 
              "Dir wurde folgende Frage gestellt: ") + query +
              "\n\n Du hast folgende Dokumente zur Verfügung, um eine Antwort zu geben. "
              "Gib dabei auch die Quelle und die Seite der von dir in der "
              "Antwort verwendeten Dokumente an.\n\n" + chunks + "\n\n"
              "Treffe keinesfalls Aussagen, deren Inhalt nicht logisch aus den Dokumenten hervorgeht. "
              "Falls das nicht möglich ist, antworte exakt mit dem Satz 'Ich kann diese Frage leider nicht beantworten' "
              )

    client = Client()
    response_stream = client.chat(
        model=getenv("LM_MODEL"),
        messages=[{"role": "user", "content": prompt}],
        stream=True
    )

    for chunk in response_stream:
        yield chunk['message']['content']







