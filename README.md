# CareMixer Backend Test
## Features

- **Timeline API**: Manage and filter patient timeline events (notes and audits)
- **External Data API**: Fetch and search Pokemon data from PokeAPI with caching
- **Chat API**: Interactive chat bot with keyword-based responses
- **Chat UI**: Simple web interface for testing the chat functionality

## Setup Instructions

### Prerequisites

- Python 3.12+ installed
- pip package manager

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/AlexWarwick01/CaremixerBackendTest.git
   cd CaremixerBackendTest
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

### Running the Application

**Start the development server:**
```bash
uvicorn main:app --reload
```

Or run directly with Python:
```bash
python main.py
```

The API will be available at `http://localhost:8000`

### API Documentation

Once the server is running, access the interactive API documentation:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## API Endpoints

### Root
- `GET /` - Welcome page with endpoint information

### Timeline API (`/timeline`)
- `GET /timeline` - Get timeline events with optional filtering
  - Query params: `type` (Note/Audit), `limit` (default: 10)
  - Example: `/timeline?type=Audit&limit=5`
- `GET /timeline/{event_id}` - Get specific timeline event by ID

### External Data API (`/external_data`)
- `GET /external_data` - Get paginated Pokemon data
  - Query params: `page` (default: 1), `limit` (default: 10, max: 50), `search` (optional)
  - Example: `/external_data?page=2&limit=20`
  - Example: `/external_data?search=char` (searches across all Pokemon)
- `GET /external_data/{pokemon_name}` - Get specific Pokemon by name
  - Example: `/external_data/charmander`

### Chat API (`/chat`)
- `GET /chat` - Get chat message history
  - Query params: `limit` (optional), `sender` (optional)
- `POST /chat` - Send a chat message and get bot response
  - Body: `{"sender": "User", "message": "Hello"}`

### Chat UI
- `GET /chat-ui` - Simple web interface for chatting
- This is the best way to test the chat functionality interactively.

## Architecture & Design Choices

### Framework: FastAPI

**Why FastAPI?**
- **High Performance**: Built on Starlette and Pydantic, one of the fastest Python frameworks
- **Async Support**: Native async/await support for concurrent operations (crucial for external API calls)
- **Automatic Documentation**: Built-in Swagger UI and ReDoc generation
- **Challenging and Fun**: I have no experience with FastAPI, so it was a great opportunity to learn and apply it in a practical scenario.

### Project Structure

```
CaremixerBackendTest/
├── main.py              # FastAPI application entry point and router configuration
├── timeline.py          # Timeline events module with in-memory storage
├── external_api.py      # Pokemon API integration with caching
├── chat.py              # Chat bot module with keyword-based responses
├── chat.html            # Simple frontend for chat interface
├── requirements.txt     # Python dependencies
└── README.md           # Project documentation
```

### State Management & Caching Strategy

#### 1. **In-Memory Storage**
All data is stored in memory using Python lists and dictionaries:
- **Timeline Events**: `TIMELINE_EVENTS` list stores pre-populated patient timeline data
- **Chat Messages**: `CHAT_MESSAGES` list stores conversation history
- **Pokemon Cache**: `POKEMON_CACHE` dictionary caches fetched Pokemon data

**Rationale**: 
- Simple and fast for a test/demo application
- No database setup required
- Data persists during server runtime
- Easy to reset by restarting the server

**Trade-offs**:
- Data is lost on server restart (acceptable for demo purposes)
- Not suitable for production (would use PostgreSQL, MongoDB, or Redis)
- Memory grows with usage (limited by available RAM)
- I attempted to use LRU but It was becoming extremely complex for this simple use case and I would have spent all night on it

#### 2. **Caching Strategy for External API**

**Implementation**:
```python
POKEMON_CACHE = {}  # Simple in-memory cache

async def fetch_pokemon_details(name: str) -> Optional[Pokemon]:
    # Check cache first
    if name.lower() in POKEMON_CACHE:
        return POKEMON_CACHE[name.lower()]
    
    # Fetch from API and cache result
    pokemon = await fetch_from_api(name)
    POKEMON_CACHE[name.lower()] = pokemon
    return pokemon
```

**Benefits**:
- Reduces external API calls (PokeAPI rate limiting)
- Faster response times for repeated requests
- Minimizes network latency

**Search Optimization**:
- When searching, fetches up to 1000 Pokemon names in one request
- Filters locally for instant search results
- Applies pagination to filtered results


### Design Patterns

1. **Router Pattern**: Modular route organization using FastAPI's `APIRouter`
   - Each feature (timeline, external_api, chat) is a separate module
   - Clean separation of concerns
   - Easy to maintain and extend

2. **Pydantic Models**: Strong data validation and serialization
   - `TimelineEvent`, `Pokemon`, `ChatMessage` models
   - Automatic request/response validation
   - Type-safe code with IDE support

3. **Middleware**: CORS enabled for frontend communication
   - Allows chat UI to communicate with API
   - Configurable for production (currently allows all origins)

4. **Error Handling**: Comprehensive exception handling
   - HTTP exceptions with proper status codes
   - Timeout handling for external API requests
   - Graceful degradation (filters out failed fetches)


**Example curl commands**:
```bash
# Get timeline events
curl "http://localhost:8000/timeline?limit=5"

# Search Pokemon
curl "http://localhost:8000/external_data?search=pikachu"

# Send chat message
curl -X POST "http://localhost:8000/chat" \
  -H "Content-Type: application/json" \
  -d '{"sender":"User","message":"hello"}'
```


## Dependencies

- **fastapi**: Modern web framework for building APIs
- **uvicorn**: ASGI server for running FastAPI
- **httpx**: Async HTTP client for external API requests
- **pydantic**: Data validation using Python type hints

