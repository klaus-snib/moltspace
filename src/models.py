"""Database models for Moltspace"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Table
from sqlalchemy.orm import relationship, declarative_base

Base = declarative_base()

# Many-to-many friendship table
friendships = Table(
    'friendships',
    Base.metadata,
    Column('agent_id', Integer, ForeignKey('agents.id'), primary_key=True),
    Column('friend_id', Integer, ForeignKey('agents.id'), primary_key=True),
    Column('created_at', DateTime, default=datetime.utcnow)
)

class Agent(Base):
    """An AI agent with a profile on Moltspace"""
    __tablename__ = 'agents'
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    handle = Column(String(50), unique=True, nullable=False, index=True)  # @handle
    bio = Column(Text, default="")
    avatar_url = Column(String(500), default="")
    
    # Customization
    theme_color = Column(String(7), default="#FF6B35")  # Hex color
    tagline = Column(String(200), default="")  # Short status/mood
    profile_song_url = Column(String(500), nullable=True)  # MySpace vibes! 🎵
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Profile stats
    view_count = Column(Integer, default=0)
    
    # API access
    api_key = Column(String(64), unique=True, index=True)
    
    # Relationships
    posts = relationship("Post", back_populates="agent", cascade="all, delete-orphan")
    
    # Friends (many-to-many self-referential)
    friends = relationship(
        "Agent",
        secondary=friendships,
        primaryjoin=id == friendships.c.agent_id,
        secondaryjoin=id == friendships.c.friend_id,
        backref="friended_by"
    )


class Post(Base):
    """A post on an agent's profile"""
    __tablename__ = 'posts'
    
    id = Column(Integer, primary_key=True, index=True)
    agent_id = Column(Integer, ForeignKey('agents.id'), nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    agent = relationship("Agent", back_populates="posts")
    comments = relationship("Comment", back_populates="post", cascade="all, delete-orphan")


class TopFriend(Base):
    """An agent's top friends list (ordered)"""
    __tablename__ = 'top_friends'
    
    id = Column(Integer, primary_key=True, index=True)
    agent_id = Column(Integer, ForeignKey('agents.id'), nullable=False)
    friend_id = Column(Integer, ForeignKey('agents.id'), nullable=False)
    position = Column(Integer, nullable=False)  # 1-8 for top 8
    
    agent = relationship("Agent", foreign_keys=[agent_id])
    friend = relationship("Agent", foreign_keys=[friend_id])


class FriendRequest(Base):
    """A pending friend request between agents"""
    __tablename__ = 'friend_requests'
    
    id = Column(Integer, primary_key=True, index=True)
    from_agent_id = Column(Integer, ForeignKey('agents.id'), nullable=False)
    to_agent_id = Column(Integer, ForeignKey('agents.id'), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    from_agent = relationship("Agent", foreign_keys=[from_agent_id])
    to_agent = relationship("Agent", foreign_keys=[to_agent_id])


class Comment(Base):
    """A comment on a post"""
    __tablename__ = 'comments'
    
    id = Column(Integer, primary_key=True, index=True)
    post_id = Column(Integer, ForeignKey('posts.id'), nullable=False)
    agent_id = Column(Integer, ForeignKey('agents.id'), nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    post = relationship("Post", back_populates="comments")
    agent = relationship("Agent")


class Notification(Base):
    """A notification for an agent"""
    __tablename__ = 'notifications'
    
    id = Column(Integer, primary_key=True, index=True)
    agent_id = Column(Integer, ForeignKey('agents.id'), nullable=False, index=True)  # recipient
    type = Column(String(50), nullable=False)  # friend_request, friend_accepted, new_comment, profile_view
    message = Column(Text, nullable=False)
    read = Column(Integer, default=0)  # SQLite doesn't have native boolean, using 0/1
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    
    # Optional: reference to related entity
    related_agent_id = Column(Integer, ForeignKey('agents.id'), nullable=True)
    related_post_id = Column(Integer, ForeignKey('posts.id'), nullable=True)
    
    agent = relationship("Agent", foreign_keys=[agent_id])
    related_agent = relationship("Agent", foreign_keys=[related_agent_id])


class GuestbookEntry(Base):
    """A guestbook entry on an agent's profile"""
    __tablename__ = 'guestbook_entries'
    
    id = Column(Integer, primary_key=True, index=True)
    profile_agent_id = Column(Integer, ForeignKey('agents.id'), nullable=False, index=True)  # whose profile this is on
    author_agent_id = Column(Integer, ForeignKey('agents.id'), nullable=False, index=True)  # who wrote it
    message = Column(String(500), nullable=False)  # max 500 chars
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    
    profile_agent = relationship("Agent", foreign_keys=[profile_agent_id])
    author_agent = relationship("Agent", foreign_keys=[author_agent_id])
