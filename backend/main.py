"""
FastAPI backend for AI-based Python code error detection.
Exposes a /predict endpoint that accepts Python code and returns predicted error type.
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Dict, Optional
from contextlib import asynccontextmanager
from model import ErrorDetectionModel
from agent_orchestrator import CodeReviewAgent
from chat_handler import ChatHandler, ChatContext, ChatMessage
import uvicorn


# Global instances (loaded once at startup)
model: ErrorDetectionModel = None
agent: CodeReviewAgent = None
chat_handler: ChatHandler = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup and shutdown events."""
    global model, agent, chat_handler
    
    # Startup
    print("Starting up... Loading model...")
    model = ErrorDetectionModel()
    print("Model loaded successfully!")
    
    print("Initializing code review agent...")
    agent = CodeReviewAgent(runtime_model=model)
    print("Agent initialized and ready!")
    
    print("Initializing chat handler...")
    chat_handler = ChatHandler()
    print("Chat handler ready!")
    
    yield
    
    # Shutdown (cleanup if needed)
    print("Shutting down...")


# Request/Response models
class PredictRequest(BaseModel):
    """Request model for /predict endpoint."""
    code: str = Field(..., description="Python source code to analyze")


class PredictResponse(BaseModel):
    """Response model for /predict endpoint."""
    error_type: str = Field(..., description="Predicted error type")
    confidence: float = Field(..., description="Confidence score (0.0 - 1.0)")


class ReviewRequest(BaseModel):
    """Request model for /review endpoint."""
    code: str = Field(..., description="Source code to analyze")
    language: str = Field(default="python", description="Programming language (python, javascript, typescript, etc.)")
    include_logic_analysis: bool = Field(True, description="Include LLM-based logic analysis")
    include_optimizations: bool = Field(True, description="Include optimization suggestions")
    include_control_flow: bool = Field(True, description="Include control flow graph analysis")


class ReviewResponse(BaseModel):
    """Response model for /review endpoint."""
    compile_time: Dict = Field(..., description="Compile-time analysis results")
    runtime_risks: List[Dict] = Field(..., description="Runtime error predictions")
    logical_concerns: List[str] = Field(..., description="Logical issues and edge cases")
    optimizations: List[Dict] = Field(..., description="Code optimization suggestions")
    control_flow: Optional[Dict] = Field(None, description="Control flow graph and issues")
    summary: str = Field(..., description="Human-readable summary")


class ChatRequest(BaseModel):
    """Request model for /chat endpoint."""
    message: str = Field(..., description="User's question or message")
    code: str = Field(..., description="Python source code being discussed")
    analysis_results: Dict = Field(..., description="Previous analysis results for context")
    chat_history: List[Dict] = Field(default=[], description="Previous messages in conversation")


class ChatResponse(BaseModel):
    """Response model for /chat endpoint."""
    response: str = Field(..., description="AI-generated response to user's message")


# Initialize FastAPI app with lifespan
app = FastAPI(
    title="Python Error Detection API",
    description="AI-based error detection for Python code using CodeBERT",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware to allow requests from VS Code extension
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for local development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """Health check endpoint."""
    return {
        "status": "running",
        "message": "Python Error Detection API is running",
        "endpoint": "/predict"
    }


@app.post("/predict", response_model=PredictResponse)
async def predict(request: PredictRequest):
    """
    Predict the error type for given Python code.
    
    Args:
        request: PredictRequest containing Python code
        
    Returns:
        PredictResponse with error_type and confidence
    """
    if model is None:
        raise HTTPException(status_code=503, detail="Model not loaded yet")
    
    if not request.code or not request.code.strip():
        raise HTTPException(status_code=400, detail="Code cannot be empty")
    
    try:
        # Get prediction from model
        error_type, confidence = model.predict(request.code)
        
        return PredictResponse(
            error_type=error_type,
            confidence=round(confidence, 4)
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error during prediction: {str(e)}"
        )


@app.post("/review", response_model=ReviewResponse)
async def review_code(request: ReviewRequest):
    """
    Comprehensive code review using agentic AI.
    
    This endpoint orchestrates multiple analysis tools:
    - Compile-time error detection (AST-based)
    - Runtime error prediction (CodeBERT model)
    - Logical error detection (LLM reasoning)
    - Optimization suggestions (heuristics + LLM)
    
    Args:
        request: ReviewRequest with code and options
        
    Returns:
        ReviewResponse with comprehensive analysis
    """
    if agent is None:
        raise HTTPException(status_code=503, detail="Agent not loaded yet")
    
    if not request.code or not request.code.strip():
        raise HTTPException(status_code=400, detail="Code cannot be empty")
    
    try:
        # Run comprehensive review
        result = agent.review_code(
            code=request.code,
            language=request.language,
            include_logic_analysis=request.include_logic_analysis,
            include_optimizations=request.include_optimizations,
            include_control_flow=request.include_control_flow
        )
        
        return ReviewResponse(
            compile_time=result.compile_time,
            runtime_risks=result.runtime_risks,
            logical_concerns=result.logical_concerns,
            optimizations=result.optimizations,
            control_flow=result.control_flow,
            summary=result.summary
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error during code review: {str(e)}"
        )


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Interactive chat about code analysis.
    
    This endpoint allows users to ask follow-up questions about their code
    and the analysis results. The chat maintains context from previous messages.
    
    Args:
        request: ChatRequest with user message, code, analysis, and history
        
    Returns:
        ChatResponse with AI-generated answer
    """
    if chat_handler is None:
        raise HTTPException(status_code=503, detail="Chat handler not loaded yet")
    
    if not request.message or not request.message.strip():
        raise HTTPException(status_code=400, detail="Message cannot be empty")
    
    try:
        # Convert chat history to ChatMessage objects
        history = [
            ChatMessage(role=msg.get("role", "user"), content=msg.get("content", ""))
            for msg in request.chat_history
        ]
        
        # Create context
        context = ChatContext(
            code=request.code,
            analysis_results=request.analysis_results,
            chat_history=history
        )
        
        # Generate response
        response_text = chat_handler.chat(request.message, context)
        
        return ChatResponse(response=response_text)
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error during chat: {str(e)}"
        )


if __name__ == "__main__":
    # Run the server
    uvicorn.run(app, host="0.0.0.0", port=8000)
