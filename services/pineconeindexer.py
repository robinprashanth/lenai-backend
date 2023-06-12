from langchain.document_loaders import DirectoryLoader, TextLoader, PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings.openai import OpenAIEmbeddings

from langchain.llms import OpenAI
# The LangChain component we'll use to get the documents
from langchain.chains import RetrievalQA
import pinecone 
from langchain.vectorstores import Pinecone
from langchain.chains.question_answering import load_qa_chain
from langchain.docstore.document import Document
from services.env import ENV_VALUES
from util import move_files
class PineConeIndexer:
    def __init__(self):
        self.index_name = "langchain-demo"
        self.model_name = ENV_VALUES["LLM_MODEL"]
        self.llm = OpenAI(model_name=self.model_name, openai_api_key=ENV_VALUES["OPEN_API_KEY"])
        self.embeddings = OpenAIEmbeddings(openai_api_key=ENV_VALUES["OPEN_API_KEY"])
        self.chain = load_qa_chain(self.llm, chain_type="stuff")
        self.initPineCone()
    
    def test(self, paths):
        print("In pinecone")
        print(paths)

    def initPineCone(self):
        pinecone.init(
            api_key=ENV_VALUES["PINECONE_API_KEY"],  # find at app.pinecone.io
            environment=ENV_VALUES["PINECONE_ENV"] # next to api key in console
        )
        self.pineConeIndex = pinecone.Index(index_name=self.index_name)
        self.index = Pinecone.from_existing_index(index_name=self.index_name, embedding=self.embeddings)
        self.qa = RetrievalQA.from_chain_type(llm=self.llm, chain_type="stuff", retriever=self.index.as_retriever())

    def get_vector_count(self):
        indexStatus = self.pineConeIndex.describe_index_stats()
        return indexStatus["total_vector_count"]
    
    def getIndexStatus(self):
        status = pinecone.describe_index(self.index_name)
        print(status)
        return status


    def embedDocs(self):
        if self.index_name not in pinecone.list_indexes():
            print(f"The index {self.index_name} does not exist in pinecone db")
        else:
            # Check if the index is empty. If empty push the initial documents to pinecone. 
            indexStatus = self.pineConeIndex.describe_index_stats()
            if indexStatus["total_vector_count"] == 0:
                print(f"Loading files to be converted and pushed to pinecone db")
                documents = self.load_docs()
                docs = self.split_docs(documents)
                self.pushEmbeddedDocs(docs)
    

    def ingest_documents(self):
        documents = self.load_docs(ENV_VALUES["newData"])
        docs = self.split_docs(documents)
        self.pushEmbeddedDocs(docs)
        move_files("newdata", "data")


    def addNewTextDoc(self, path):
        self.loader = TextLoader(path)
        doc = self.loader.load()
        print (f"You have {len(doc)} document")
        print (f"You have {len(doc[0].page_content)} characters in that document")
        docs = self.split_docs(doc)
        self.index.add_documents(documents=docs)
    
    def addPlainText(self, text):
        doc = Document(page_content=text)
        # docs = self.split_docs(doc)
        # print(docs)
        self.index.add_documents(documents=doc)

    def addNewPDFDoc(self, path):
        self.loader = PyPDFLoader(path)
        doc = self.loader.load()
        print (f"You have {len(doc)} document")
        print (f"You have {len(doc[0].page_content)} characters in that document")
        docs = self.split_docs(doc)
        self.index.add_documents(documents=docs)

    def load_docs(self, documentspath=ENV_VALUES["datapath"]):
       loader = DirectoryLoader(documentspath)
       documents = loader.load()
       print (f"You have {len(documents)} document")
       return documents
    
    def RetrievalQA(self):
        self.qa = RetrievalQA.from_chain_type(llm=self.llm, chain_type="stuff", retriever=self.index.as_retriever())

    def split_docs(self, documents,chunk_size=1000, chunk_overlap=20):
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
        docs = text_splitter.split_documents(documents)
         # Get the total number of characters so we can see the average later
        num_total_characters = sum([len(x.page_content) for x in docs])
        print (f"Now you have {len(docs)} documents that have an average of {num_total_characters / len(docs):,.0f} characters (smaller pieces)")
        return docs
    
    def pushEmbeddedDocs(self, docs):
        Pinecone.from_documents(docs, self.embeddings, index_name=self.index_name)

    def get_similiar_docs(self, query,k=2,score=False):
        if score:
          similar_docs = self.index.similarity_search_with_score(query,k=k)
        else:
          similar_docs = self.index.similarity_search(query,k=k)
        return similar_docs
    
    def get_answer(self, query):
       similar_docs = self.get_similiar_docs(query)
       # print(similar_docs)
       answer =  self.chain.run(input_documents=similar_docs, question=query)
       return answer
    
    def getSolution(self, query):
        return self.qa.run(query)
    
pineConeIndexer = PineConeIndexer()

# if __name__ == "__main__":
#    pineConeIndexer.embedDocs()
# #    ans = pineConeIndexer.get_answer("Why are none of my classes showing up?")
# #    print(ans)
# #    pineConeIndexer.addNewTextDoc("datas/activehrs.txt")
# #    ans = pineConeIndexer.get_answer("How can I configure active hrs")
# #    print(ans)
#    ss = pineConeIndexer.getSolution("Why are none of my classes showing up?")
#    print(ss)
