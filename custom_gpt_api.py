#!/usr/bin/env python3
"""
External API for Custom GPT Integration
Provides endpoints that OpenAI Custom GPT can call via Actions
"""

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
import uvicorn

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# FastAPI app for Custom GPT integration
custom_gpt_app = FastAPI(
    title="Custom GPT Knowledge API",
    description="External API for OpenAI Custom GPT to access Obsidian vault and GitHub repository",
    version="1.0.0"
)

# CORS middleware to allow OpenAI to call our API
custom_gpt_app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # OpenAI's servers need access
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database connection
MONGODB_URL = os.getenv('MONGO_URL', 'mongodb://localhost:27017')
client = AsyncIOMotorClient(MONGODB_URL)
db = client.chatgpt_memory

# Response models for Custom GPT
class ObsidianSearchResult(BaseModel):
    title: str
    content: str
    file_path: str
    relevance: str

class GitHubSearchResult(BaseModel):
    file_name: str
    file_path: str
    content: str
    repository: str

class KnowledgeSearchResponse(BaseModel):
    obsidian_results: List[ObsidianSearchResult]
    github_results: List[GitHubSearchResult]
    total_results: int
    summary: str

@custom_gpt_app.get("/")
async def root():
    """API health check"""
    return {
        "status": "operational",
        "service": "Custom GPT Knowledge API",
        "endpoints": [
            "/obsidian/search",
            "/github/search", 
            "/knowledge/search"
        ]
    }

@custom_gpt_app.get("/obsidian/search", response_model=Dict[str, Any])
async def search_obsidian_vault(
    query: str = Query(..., description="Search query for Obsidian vault"),
    limit: int = Query(5, description="Maximum number of results to return")
):
    """
    Search Obsidian vault for relevant notes
    This endpoint is designed to be called by Custom GPT Actions
    """
    try:
        logger.info(f"Obsidian search query: {query}")
        
        # Search the obsidian_notes collection
        search_results = []
        
        # Try text search first
        try:
            cursor = db.obsidian_notes.find({
                "$text": {"$search": query}
            }).limit(limit)
            
            async for note in cursor:
                search_results.append({
                    "title": note.get("title", "Untitled"),
                    "content": note.get("content", "")[:1000],  # Truncate for Custom GPT
                    "file_path": note.get("file_path", "unknown"),
                    "relevance": "high"
                })
        except:
            # Fallback to regex search
            cursor = db.obsidian_notes.find({
                "$or": [
                    {"title": {"$regex": query, "$options": "i"}},
                    {"content": {"$regex": query, "$options": "i"}}
                ]
            }).limit(limit)
            
            async for note in cursor:
                search_results.append({
                    "title": note.get("title", "Untitled"),
                    "content": note.get("content", "")[:1000],
                    "file_path": note.get("file_path", "unknown"),
                    "relevance": "medium"
                })
        
        response = {
            "query": query,
            "results": search_results,
            "total_found": len(search_results),
            "source": "obsidian_vault",
            "summary": f"Found {len(search_results)} notes matching '{query}' in your Obsidian vault"
        }
        
        logger.info(f"Obsidian search returned {len(search_results)} results")
        return response
        
    except Exception as e:
        logger.error(f"Error searching Obsidian vault: {e}")
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")

@custom_gpt_app.get("/github/search", response_model=Dict[str, Any])
async def search_github_repository(
    query: str = Query(..., description="Search query for GitHub repository"),
    repository: str = Query("flamesphere", description="Repository to search"),
    limit: int = Query(5, description="Maximum number of results to return")
):
    """
    Search GitHub repository for relevant files and content
    This endpoint is designed to be called by Custom GPT Actions
    """
    try:
        logger.info(f"GitHub search query: {query}, repo: {repository}")
        
        # Search repository files (this would be populated by the GitHub integration)
        search_results = []
        
        # For now, return a placeholder response indicating GitHub integration
        response = {
            "query": query,
            "repository": repository,
            "results": search_results,
            "total_found": 0,
            "source": "github_repository",
            "summary": f"GitHub repository search for '{query}' in {repository} repository"
        }
        
        logger.info(f"GitHub search returned {len(search_results)} results")
        return response
        
    except Exception as e:
        logger.error(f"Error searching GitHub repository: {e}")
        raise HTTPException(status_code=500, detail=f"GitHub search failed: {str(e)}")

@custom_gpt_app.get("/knowledge/search", response_model=Dict[str, Any])
async def search_all_knowledge(
    query: str = Query(..., description="Search query across all knowledge sources"),
    limit: int = Query(10, description="Maximum total results to return")
):
    """
    Search across both Obsidian vault and GitHub repository
    This is the main endpoint Custom GPT should use for comprehensive searches
    """
    try:
        logger.info(f"Knowledge search query: {query}")
        
        # Search Obsidian vault
        obsidian_results = []
        try:
            cursor = db.obsidian_notes.find({
                "$text": {"$search": query}
            }).limit(limit // 2)
            
            async for note in cursor:
                obsidian_results.append({
                    "title": note.get("title", "Untitled"),
                    "content": note.get("content", "")[:800],  # Shorter for combined results
                    "file_path": note.get("file_path", "unknown"),
                    "source": "obsidian_vault"
                })
        except:
            # Fallback to regex search
            cursor = db.obsidian_notes.find({
                "$or": [
                    {"title": {"$regex": query, "$options": "i"}},
                    {"content": {"$regex": query, "$options": "i"}}
                ]
            }).limit(limit // 2)
            
            async for note in cursor:
                obsidian_results.append({
                    "title": note.get("title", "Untitled"),
                    "content": note.get("content", "")[:800],
                    "file_path": note.get("file_path", "unknown"),
                    "source": "obsidian_vault"
                })
        
        # GitHub results (placeholder for now)
        github_results = []
        
        # Combine results
        all_results = obsidian_results + github_results
        
        response = {
            "query": query,
            "obsidian_results": obsidian_results,
            "github_results": github_results,
            "all_results": all_results,
            "total_found": len(all_results),
            "summary": f"Found {len(obsidian_results)} Obsidian notes and {len(github_results)} GitHub files matching '{query}'"
        }
        
        logger.info(f"Knowledge search returned {len(all_results)} total results")
        return response
        
    except Exception as e:
        logger.error(f"Error in knowledge search: {e}")
        raise HTTPException(status_code=500, detail=f"Knowledge search failed: {str(e)}")

@custom_gpt_app.get("/obsidian/get-note")
async def get_specific_obsidian_note(
    title: str = Query(..., description="Exact title of the note to retrieve"),
    file_path: Optional[str] = Query(None, description="Optional file path for more specific matching")
):
    """
    Get the full content of a specific Obsidian note by title
    Useful when Custom GPT wants to reference a specific note completely
    """
    try:
        logger.info(f"Getting specific note: {title}")
        
        # Search for exact title match
        query = {"title": {"$regex": f"^{title}$", "$options": "i"}}
        if file_path:
            query["file_path"] = file_path
            
        note = await db.obsidian_notes.find_one(query)
        
        if not note:
            raise HTTPException(status_code=404, detail=f"Note '{title}' not found")
        
        response = {
            "title": note.get("title", "Untitled"),
            "content": note.get("content", ""),
            "file_path": note.get("file_path", "unknown"),
            "created_at": note.get("created_at"),
            "tags": note.get("tags", []),
            "source": "obsidian_vault"
        }
        
        logger.info(f"Retrieved specific note: {title}")
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving note '{title}': {e}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve note: {str(e)}")

@custom_gpt_app.get("/obsidian/list-notes")
async def list_obsidian_notes(
    limit: int = Query(20, description="Number of notes to return"),
    offset: int = Query(0, description="Number of notes to skip")
):
    """
    List available Obsidian notes with titles and brief info
    Helps Custom GPT understand what's available in the vault
    """
    try:
        logger.info(f"Listing notes: limit={limit}, offset={offset}")
        
        # Get note list
        cursor = db.obsidian_notes.find({}, {
            "title": 1, 
            "file_path": 1, 
            "created_at": 1,
            "content": 1  # Get first bit of content for preview
        }).skip(offset).limit(limit)
        
        notes = []
        async for note in cursor:
            content_preview = note.get("content", "")[:200] + "..." if len(note.get("content", "")) > 200 else note.get("content", "")
            notes.append({
                "title": note.get("title", "Untitled"),
                "file_path": note.get("file_path", "unknown"),
                "created_at": note.get("created_at"),
                "content_preview": content_preview
            })
        
        # Get total count
        total_count = await db.obsidian_notes.count_documents({})
        
        response = {
            "notes": notes,
            "total_count": total_count,
            "returned_count": len(notes),
            "offset": offset,
            "limit": limit,
            "has_more": offset + len(notes) < total_count
        }
        
        logger.info(f"Listed {len(notes)} notes out of {total_count} total")
        return response
        
    except Exception as e:
        logger.error(f"Error listing notes: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to list notes: {str(e)}")

if __name__ == "__main__":
    # Run the Custom GPT API server
    uvicorn.run(custom_gpt_app, host="0.0.0.0", port=8002)