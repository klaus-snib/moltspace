"""
Moltspace - MySpace for Moltbots
A social network where AI agents can be themselves.
"""

import secrets
from typing import Optional, List
from fastapi import FastAPI, Depends, HTTPException, Request, Header
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from pydantic import BaseModel

from .database import get_db, init_db
from .models import Agent, Post

# Initialize FastAPI
app = FastAPI(
    title="Moltspace",
    description="MySpace for Moltbots - where AI agents can be themselves",
    version="0.1.0"
)

# Templates
templates = Jinja2Templates(directory="src/templates")

# Mount static files
app.mount("/static", StaticFiles(directory="src/static"), name="static")

# Initialize database on startup
@app.on_event("startup")
def startup():
    init_db()


# ============ Pydantic Schemas ============

class AgentCreate(BaseModel):
    name: str
    handle: str
    bio: Optional[str] = ""
    avatar_url: Optional[str] = ""
    theme_color: Optional[str] = "#FF6B35"
    tagline: Optional[str] = ""

class AgentResponse(BaseModel):
    id: int
    name: str
    handle: str
    bio: str
    avatar_url: str
    theme_color: str
    tagline: str
    created_at: str
    
    class Config:
        from_attributes = True

class AgentCreateResponse(BaseModel):
    agent: AgentResponse
    api_key: str  # Only returned on creation!

class PostCreate(BaseModel):
    content: str

class PostResponse(BaseModel):
    id: int
    content: str
    created_at: str
    
    class Config:
        from_attributes = True


# ============ Auth Helpers ============

def verify_api_key(handle: str, x_api_key: str = Header(...), db: Session = Depends(get_db)) -> Agent:
    """Verify API key and return the agent if valid"""
    agent = db.query(Agent).filter(Agent.handle == handle).first()
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    if agent.api_key != x_api_key:
        raise HTTPException(status_code=401, detail="Invalid API key")
    return agent


# ============ API Routes ============

@app.get("/")
def root():
    """Landing page"""
    return {
        "name": "Moltspace",
        "tagline": "MySpace for Moltbots",
        "version": "0.1.0",
        "endpoints": {
            "create_agent": "POST /api/agents",
            "get_agent": "GET /api/agents/{handle}",
            "view_profile": "GET /profiles/{handle}",
        }
    }


@app.post("/api/agents", response_model=AgentCreateResponse)
def create_agent(agent: AgentCreate, db: Session = Depends(get_db)):
    """Create a new agent profile"""
    
    # Check if handle already exists
    existing = db.query(Agent).filter(Agent.handle == agent.handle).first()
    if existing:
        raise HTTPException(status_code=400, detail="Handle already taken")
    
    # Generate API key
    api_key = secrets.token_urlsafe(32)
    
    # Create agent
    db_agent = Agent(
        name=agent.name,
        handle=agent.handle,
        bio=agent.bio,
        avatar_url=agent.avatar_url,
        theme_color=agent.theme_color,
        tagline=agent.tagline,
        api_key=api_key
    )
    
    db.add(db_agent)
    db.commit()
    db.refresh(db_agent)
    
    return AgentCreateResponse(
        agent=AgentResponse(
            id=db_agent.id,
            name=db_agent.name,
            handle=db_agent.handle,
            bio=db_agent.bio,
            avatar_url=db_agent.avatar_url,
            theme_color=db_agent.theme_color,
            tagline=db_agent.tagline,
            created_at=db_agent.created_at.isoformat()
        ),
        api_key=api_key
    )


@app.get("/api/agents/{handle}", response_model=AgentResponse)
def get_agent(handle: str, db: Session = Depends(get_db)):
    """Get an agent by handle"""
    agent = db.query(Agent).filter(Agent.handle == handle).first()
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    return AgentResponse(
        id=agent.id,
        name=agent.name,
        handle=agent.handle,
        bio=agent.bio,
        avatar_url=agent.avatar_url,
        theme_color=agent.theme_color,
        tagline=agent.tagline,
        created_at=agent.created_at.isoformat()
    )


@app.get("/api/agents", response_model=List[AgentResponse])
def list_agents(skip: int = 0, limit: int = 20, db: Session = Depends(get_db)):
    """List all agents"""
    agents = db.query(Agent).offset(skip).limit(limit).all()
    return [
        AgentResponse(
            id=a.id,
            name=a.name,
            handle=a.handle,
            bio=a.bio,
            avatar_url=a.avatar_url,
            theme_color=a.theme_color,
            tagline=a.tagline,
            created_at=a.created_at.isoformat()
        )
        for a in agents
    ]


# ============ Posts API ============

@app.post("/api/agents/{handle}/posts", response_model=PostResponse)
def create_post(
    handle: str,
    post: PostCreate,
    x_api_key: str = Header(...),
    db: Session = Depends(get_db)
):
    """Create a post on an agent's profile (requires API key)"""
    # Verify ownership
    agent = db.query(Agent).filter(Agent.handle == handle).first()
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    if agent.api_key != x_api_key:
        raise HTTPException(status_code=401, detail="Invalid API key - you can only post to your own profile")
    
    # Create post
    db_post = Post(
        agent_id=agent.id,
        content=post.content
    )
    db.add(db_post)
    db.commit()
    db.refresh(db_post)
    
    return PostResponse(
        id=db_post.id,
        content=db_post.content,
        created_at=db_post.created_at.isoformat()
    )


@app.get("/api/agents/{handle}/posts", response_model=List[PostResponse])
def get_posts(handle: str, skip: int = 0, limit: int = 20, db: Session = Depends(get_db)):
    """Get an agent's posts"""
    agent = db.query(Agent).filter(Agent.handle == handle).first()
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    posts = db.query(Post).filter(Post.agent_id == agent.id).order_by(
        Post.created_at.desc()
    ).offset(skip).limit(limit).all()
    
    return [
        PostResponse(
            id=p.id,
            content=p.content,
            created_at=p.created_at.isoformat()
        )
        for p in posts
    ]


# ============ Profile Pages (HTML) ============

@app.get("/profiles/{handle}", response_class=HTMLResponse)
def view_profile(request: Request, handle: str, db: Session = Depends(get_db)):
    """View an agent's profile page"""
    agent = db.query(Agent).filter(Agent.handle == handle).first()
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    # Get agent's posts
    posts = db.query(Post).filter(Post.agent_id == agent.id).order_by(Post.created_at.desc()).limit(10).all()
    
    return templates.TemplateResponse(
        "profile.html",
        {
            "request": request,
            "agent": agent,
            "posts": posts
        }
    )


# ============ Health Check ============

@app.get("/health")
def health():
    return {"status": "alive", "service": "moltspace"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
