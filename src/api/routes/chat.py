"""LLM chat refinement routes."""

from fastapi import APIRouter, HTTPException
from src.api.models import RefineRequest, RefineResponse
from src.generators.twitter_generator import TwitterGenerator
from src.rag.retriever import Retriever
from src.rag.vector_store import VectorStore
from src.llm.openai_client import OpenAIClient
from src.utils.config import Config

router = APIRouter(prefix="/chat", tags=["chat"])


def get_generator():
    """Initialize the Twitter generator with dependencies."""
    vector_store = VectorStore()
    retriever = Retriever(vector_store)
    llm_client = OpenAIClient()
    return TwitterGenerator(llm_client, retriever, Config)


@router.post("/refine", response_model=RefineResponse)
async def refine_content(request: RefineRequest):
    """
    Refine post content using LLM.

    Examples:
    - "make this about courage"
    - "make it shorter"
    - "add a question at the end"
    - "make it more casual"
    """
    try:
        generator = get_generator()

        result = generator.refine(
            content=request.content,
            instruction=request.instruction,
        )

        if result.get("error"):
            raise HTTPException(status_code=500, detail=result["error"])

        return RefineResponse(
            content=result.get("content", ""),
            original=result.get("original", request.content),
            instruction=result.get("instruction", request.instruction),
            model=result.get("model", "gpt4"),
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/suggest")
async def suggest_improvements(content: str):
    """Get LLM suggestions for improving a post."""
    try:
        generator = get_generator()

        suggestions = []

        prompts = [
            ("hook", "Suggest a more engaging hook for this stoic post"),
            ("clarity", "Suggest how to make this clearer and more accessible"),
            ("action", "Suggest an actionable takeaway to add"),
        ]

        for suggestion_type, instruction in prompts:
            result = generator.refine(
                content=content,
                instruction=instruction,
            )
            if not result.get("error"):
                suggestions.append({
                    "type": suggestion_type,
                    "suggestion": result.get("content", ""),
                })

        return {"suggestions": suggestions}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/virtue-shift")
async def shift_virtue(content: str, target_virtue: str):
    """Reframe content to emphasize a different stoic virtue."""
    try:
        generator = get_generator()

        virtue_descriptions = {
            "wisdom": "practical wisdom and good judgment",
            "courage": "bravery and facing fears",
            "justice": "fairness and treating others well",
            "temperance": "self-control and moderation",
        }

        instruction = f"Reframe this to emphasize {virtue_descriptions.get(target_virtue, target_virtue)}"

        result = generator.refine(
            content=content,
            instruction=instruction,
        )

        if result.get("error"):
            raise HTTPException(status_code=500, detail=result["error"])

        return {
            "original": content,
            "shifted": result.get("content", ""),
            "target_virtue": target_virtue,
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
