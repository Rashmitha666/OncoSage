from langchain_huggingface import HuggingFaceEmbeddings
from langchain_ollama import OllamaLLM
from langchain.chains import RetrievalQA
from langchain_community.vectorstores import FAISS
from langchain_community.document_loaders import WikipediaLoader


def create_agent(topic="Lung cancer"):
    loader = WikipediaLoader(query=topic, load_max_docs=2)
    docs = loader.load()

    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    vectordb = FAISS.from_documents(docs, embeddings)

    llm = OllamaLLM(model="mistral")
    qa = RetrievalQA.from_chain_type(llm=llm, retriever=vectordb.as_retriever())
    return qa

def get_wikipedia_answer(topic, question):
    agent = create_agent(topic)
    answer = agent.invoke(question)
    return {
        "answer": answer,
        "source": f"Wikipedia (topic: {topic})",
        "source_url": f"https://en.wikipedia.org/wiki/{topic.replace('','_')}"
}
