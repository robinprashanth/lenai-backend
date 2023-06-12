import os
from typing import Optional
import uvicorn
from fastapi import FastAPI, HTTPException, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
import urllib.parse
from services.pineconeindexer import pineConeIndexer
from pydantic import BaseModel, Field
from services.models import TextDoc
from typing import List
import datetime
from util import readAllFiles, readFiles
from fastapi.responses import FileResponse

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

@app.get("/indexstatus")
def getIndexStatus():
    status = pineConeIndexer.getIndexStatus()
    return { "success": True, "data" : status }

@app.post("/embeddocs")
def getVectorsCount():
    pineConeIndexer.embedDocs()
    return { "success": True }

@app.post("/addtext")
def addText(body: TextDoc):
    pineConeIndexer.addPlainText(body.data)
    return { "success": True }

@app.post("/ingestDocuments")
def ingestDocuments():
    pineConeIndexer.ingest_documents()
    return { "success": True }

@app.post("/upload-files")
def upload(files: List[UploadFile] = File(...)):
    for file in files:
        try:
            contents = file.file.read()
            filename = f"newdata/{file.filename}"
            with open(filename, 'wb') as f:
                f.write(contents)
        except Exception:
            return {"message": "There was an error uploading the file(s)"}
        finally:
            file.file.close()

    return {"message": f"Successfuly uploaded {[file.filename for file in files]}"}    

@app.get("/newlyAddedfiles")
async def get_files():
    allFiles = readFiles("newdata")

    return allFiles

@app.get("/ingestedfiles")
async def get_ingested_files():
    allFiles = readFiles("data")

    return allFiles

@app.get("/newfiles/{filename}")
async def get_new_file(filename: str):
    directory = "newdata"
    file_path = f"{directory}/{filename}"
    return FileResponse(file_path, media_type="application/octet-stream", filename=filename)

@app.get("/trainedfiles/{filename}")
async def get_new_file(filename: str):
    directory = "data"
    file_path = f"{directory}/{filename}"
    return FileResponse(file_path, media_type="application/octet-stream", filename=filename)


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