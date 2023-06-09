from langchain.document_loaders import DirectoryLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter

import openai
from langchain.embeddings.openai import OpenAIEmbeddings

from langchain.llms import OpenAI

import pinecone 
from langchain.vectorstores import Pinecone

from env import ENV_VALUES

directory = 'data'

pdf_loader = DirectoryLoader('data', glob='**/*.pdf')
txt_loader = DirectoryLoader('data', glob='**/*.txt')

loaders = [pdf_loader, txt_loader]
documents = []
for loader in loaders:
  documents.extend(loader.load())

print(f"There are total {len(documents)} ")

def load_docs(directory):
  loader = DirectoryLoader(directory)
  documents = loader.load()
  return documents

def split_docs(documents,chunk_size=1000,chunk_overlap=20):
  text_splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
  docs = text_splitter.split_documents(documents)
  return docs

embeddings = OpenAIEmbeddings(model_name="ada", openai_api_key=ENV_VALUES["OPEN_API_KEY"])

query_result = embeddings.embed_query("Hello world")
len(query_result)



documents = load_docs(directory)
print(len(documents))

docs = split_docs(documents)
print(len(docs))

print(docs[0].page_content)

print(docs[5].page_content)

pinecone.init(
    api_key="fd693794-a9e2-4ea2-a072-365fd8376ab9",  # find at app.pinecone.io
    environment="asia-northeast1-gcp"  # next to api key in console
)

index_name = "langchain-demo"

index = Pinecone.from_documents(docs, embeddings, index_name=index_name)

def get_similiar_docs(query,k=2,score=False):
  if score:
    similar_docs = index.similarity_search_with_score(query,k=k)
  else:
    similar_docs = index.similarity_search(query,k=k)
  return similar_docs

query = "Why are none of my classes showing up?"
similar_docs = get_similiar_docs(query)
similar_docs

# model_name = "text-davinci-003"
# model_name = "gpt-3.5-turbo"
# model_name = "gpt-4"
# llm = OpenAI(model_name=model_name)