import os
from typing import Optional
import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import urllib.parse
from services.pineconeindexer import pineConeIndexer

app = FastAPI()

origins = [
    "*",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/hello")
def auth():
    return { "msg" : "hello" }

@app.get("/vectorcount")
def getVectorsCount():
    count = pineConeIndexer.get_vector_count()
    return { "success": True, "count" : count }

@app.post("/embeddocs")
def getVectorsCount():
    pineConeIndexer.embedDocs()
    return { "success": True }

@app.post("/adddocument/{filename}")
def addDocumentToPineCone(filename: str):
    split_tup = os.path.splitext(filename)
    fileExtention = split_tup[1]

    if fileExtention == ".txt":
        print(f"Converting the {filename} into documents")
        pineConeIndexer.addNewTextDoc(f"data/{filename}")
        print(f"Successfully converted {filename} file into embedded vectors and added to the pinecone database")
        return {"success": True}

    if fileExtention == ".pdf":
        print(f"Converting the {filename} into documents")
        pineConeIndexer.addNewPDFDoc(f"data/{filename}")
        print(f"Successfully converted {filename} file into embedded vectors and added to the pinecone database")
        return {"success": True}
    raise HTTPException(status_code=404, detail="File not supported at this file")

@app.get("/knowledgebase")
def knowledgesupport( q: Optional[str] = None):
    try:
        if q:
            answer = pineConeIndexer.getSolution(urllib.parse.unquote(q))
            return { "success": True, "message": answer }

        return { "success": False, "message": "Query is missing" }

    except Exception as e:
        return { "success": False, "message": "Something went wrong" }

if __name__ == '__main__':
    uvicorn.run('main:app', host="0.0.0.0", port=8000, reload=True)