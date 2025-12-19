"""Content generation routes."""

from fastapi import APIRouter, HTTPException
from src.api.models import (
    GenerateRequest,
    GenerateReplyRequest,
    GenerateResponse,
)
from src.db.posts import PostsDB
from src.generators.twitter_generator import TwitterGenerator
from src.llm.openai_client import OpenAIClient
from src.utils.config import Config

# Optional RAG imports - may not be available on all Python versions
try:
    from src.rag.retriever import Retriever
    from src.rag.vector_store import VectorStore
    RAG_AVAILABLE = True
except ImportError:
    Retriever = None
    VectorStore = None
    RAG_AVAILABLE = False

router = APIRouter(prefix="/generate", tags=["generate"])


def get_generator():
    """Initialize the Twitter generator with dependencies."""
    retriever = None
    if RAG_AVAILABLE:
        vector_store = VectorStore()
        retriever = Retriever(vector_store)
    llm_client = OpenAIClient()
    return TwitterGenerator(llm_client, retriever, Config)


@router.post("", response_model=GenerateResponse)
async def generate_post(request: GenerateRequest):
    """Generate a new stoic-themed post using 70/20/10 engagement strategy."""
    try:
        generator = get_generator()

        result = generator.generate(
            topic=request.topic or "stoic wisdom for daily life",
            include_examples=request.include_examples,
            format_type=request.format_type,
            virtue=request.virtue,
        )

        if result.get("error"):
            raise HTTPException(status_code=500, detail=result["error"])

        tweets = result.get("tweets", [])
        content = result.get("content", "")
        format_type = result.get("format_type", "short")
        virtue = result.get("virtue", "general")
        tweet_count = result.get("tweet_count", 1)

        posts_db = PostsDB()
        post_data = {
            "content": content,
            "topic": result.get("topic", request.topic),
            "post_type": "original",
            "format_type": format_type,
            "virtue": virtue,
            "tweets": tweets,
            "tweet_count": tweet_count,
            "model": result.get("model", "gpt4"),
            "citations": {"sources": result.get("citations", [])},
            "status": "pending_review"
        }
        saved_post = posts_db.create(post_data)

        citations_str = result.get("citations", "")
        citations_list = None
        if citations_str:
            citations_list = [{"source": line.strip("- ").strip()}
                             for line in citations_str.strip().split("\n")[1:]
                             if line.strip()]

        return GenerateResponse(
            content=content,
            tweets=tweets,
            format_type=format_type,
            virtue=virtue,
            tweet_count=tweet_count,
            topic=result.get("topic", request.topic),
            model=result.get("model", "gpt4"),
            citations=citations_list,
            post_id=saved_post.get("id") if saved_post else None
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/reply", response_model=GenerateResponse)
async def generate_reply(request: GenerateReplyRequest):
    """Generate a stoic reply to a tweet (always 280 characters or less)."""
    try:
        generator = get_generator()

        result = generator.generate_reply(
            original_content=request.tweet_text,
            username=request.username or "user",
            virtue=request.virtue,
        )

        if result.get("error"):
            raise HTTPException(status_code=500, detail=result["error"])

        reply_content = result.get("content", "")
        tweets = result.get("tweets", [reply_content] if reply_content else [])
        virtue = result.get("virtue", "general")

        posts_db = PostsDB()
        post_data = {
            "content": reply_content,
            "topic": f"Reply to @{request.username}" if request.username else "Trending reply",
            "post_type": "reply",
            "format_type": "reply",
            "virtue": virtue,
            "tweets": tweets,
            "tweet_count": 1,
            "reply_to_tweet_id": request.tweet_id,
            "reply_to_content": request.tweet_text,
            "reply_to_username": request.username,
            "model": result.get("model", "gpt4"),
            "citations": {"sources": result.get("citations", [])},
            "status": "pending_review"
        }
        saved_post = posts_db.create(post_data)

        citations_str = result.get("citations", "")
        citations_list = None
        if citations_str:
            citations_list = [{"source": line.strip("- ").strip()}
                             for line in citations_str.strip().split("\n")[1:]
                             if line.strip()]

        return GenerateResponse(
            content=reply_content,
            tweets=tweets,
            format_type="reply",
            virtue=virtue,
            tweet_count=1,
            topic=post_data["topic"],
            model=result.get("model", "gpt4"),
            citations=citations_list,
            post_id=saved_post.get("id") if saved_post else None
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
