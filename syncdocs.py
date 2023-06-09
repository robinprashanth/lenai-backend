from dotenv import load_dotenv, dotenv_values
import sys
import os
from langchain.vectorstores import Pinecone
import pinecone 
from langchain.document_loaders import TextLoader, PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings.openai import OpenAIEmbeddings
ENV_VALUES = dotenv_values('.env')

index_name="langchain-demo"
embeddings = OpenAIEmbeddings(openai_api_key=ENV_VALUES["OPEN_API_KEY"])
pinecone.init(
            api_key=ENV_VALUES["PINECONE_API_KEY"],  # find at app.pinecone.io
            environment=ENV_VALUES["PINECONE_ENV"] # next to api key in console
        )
pineConeIndex = pinecone.Index(index_name="langchain-demo")
index = Pinecone.from_existing_index(index_name=index_name, embedding=embeddings)
# Get new files and modified files list
new_files_list = sys.argv[1].split(",")
modified_list = sys.argv[2].split(",")

print(f"There are {len(new_files_list)} new files")
print(f"There are {len(modified_list)} modified files")

def addNewTextDoc(path):
    loader = TextLoader(path, encoding="utf-8")
    doc = loader.load()
    print (f"You have {len(doc)} document")
    print (f"You have {len(doc[0].page_content)} characters in that document")
    docs = split_docs(doc)
    index.add_documents(documents=docs)

def addNewPDFDoc(path):
    loader = PyPDFLoader(path)
    doc = loader.load()
    print (f"You have {len(doc)} document")
    print (f"You have {len(doc[0].page_content)} characters in that document")
    docs = split_docs(doc)
    index.add_documents(documents=docs)

def split_docs(documents,chunk_size=1000, chunk_overlap=20):
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    docs = text_splitter.split_documents(documents)
     # Get the total number of characters so we can see the average later
    num_total_characters = sum([len(x.page_content) for x in docs])
    print (f"Now you have {len(docs)} documents that have an average of {num_total_characters / len(docs):,.0f} characters (smaller pieces)")
    return docs

if len(new_files_list) > 0:
    for file in new_files_list:
        split_tup = os.path.splitext(file)
        fileExtention = split_tup[1]    

        if fileExtention == ".txt":
            print("***"*20)
            print(f"Converting the {file} into documents")
            addNewTextDoc(file)
            print(f"Successfully converted {file} file into embedded vectors and added to the pinecone database")
            print("***"*20)
        if fileExtention == ".pdf":
            print("***"*20)
            print(f"Converting the {file} into documents")
            addNewPDFDoc(file)
            print(f"Successfully converted {file} file into embedded vectors and added to the pinecone database")
            print("***"*20)
else:
    print("No new files found in the data folder. Skipping pinecone vector db operations.")