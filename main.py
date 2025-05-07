from fastapi import FastAPI
from dotenv import load_dotenv

from routes import flowchart

# Load environment variables
load_dotenv()

app = FastAPI(title="Flowchart Generator API")

@app.get("/")
async def root():
    return {"message": "Flowchart Generator API is running"}

app.include_router(flowchart.router, prefix="/flowchart")







