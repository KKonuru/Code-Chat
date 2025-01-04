from ollama import chat, ChatResponse,embeddings
from ollama import ChatResponse
from langchain_ollama import ChatOllama,OllamaEmbeddings
from langchain_community.vectorstores import FAISS
import faiss


#Define the chat model
llm = ChatOllama(
    model = "llama3.2",
    temperature = 0.8,
    num_predict = 256,
    # other params ...
  )

#Define the embedding model
embedding_model = OllamaEmbeddings(
    model="nomic-embed-text"
)






  

def main():
    print("Hello World")


if __name__=="__main__":
    main()