from langchain import OpenAI

# The vectorstore we'll be using
from langchain.vectorstores import FAISS

# The LangChain component we'll use to get the documents
from langchain.chains import RetrievalQA

# The easy document loader for text
from langchain.document_loaders import TextLoader

# The embedding engine that will convert our text to vectors
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.llms import OpenAI
from langchain.chains.summarize import load_summarize_chain
from langchain.text_splitter import RecursiveCharacterTextSplitter

from services.env import ENV_VALUES

class KnowledgeQA:
    def __init__(self):
        self.llm = OpenAI(temperature=0, openai_api_key=ENV_VALUES["OPEN_API_KEY"])
        self.loadDocs()

    def loadDocs(self):
        self.loader = TextLoader('data/lanschool/teacherfaqs.txt')
        doc = self.loader.load()
        print (f"You have {len(doc)} document")
        print (f"You have {len(doc[0].page_content)} characters in that document")
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=3000, chunk_overlap=400)
        docs = text_splitter.split_documents(doc)
        # Get the total number of characters so we can see the average later
        num_total_characters = sum([len(x.page_content) for x in docs])
        print (f"Now you have {len(docs)} documents that have an average of {num_total_characters / len(docs):,.0f} characters (smaller pieces)")
        # Get your embeddings engine ready
        embeddings = OpenAIEmbeddings(openai_api_key=ENV_VALUES["OPEN_API_KEY"])
        
        # Embed your documents and combine with the raw text in a pseudo db. Note: This will make an API call to OpenAI
        # Facebook AI Similarity Search (Faiss) is a library for efficient similarity search and clustering of dense vectors. It contains algorithms that search in sets of vectors of any size, up to ones that possibly do not fit in RAM.
        # It also contains supporting code for evaluation and parameter tuning.
        # https://python.langchain.com/en/latest/modules/indexes/vectorstores/examples/faiss.html
        docsearch = FAISS.from_documents(docs, embeddings)
        self.qa = RetrievalQA.from_chain_type(llm=self.llm, chain_type="stuff", retriever=docsearch.as_retriever())

    def getSolution(self, query):
        return self.qa.run(query)

knowledgeQA = KnowledgeQA()