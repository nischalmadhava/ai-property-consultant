from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session
from app.config import get_db
from app.schemas import ChatRequest, ChatResponse, LocationResponse, MapDivision
from app.agents.orchestrator import AgentOrchestrator
import uuid
import asyncio

router = APIRouter(prefix="/api", tags=["chat"])

# Store for websocket connections
class ConnectionManager:
    def __init__(self):
        self.active_connections = {}
    
    async def connect(self, session_id: str, websocket: WebSocket):
        await websocket.accept()
        self.active_connections[session_id] = websocket
    
    async def disconnect(self, session_id: str):
        if session_id in self.active_connections:
            del self.active_connections[session_id]
    
    async def send_personal(self, session_id: str, message: str):
        if session_id in self.active_connections:
            await self.active_connections[session_id].send_text(message)

manager = ConnectionManager()

@router.post("/chat")
async def chat(
    request: ChatRequest,
    db: Session = Depends(get_db)
) -> ChatResponse:
    """
    Process chat message through the agentic workflow
    """
    
    if not request.message or not request.message.strip():
        raise HTTPException(status_code=400, detail="Message cannot be empty")
    
    user_id = request.user_id or "anonymous"
    session_id = request.session_id or str(uuid.uuid4())
    
    try:
        orchestrator = AgentOrchestrator(db)
        response = await orchestrator.process_query(
            user_query=request.message,
            user_id=user_id,
            session_id=session_id
        )
        return response
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing query: {str(e)}")

@router.websocket("/ws/chat/{session_id}")
async def websocket_chat(websocket: WebSocket, session_id: str, db: Session = Depends(get_db)):
    """
    WebSocket endpoint for real-time chat
    """
    
    await manager.connect(session_id, websocket)
    
    try:
        orchestrator = AgentOrchestrator(db)
        
        while True:
            data = await websocket.receive_text()
            
            # Send processing status
            await manager.send_personal(session_id, '{"type": "status", "message": "Processing your query..."}')
            
            # Process query
            response = await orchestrator.process_query(
                user_query=data,
                user_id="websocket_user",
                session_id=session_id
            )
            
            # Send response
            import json
            await manager.send_personal(
                session_id,
                json.dumps({
                    "type": "response",
                    "data": response.model_dump()
                })
            )
    
    except WebSocketDisconnect:
        manager.disconnect(session_id)
    except Exception as e:
        await manager.send_personal(session_id, f'{{"type": "error", "message": "{str(e)}"}}')
        manager.disconnect(session_id)

@router.get("/locations")
async def get_locations() -> LocationResponse:
    """
    Get Bangalore divisions and areas for map interface
    """
    
    divisions = [
        MapDivision(
            name="North Bangalore",
            bounds={
                "north": 13.2,
                "south": 13.0,
                "east": 77.7,
                "west": 77.5
            },
            description="Includes Yeshwanthpur, Whitefield, Hebbal, Yelahanka"
        ),
        MapDivision(
            name="South Bangalore",
            bounds={
                "north": 12.95,
                "south": 12.7,
                "east": 77.65,
                "west": 77.45
            },
            description="Includes Kanakapura, HSR Layout, Koramangala, Jayanagar"
        ),
        MapDivision(
            name="East Bangalore",
            bounds={
                "north": 13.05,
                "south": 12.8,
                "east": 77.8,
                "west": 77.6
            },
            description="Includes Marathahalli, Sarjapur, Varthur"
        ),
        MapDivision(
            name="West Bangalore",
            bounds={
                "north": 13.1,
                "south": 12.85,
                "east": 77.5,
                "west": 77.2
            },
            description="Includes Tumkur Road, Nelamangala, Chikballapur"
        ),
    ]
    
    areas = [
        "Kanakapura", "Anjanapura", "HSR Layout", "Koramangala",
        "Yeshwanthpur", "Whitefield", "Hebbal", "Yelahanka",
        "Marathahalli", "Sarjapur", "Varthur",
        "Tumkur Road", "Nelamangala"
    ]
    
    return LocationResponse(divisions=divisions, areas=areas)

@router.post("/search-by-location")
async def search_by_location(
    division: str,
    db: Session = Depends(get_db)
) -> ChatResponse:
    """
    Search properties by selecting a division on the map
    """
    
    query = f"Show me available properties in {division} Bangalore"
    
    orchestrator = AgentOrchestrator(db)
    response = await orchestrator.process_query(
        user_query=query,
        user_id="map_selection"
    )
    
    return response
