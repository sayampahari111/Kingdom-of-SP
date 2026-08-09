


from fastapi import FastAPI, UploadFile, File

app = FastAPI( title="Kingdom of SP",
    description="JEE PDF Summary and Question Generator",
    version="1.0")

@app.get("/")
def home():
    return {"message": "Hello Sayam"}

@app.post("/upload")
async def upload_pdf(file: UploadFile = File(...)):
    return {
        "filename": file.filename,
        "type": file.content_type
    }