# Chat Simulation API Module
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List
from datetime import datetime
import random
import asyncio

router = APIRouter()

# Model for Chat Messages
class ChatMessage(BaseModel):
    id: int
    sender: str
    message: str
    timestamp: datetime

# Model for Incoming Chat Request
class ChatRequest(BaseModel):
    sender: str
    message: str

# Model for Chat Response
class ChatResponse(BaseModel):
    reply: ChatMessage
    bot_response: ChatMessage


# In-memory storage for chat messages
CHAT_MESSAGES: List[ChatMessage] = []
message_id_counter = 1

# Predefined bot replies
# These are extremely generic
BOT_REPLIES = [
    "Hello! How can I assist you today?",
    "I'm here to help! What do you need?",
    "Can you please provide more details?",
    "Thank you for reaching out!",
    "I'm glad to assist you with that.",
    "Let me check that for you.",
    "Could you clarify your question?",
    "I'm here to support you!",
    "What else can I do for you?",
    "Feel free to ask me anything!"
]

# Keyword-based replies
# These replies are triggered if certain keywords are found in the user's message
# In future, this could be expanded with more sophisticated NLP techniques
KEYWORD_REPLIES = {
    "hello": "Hi there! How can I help you?",
    "help": "Sure! What do you need assistance with?",
    "thanks": "You're welcome! Let me know if you have more questions.",
    "problem": "I'm sorry to hear that. Can you tell me more about the problem?",
    "issue": "Let's see how we can resolve that issue together."
}


def generate_bot_reply(user_message: str) -> str:
    
    # Convert message to lowercase for keyword matching
    message_lower = user_message.lower()

    # Check for keyword-based replies first
    for keyword, reply in KEYWORD_REPLIES.items():
        if keyword in message_lower:
            return reply
    # If no keywords matched, return a random generic reply
    return random.choice(BOT_REPLIES)

def create_chat_message(sender: str, message: str) -> ChatMessage:
    global message_id_counter
    chat_message = ChatMessage(
        id=message_id_counter,
        sender=sender,
        message=message,
        timestamp=datetime.now().isoformat()
    )
    message_id_counter += 1
    return chat_message

@router.get("/", response_model=List[ChatMessage])
async def get_chat_messages(limit: int = None, sender: str = None):
    
    # Retrieve chat messages with optional filtering by sender and limit.
  
    messages = CHAT_MESSAGES.copy()
    if sender:
        messages = [msg for msg in messages if msg.sender == sender]
    messages = sorted(messages, key=lambda x: x.timestamp, reverse=True)
    if limit:
        messages = messages[:limit]
    return messages

@router.post("/", response_model=ChatResponse)
async def post_chat_message(chat_request: ChatRequest):
    # Validate Input
    if not chat_request.message.strip():
        raise HTTPException(status_code=400, detail="Message cannot be empty")
    
    # Create User Message
    user_message = create_chat_message(sender=chat_request.sender, message=chat_request.message)
    CHAT_MESSAGES.append(user_message)

    # Simulate Bot Reply Generation Delay
    await asyncio.sleep(1)  # Simulate processing time

    # Generate Bot Reply
    bot_reply_text = generate_bot_reply(chat_request.message)
    bot_message = create_chat_message(sender="Bot", message=bot_reply_text)
    CHAT_MESSAGES.append(bot_message)
    return ChatResponse(reply=user_message, bot_response=bot_message)
   


