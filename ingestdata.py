from dotenv import load_dotenv, dotenv_values
import os
import sys
from langchain.vectorstores import Pinecone
import pinecone 
from langchain.document_loaders import DirectoryLoader, TextLoader, PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings.openai import OpenAIEmbeddings
from util import move_files
#

embeddings = OpenAIEmbeddings(openai_api_key=os.getenv("OPEN_API_KEY"))
pinecone.init(
            api_key=os.getenv("PINECONE_API_KEY"),  # find at app.pinecone.io
            environment=os.getenv("PINECONE_ENV") # next to api key in console
        )
pineConeIndex = pinecone.Index(index_name=os.getenv("PINECONE_INDEX"))
index = Pinecone.from_existing_index(index_name=os.getenv("PINECONE_INDEX"), embedding=embeddings)

def addNewTextDoc(path):
    loader = TextLoader(path, encoding="utf-8")
    doc = loader.load()
    docs = split_docs(doc)
    index.add_documents(documents=docs)

def addNewPDFDoc(path):
    loader = PyPDFLoader(path)
    doc = loader.load()
    docs = split_docs(doc)
    index.add_documents(documents=docs)

def split_docs(documents,chunk_size=1000, chunk_overlap=20):
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    docs = text_splitter.split_documents(documents)
     # Get the total number of characters so we can see the average later
    num_total_characters = sum([len(x.page_content) for x in docs])
    print (f"Now you have {len(docs)} documents that have an average of {num_total_characters / len(docs):,.0f} characters (smaller pieces)")
    return docs

def load_docs(documentspath):
       loader = DirectoryLoader(documentspath)
       documents = loader.load()
       print (f"You have {len(documents)} document")
       return documents

def ingets_data():
    documents = load_docs("newdata")
    docs = split_docs(documents)
    Pinecone.from_documents(docs, embeddings, index_name=os.getenv("PINECONE_INDEX"))
    move_files("newdata", "data")

ingets_data()