from fastapi import FastAPI, APIRouter, HTTPException, UploadFile, File
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import uuid
from datetime import datetime
import json
from openai import OpenAI
import asyncio


ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# OpenAI client
try:
    openai_client = OpenAI(
        api_key=os.environ['OPENAI_API_KEY']
    )
except Exception as e:
    print(f"Warning: OpenAI client initialization failed: {e}")
    openai_client = None

# Create the main app without a prefix
app = FastAPI()

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")


# Define Models
class ChatMessage(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    role: str  # "user" or "assistant" 
    content: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class Conversation(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    session_id: str
    messages: List[ChatMessage]
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None

class ChatResponse(BaseModel):
    message: str
    session_id: str
    conversation_id: str

class ObsidianNote(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str
    content: str
    file_path: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    tags: List[str] = []

class StatusCheck(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    client_name: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class StatusCheckCreate(BaseModel):
    client_name: str


# Helper functions
async def get_conversation_history(session_id: str, limit: int = 10) -> List[ChatMessage]:
    """Get recent conversation history for context"""
    conversations = await db.conversations.find(
        {"session_id": session_id}
    ).sort("updated_at", -1).limit(5).to_list(5)
    
    all_messages = []
    for conv in conversations:
        all_messages.extend(conv.get("messages", []))
    
    # Sort by timestamp and get most recent messages
    all_messages.sort(key=lambda x: x.get("timestamp", datetime.utcnow()), reverse=True)
    return all_messages[:limit]

async def search_relevant_notes(query: str, limit: int = 3) -> List[Dict]:
    """Simple text search in Obsidian notes"""
    try:
        # Try text search first
        notes = await db.obsidian_notes.find(
            {"$text": {"$search": query}}
        ).limit(limit).to_list(limit)
        return notes
    except Exception as e:
        # If text search fails (no index), fall back to simple regex search
        try:
            notes = await db.obsidian_notes.find(
                {"$or": [
                    {"title": {"$regex": query, "$options": "i"}},
                    {"content": {"$regex": query, "$options": "i"}}
                ]}
            ).limit(limit).to_list(limit)
            return notes
        except Exception as e2:
            logging.error(f"Note search error: {e2}")
            return []

async def generate_chat_response(messages: List[Dict], relevant_notes: List[Dict] = None) -> str:
    """Generate response using OpenAI with memory and notes context"""
    
    if openai_client is None:
        return "I apologize, but the OpenAI service is currently unavailable. The chat system is running but cannot generate AI responses at the moment."
    
    system_prompt = """You are an AI assistant with continuous memory and access to the user's personal knowledge base from their Obsidian notes. 

Key capabilities:
1. You remember all previous conversations in this session
2. You can access and reference the user's Obsidian notes when relevant
3. You maintain context across multiple conversations
4. You can help create new notes and logs based on our conversations

When responding:
- Reference previous conversations when relevant
- Cite Obsidian notes when they provide helpful context
- Offer to create new notes for important insights or information
- Be conversational but knowledgeable"""

    if relevant_notes:
        notes_context = "\n\nRELEVANT NOTES FROM YOUR OBSIDIAN VAULT:\n"
        for note in relevant_notes:
            notes_context += f"\n**{note.get('title', 'Untitled')}**:\n{note.get('content', '')[:500]}...\n"
        system_prompt += notes_context

    # Prepare messages for OpenAI
    openai_messages = [{"role": "system", "content": system_prompt}]
    openai_messages.extend(messages)

    try:
        response = openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=openai_messages,
            max_tokens=1000,
            temperature=0.7
        )
        return response.choices[0].message.content
    except Exception as e:
        logging.error(f"OpenAI API error: {e}")
        return f"I apologize, but I'm having trouble connecting to my language model right now. Error: {str(e)}"


# API Routes
@api_router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Main chat endpoint with continuous memory"""
    try:
        # Generate session ID if not provided
        session_id = request.session_id or str(uuid.uuid4())
        
        # Get conversation history for context
        history = await get_conversation_history(session_id)
        
        # Search for relevant Obsidian notes
        relevant_notes = await search_relevant_notes(request.message)
        
        # Prepare messages for OpenAI (convert history to dict format)
        messages = []
        for msg in reversed(history[-8:]):  # Last 8 messages for context
            messages.append({
                "role": msg.get("role", "user"),
                "content": msg.get("content", "")
            })
        
        # Add current message
        messages.append({"role": "user", "content": request.message})
        
        # Generate response
        response_content = await generate_chat_response(messages, relevant_notes)
        
        # Create new conversation record
        user_message = ChatMessage(role="user", content=request.message)
        assistant_message = ChatMessage(role="assistant", content=response_content)
        
        conversation = Conversation(
            session_id=session_id,
            messages=[user_message.dict(), assistant_message.dict()]
        )
        
        # Save to database
        await db.conversations.insert_one(conversation.dict())
        
        return ChatResponse(
            message=response_content,
            session_id=session_id,
            conversation_id=conversation.id
        )
        
    except Exception as e:
        logging.error(f"Chat error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/conversations/{session_id}")
async def get_conversation(session_id: str):
    """Get conversation history for a session"""
    conversations = await db.conversations.find(
        {"session_id": session_id}
    ).sort("created_at", 1).to_list(100)
    
    return {"conversations": conversations}

@api_router.post("/notes/upload")
async def upload_obsidian_notes(files: List[UploadFile] = File(...)):
    """Upload Obsidian notes (.md files)"""
    uploaded_notes = []
    
    for file in files:
        if not file.filename.endswith('.md'):
            continue
            
        content = await file.read()
        text_content = content.decode('utf-8')
        
        # Extract title from filename
        title = file.filename.replace('.md', '')
        
        note = ObsidianNote(
            title=title,
            content=text_content,
            file_path=file.filename,
            tags=[]  # Could extract hashtags from content later
        )
        
        await db.obsidian_notes.insert_one(note.dict())
        uploaded_notes.append(note.dict())
    
    # Create text index for search
    try:
        await db.obsidian_notes.create_index([("title", "text"), ("content", "text")])
    except:
        pass  # Index might already exist
    
    return {"uploaded_notes": len(uploaded_notes), "notes": uploaded_notes}

@api_router.get("/notes")
async def get_notes():
    """Get all Obsidian notes"""
    try:
        notes_cursor = db.obsidian_notes.find()
        notes = []
        async for note in notes_cursor:
            # Convert ObjectId to string for JSON serialization
            note['_id'] = str(note['_id'])
            notes.append(note)
        return {"notes": notes}
    except Exception as e:
        logging.error(f"Error getting notes: {e}")
        return {"notes": []}

@api_router.post("/notes/create")
async def create_note(title: str, content: str):
    """Create a new note"""
    note = ObsidianNote(
        title=title,
        content=content,
        file_path=f"{title}.md"
    )
    
    await db.obsidian_notes.insert_one(note.dict())
    return note.dict()

@api_router.delete("/conversations/clear/{session_id}")
async def clear_conversation(session_id: str):
    """Clear conversation history for a session"""
    result = await db.conversations.delete_many({"session_id": session_id})
    return {"deleted_count": result.deleted_count}

# Basic routes
@api_router.get("/")
async def root():
    return {"message": "Continuous Memory ChatGPT with Obsidian Integration"}

@api_router.post("/status", response_model=StatusCheck)
async def create_status_check(input: StatusCheckCreate):
    status_dict = input.dict()
    status_obj = StatusCheck(**status_dict)
    _ = await db.status_checks.insert_one(status_obj.dict())
    return status_obj

@api_router.get("/status", response_model=List[StatusCheck])
async def get_status_checks():
    status_checks = await db.status_checks.find().to_list(1000)
    return [StatusCheck(**status_check) for status_check in status_checks]

# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()