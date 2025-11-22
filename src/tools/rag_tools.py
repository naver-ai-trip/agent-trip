"""RAG (Retrieval-Augmented Generation) tools for travel document search."""

import httpx
import logging
from typing import List, Dict, Any, Optional
from langchain_core.tools import tool
from pinecone import Pinecone, ServerlessSpec

from src.config import settings

logger = logging.getLogger(__name__)

# Initialize Pinecone client (lazy initialization)
_pinecone_client = None
_pinecone_index = None


def get_pinecone_index():
    """Get or initialize Pinecone index."""
    global _pinecone_client, _pinecone_index
    
    if _pinecone_index is None:
        if not settings.PINECONE_API_KEY:
            logger.warning("Pinecone API key not configured. RAG features will be disabled.")
            return None
        
        _pinecone_client = Pinecone(api_key=settings.PINECONE_API_KEY)
        
        # Check if index exists, create if not
        existing_indexes = _pinecone_client.list_indexes()
        if settings.PINECONE_INDEX_NAME not in [idx.name for idx in existing_indexes]:
            logger.info(f"Creating Pinecone index: {settings.PINECONE_INDEX_NAME}")
            _pinecone_client.create_index(
                name=settings.PINECONE_INDEX_NAME,
                dimension=settings.EMBEDDING_DIMENSION,
                metric="cosine",
                spec=ServerlessSpec(
                    cloud="aws",
                    region=settings.PINECONE_ENVIRONMENT or "us-east-1"
                )
            )
        
        _pinecone_index = _pinecone_client.Index(settings.PINECONE_INDEX_NAME)
        logger.info(f"Connected to Pinecone index: {settings.PINECONE_INDEX_NAME}")
    
    return _pinecone_index


async def call_naver_clova_api(
    endpoint: str,
    payload: Dict[str, Any],
    request_id: Optional[str] = None
) -> Dict[str, Any]:
    """Call Naver Clova Studio API.
    
    Args:
        endpoint: API endpoint path (e.g., "/v1/api-tools/embedding/v2")
        payload: Request payload
        request_id: Optional request ID for tracking
    
    Returns:
        API response as dictionary
    
    Note:
        Uses new streaming base URL (https://clovastudio.stream.ntruss.com/)
        For test API keys: Only requires Authorization header
        For service API keys: Requires both Authorization and X-NCP-APIGW-API-KEY
    """
    # Use new streaming base URL (recommended by Clova Studio docs)
    base_url = "https://clovastudio.stream.ntruss.com"
    url = f"{base_url}{endpoint}"
    
    headers = {
        "Content-Type": "application/json",
    }
    
    # Add authentication headers
    if settings.NAVER_CLOVA_API_KEY:
        # Test API key: Authorization Bearer header (starts with 'nv-')
        headers["Authorization"] = f"Bearer {settings.NAVER_CLOVA_API_KEY}"
    else:
        raise ValueError("NAVER_CLOVA_API_KEY is required")
    
    # Service API key: Additional X-NCP-APIGW-API-KEY header (optional for test keys)
    if settings.NAVER_CLOVA_APIGW_API_KEY and settings.NAVER_CLOVA_APIGW_API_KEY != "your_apigw_key_here":
        headers["X-NCP-APIGW-API-KEY"] = settings.NAVER_CLOVA_APIGW_API_KEY
    
    # Optional request ID for tracking
    if request_id or settings.NAVER_CLOVA_REQUEST_ID:
        headers["X-NCP-CLOVASTUDIO-REQUEST-ID"] = request_id or settings.NAVER_CLOVA_REQUEST_ID
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(url, json=payload, headers=headers)
            response.raise_for_status()
            return response.json()
    except httpx.HTTPError as e:
        logger.error(f"Naver Clova API error: {e}")
        if hasattr(e, 'response') and e.response is not None:
            logger.error(f"Response status: {e.response.status_code}")
            logger.error(f"Response body: {e.response.text}")
        raise


@tool
async def embed_query(query: str) -> List[float]:
    """Generate embedding vector for a search query using Naver Embedding v2 (bge-m3).
    
    Args:
        query: Text query to embed (max 8192 tokens)
    
    Returns:
        1024-dimensional embedding vector
    """
    logger.info(f"Embedding query: {query[:100]}...")
    
    payload = {"text": query}
    
    try:
        response = await call_naver_clova_api("/v1/api-tools/embedding/v2", payload)
        
        if response.get("status", {}).get("code") == "20000":
            embedding = response["result"]["embedding"]
            token_count = response["result"]["inputTokens"]
            logger.info(f"Generated embedding with {token_count} tokens")
            return embedding
        else:
            logger.error(f"Embedding API error: {response}")
            raise Exception(f"Embedding failed: {response.get('status', {}).get('message')}")
    
    except Exception as e:
        logger.error(f"Failed to generate embedding: {e}")
        raise


@tool
async def search_vector_db(
    query_embedding: List[float],
    top_k: int = None,
    filters: Optional[Dict[str, Any]] = None
) -> List[Dict[str, Any]]:
    """Search Pinecone vector database for relevant document chunks.
    
    Args:
        query_embedding: 1024-dimensional query vector
        top_k: Number of results to return (default: RAG_TOP_K from config)
        filters: Metadata filters (e.g., {"location": "Seoul", "category": "culture"})
    
    Returns:
        List of matching documents with scores and metadata
    """
    index = get_pinecone_index()
    if index is None:
        logger.warning("Pinecone not configured, returning empty results")
        return []
    
    top_k = top_k or settings.RAG_TOP_K
    
    try:
        # Query Pinecone
        results = index.query(
            vector=query_embedding,
            top_k=top_k,
            include_metadata=True,
            filter=filters
        )
        
        # Format results
        documents = []
        for match in results.matches:
            # Extract text content from metadata (support multiple field names)
            text_content = (
                match.metadata.get("text") or 
                match.metadata.get("full_content") or 
                match.metadata.get("content") or 
                ""
            )
            
            documents.append({
                "id": match.id,
                "score": match.score,
                "text": text_content,
                "metadata": {
                    "document_id": match.metadata.get("document_id"),
                    "chunk_index": match.metadata.get("chunk_index"),
                    "location": match.metadata.get("location"),
                    "category": match.metadata.get("category"),
                    "page": match.metadata.get("page"),
                    "title": match.metadata.get("title"),
                    "language": match.metadata.get("language"),
                }
            })
        
        logger.info(f"Vector search returned {len(documents)} documents")
        return documents
    
    except Exception as e:
        logger.error(f"Vector search failed: {e}")
        return []


@tool
async def rerank_documents(
    query: str,
    documents: List[Dict[str, Any]],
    max_tokens: int = None
) -> Dict[str, Any]:
    """Rerank retrieved documents using Naver Reranker API.
    
    Args:
        query: Original user query
        documents: List of documents from vector search
        max_tokens: Maximum tokens for reranking (default: RAG_MAX_TOKENS)
    
    Returns:
        Reranked result with cited documents and suggested queries
    """
    logger.info(f"Reranking {len(documents)} documents for query: {query[:100]}...")
    
    max_tokens = max_tokens or settings.RAG_MAX_TOKENS
    
    # Format documents for reranker
    reranker_docs = [
        {
            "id": doc["id"],
            "doc": doc["text"]
        }
        for doc in documents
    ]
    
    payload = {
        "documents": reranker_docs,
        "query": query,
        "maxTokens": max_tokens
    }
    
    try:
        response = await call_naver_clova_api("/v1/api-tools/reranker", payload)
        
        if response.get("status", {}).get("code") == "20000":
            result = response["result"]
            
            # Enhance cited documents with original metadata
            cited_docs = result.get("citedDocuments", [])
            for cited in cited_docs:
                # Find original document to get metadata
                original = next((d for d in documents if d["id"] == cited["id"]), None)
                if original:
                    cited["metadata"] = original["metadata"]
                    cited["score"] = original["score"]
            
            return {
                "result": result.get("result", ""),
                "cited_documents": cited_docs,
                "suggested_queries": result.get("suggestedQueries", []),
                "usage": result.get("usage", {})
            }
        else:
            logger.error(f"Reranker API error: {response}")
            return {
                "result": "",
                "cited_documents": [],
                "suggested_queries": [],
                "usage": {}
            }
    
    except Exception as e:
        logger.error(f"Reranking failed: {e}")
        return {
            "result": "",
            "cited_documents": [],
            "suggested_queries": [],
            "usage": {}
        }


@tool
async def rag_reasoning(
    query: str,
    search_results: List[Dict[str, Any]],
    conversation_history: Optional[List[Dict[str, str]]] = None
) -> Dict[str, Any]:
    """Use Naver RAG Reasoning API to generate contextual answer from retrieved documents.
    
    Args:
        query: User's question
        search_results: Retrieved and reranked documents
        conversation_history: Previous conversation messages
    
    Returns:
        RAG-generated response with tool calls or final answer
    """
    logger.info(f"RAG reasoning for query: {query[:100]}...")
    
    # Build messages array
    messages = conversation_history or []
    messages.append({
        "role": "user",
        "content": query
    })
    
    # Define the travel document retrieval tool
    tools = [
        {
            "type": "function",
            "function": {
                "name": "travel_document_search",
                "description": (
                    "Search travel documents for information about Korean destinations, "
                    "culture, customs, history, travel tips, local insights, and practical advice. "
                    "Use this when the user asks about cultural etiquette, historical context, "
                    "best practices, local transportation, seasonal information, or travel recommendations."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "The refined search query based on user's question"
                        }
                    },
                    "required": ["query"]
                }
            }
        }
    ]
    
    payload = {
        "messages": messages,
        "tools": tools,
        "toolChoice": "auto",
        "topP": 0.8,
        "topK": 0,
        "maxTokens": settings.RAG_MAX_TOKENS,
        "temperature": settings.RAG_TEMPERATURE,
        "repetitionPenalty": 1.1,
        "stop": [],
        "seed": 0,
        "includeAiFilters": True
    }
    
    try:
        response = await call_naver_clova_api("/v1/api-tools/rag-reasoning", payload)
        
        if response.get("status", {}).get("code") == "20000":
            result = response["result"]
            message = result.get("message", {})
            
            return {
                "role": message.get("role", "assistant"),
                "content": message.get("content", ""),
                "thinking_content": message.get("thinkingContent"),
                "tool_calls": message.get("toolCalls", []),
                "usage": result.get("usage", {})
            }
        else:
            logger.error(f"RAG Reasoning API error: {response}")
            return {
                "role": "assistant",
                "content": "I apologize, but I couldn't process your request at the moment.",
                "thinking_content": None,
                "tool_calls": [],
                "usage": {}
            }
    
    except Exception as e:
        logger.error(f"RAG reasoning failed: {e}")
        return {
            "role": "assistant",
            "content": "I apologize, but I couldn't process your request at the moment.",
            "thinking_content": None,
            "tool_calls": [],
            "usage": {}
        }


@tool
async def fetch_document_metadata(document_id: str) -> Optional[Dict[str, Any]]:
    """Fetch document metadata from Laravel backend.
    
    Args:
        document_id: Document identifier
    
    Returns:
        Document metadata (title, author, URL, etc.)
    """
    # TODO: Replace with your actual Laravel API endpoint
    # This is a placeholder - you'll provide the real endpoint later
    logger.info(f"Fetching metadata for document: {document_id}")
    
    try:
        url = f"{settings.BE_API_BASE}/documents/{document_id}"
        
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(url)
            response.raise_for_status()
            
            data = response.json()
            return {
                "id": document_id,
                "title": data.get("title"),
                "author": data.get("author"),
                "category": data.get("category"),
                "file_url": data.get("file_url"),
                "upload_date": data.get("upload_date"),
                "page_count": data.get("page_count"),
            }
    
    except Exception as e:
        logger.error(f"Failed to fetch document metadata: {e}")
        return None


# RAG Keywords for intent detection
RAG_KEYWORDS = [
    # Culture & Customs
    "culture", "custom", "etiquette", "tradition", "manner", "behavior", 
    "respect", "bow", "礼儀", "예절", "문화",
    
    # History
    "history", "historical", "heritage", "ancient", "dynasty", "king", "queen",
    "palace", "temple", "museum", "역사", "유산",
    
    # Travel Tips
    "tip", "advice", "recommendation", "guide", "how to", "best time", 
    "season", "weather", "avoid", "준비", "꿀팁",
    
    # Local Insights
    "local", "insider", "secret", "hidden", "authentic", "traditional",
    "transportation", "subway", "bus", "taxi", "현지", "교통",
    
    # Practical Information
    "visa", "currency", "money", "sim card", "wifi", "emergency", 
    "hospital", "pharmacy", "비자", "환전",
]


def is_rag_query(query: str) -> bool:
    """Detect if a query should use RAG (travel knowledge) vs regular search.
    
    Args:
        query: User's question
    
    Returns:
        True if query is about culture/history/tips/insights
    """
    query_lower = query.lower()
    
    # Check for RAG keywords
    for keyword in RAG_KEYWORDS:
        if keyword in query_lower:
            logger.info(f"RAG query detected (keyword: {keyword})")
            return True
    
    # Check for question patterns about knowledge/information
    knowledge_patterns = [
        "what is", "what are", "tell me about", "explain", "why",
        "how does", "how do", "can you explain", "what's the",
        "알려줘", "설명해", "뭐야", "어때"
    ]
    
    for pattern in knowledge_patterns:
        if pattern in query_lower:
            # But not if it's asking for place recommendations
            if not any(word in query_lower for word in ["recommend", "suggestion", "find", "search", "추천"]):
                logger.info(f"RAG query detected (pattern: {pattern})")
                return True
    
    return False
