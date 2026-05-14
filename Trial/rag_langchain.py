from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain_classic.chains import RetrievalQA
from langchain_community.document_loaders import TextLoader
loader = TextLoader("bio.txt")
documents = loader.load()
splitter = RecursiveCharacterTextSplitter(
    chunk_size=300,
    chunk_overlap=50
)

docs = splitter.split_documents(documents)
embeddings = GoogleGenerativeAIEmbeddings(
    model="gemini-embedding-001",
    google_api_key="AIzaSyDrNgEGwWUUv5NoONCols-gCV2_x2i27hM"
)
vectorstore = FAISS.from_documents(docs, embeddings)
retriever = vectorstore.as_retriever(search_kwargs={"k": 3})
llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    google_api_key="AIzaSyDrNgEGwWUUv5NoONCols-gCV2_x2i27hM"
)
qa_chain = RetrievalQA.from_chain_type(
    llm=llm,
    retriever=retriever
)
query = input("Ask: ")

response = qa_chain.run(query)

print("\nAnswer:\n")
print(response)
