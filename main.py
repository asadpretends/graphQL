import logging
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from agent import GraphQLAgent

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(title="GraphQL Agent API")

# Initialize agent
agent = GraphQLAgent()

class QueryRequest(BaseModel):
    q: str

class QueryResponse(BaseModel):
    answer: str

@app.post("/query", response_model=QueryResponse)
async def process_query(request: QueryRequest):
    """Process a natural language query and return a formatted response"""
    try:
        logger.info(f"Received query: {request.q}")
        result = agent.process_query(request.q)
        return result
    except Exception as e:
        logger.error(f"Error processing request: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "ok"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)