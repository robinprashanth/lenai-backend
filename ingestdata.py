from dotenv import dotenv_values
import sys
import os
from langchain.vectorstores import Pinecone
import pinecone 
from langchain.document_loaders import DirectoryLoader, TextLoader, PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings.openai import OpenAIEmbeddings
from util import move_files
ENV_VALUES = dotenv_values('.env')

embeddings = OpenAIEmbeddings(openai_api_key=ENV_VALUES["OPEN_API_KEY"])
pinecone.init(
            api_key=ENV_VALUES["PINECONE_API_KEY"],  # find at app.pinecone.io
            environment=ENV_VALUES["PINECONE_ENV"] # next to api key in console
        )
pineConeIndex = pinecone.Index(index_name=ENV_VALUES["PINECONE_INDEX"])
index = Pinecone.from_existing_index(index_name=ENV_VALUES["PINECONE_INDEX"], embedding=embeddings)

# Get new files and modified files list
new_files_list = sys.argv[1].split(",")
modified_list = sys.argv[2].split(",")

print(f"There are {len(new_files_list)} new files found")
print(f"There are {len(modified_list)} modified files found")

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

# if len(new_files_list) > 0:
#     for file in new_files_list:
#         split_tup = os.path.splitext(file)
#         fileExtention = split_tup[1]    

#         if fileExtention == ".txt":
#             print("***"*20)
#             print(f"Converting the {file} into documents")
#             addNewTextDoc(file)
#             print(f"Successfully converted {file} file into embedded vectors and added to the pinecone database")
#             print("***"*20)
#         if fileExtention == ".pdf":
#             print("***"*20)
#             print(f"Converting the {file} into documents")
#             addNewPDFDoc(file)
#             print(f"Successfully converted {file} file into embedded vectors and added to the pinecone database")
#             print("***"*20)
#     print("***Ingestion Complete***")#
# else:
#     print("No new files found in the data folder. Skipping pinecone vector db operations.")

def load_docs(documentspath=ENV_VALUES["datapath"]):
       loader = DirectoryLoader(documentspath)
       documents = loader.load()
       print (f"You have {len(documents)} document")
       return documents

if len(new_files_list) > 0:
    documents = load_docs(ENV_VALUES["newData"])
    docs = split_docs(documents)
    Pinecone.from_documents(docs, embeddings, index_name=ENV_VALUES["PINECONE_INDEX"])
    move_files("newdata", "data")