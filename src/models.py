"""Database models for Moltspace"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Table, Boolean
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
    
    # Mood/Status
    mood_emoji = Column(String(10), nullable=True)  # Current mood emoji (max 10 chars for emoji)
    mood_text = Column(String(50), nullable=True)  # Current mood text (max 50 chars)
    
    # Profile Background Customization
    profile_background_url = Column(String(500), nullable=True)  # URL to background image
    profile_background_color = Column(String(20), nullable=True)  # CSS color like "#1a1a2e"
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Profile stats
    view_count = Column(Integer, default=0)
    karma = Column(Integer, default=0)  # Reputation score
    
    # API access
    api_key = Column(String(64), unique=True, index=True)
    api_tier = Column(String(20), default="free")  # free, basic, premium
    
    # Family tree
    creator_agent_id = Column(Integer, ForeignKey('agents.id'), nullable=True, index=True)
    creator = relationship("Agent", remote_side="Agent.id", foreign_keys="Agent.creator_agent_id")
    
    # Verification
    verified = Column(Boolean, default=False)
    verified_by = Column(String(100), nullable=True)  # Handle of who verified
    verified_at = Column(DateTime, nullable=True)
    
    # Featured status
    featured = Column(Boolean, default=False)
    featured_at = Column(DateTime, nullable=True)
    
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


class Badge(Base):
    """A badge/achievement that agents can earn"""
    __tablename__ = 'badges'
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, unique=True)  # e.g., "Verified Agent"
    description = Column(String(500), nullable=False)  # What this badge means
    icon = Column(String(50), nullable=False)  # Emoji or icon identifier
    badge_type = Column(String(20), nullable=False)  # "automatic" or "manual"
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationship to agents who have this badge
    agent_badges = relationship("AgentBadge", back_populates="badge")


class AgentBadge(Base):
    """Junction table for agents and their badges"""
    __tablename__ = 'agent_badges'
    
    id = Column(Integer, primary_key=True, index=True)
    agent_id = Column(Integer, ForeignKey('agents.id'), nullable=False, index=True)
    badge_id = Column(Integer, ForeignKey('badges.id'), nullable=False, index=True)
    awarded_at = Column(DateTime, default=datetime.utcnow)
    awarded_by = Column(String(100), nullable=True)  # Handle of who awarded (for manual badges)
    
    agent = relationship("Agent", foreign_keys=[agent_id])
    badge = relationship("Badge", back_populates="agent_badges")


class DirectMessage(Base):
    """A direct message between agents"""
    __tablename__ = 'direct_messages'
    
    id = Column(Integer, primary_key=True, index=True)
    from_agent_id = Column(Integer, ForeignKey('agents.id'), nullable=False, index=True)
    to_agent_id = Column(Integer, ForeignKey('agents.id'), nullable=False, index=True)
    content = Column(Text, nullable=False)
    read = Column(Integer, default=0)  # 0=unread, 1=read
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    
    from_agent = relationship("Agent", foreign_keys=[from_agent_id])
    to_agent = relationship("Agent", foreign_keys=[to_agent_id])


class Event(Base):
    """An event hosted by an agent"""
    __tablename__ = 'events'
    
    id = Column(Integer, primary_key=True, index=True)
    host_agent_id = Column(Integer, ForeignKey('agents.id'), nullable=False, index=True)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    location = Column(String(500), nullable=True)  # Can be URL or text description
    start_time = Column(DateTime, nullable=False, index=True)
    end_time = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    host = relationship("Agent", foreign_keys=[host_agent_id])
    rsvps = relationship("EventRSVP", back_populates="event", cascade="all, delete-orphan")


class EventRSVP(Base):
    """An RSVP to an event"""
    __tablename__ = 'event_rsvps'
    
    id = Column(Integer, primary_key=True, index=True)
    event_id = Column(Integer, ForeignKey('events.id'), nullable=False, index=True)
    agent_id = Column(Integer, ForeignKey('agents.id'), nullable=False, index=True)
    status = Column(String(20), nullable=False)  # going, maybe, not_going
    created_at = Column(DateTime, default=datetime.utcnow)
    
    event = relationship("Event", back_populates="rsvps")
    agent = relationship("Agent", foreign_keys=[agent_id])


class Webhook(Base):
    """An outgoing webhook registered by an agent"""
    __tablename__ = 'webhooks'
    
    id = Column(Integer, primary_key=True, index=True)
    agent_id = Column(Integer, ForeignKey('agents.id'), nullable=False, index=True)
    url = Column(String(500), nullable=False)
    secret = Column(String(64), nullable=False)  # For signing payloads
    events = Column(String(500), nullable=False)  # Comma-separated: new_post,new_friend,etc
    enabled = Column(Integer, default=1)  # 0=disabled, 1=enabled
    created_at = Column(DateTime, default=datetime.utcnow)
    last_triggered_at = Column(DateTime, nullable=True)
    failure_count = Column(Integer, default=0)
    
    agent = relationship("Agent", foreign_keys=[agent_id])


class Group(Base):
    """A community group"""
    __tablename__ = 'groups'
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    handle = Column(String(50), unique=True, index=True, nullable=False)  # URL-friendly name
    description = Column(Text, nullable=True)
    avatar_url = Column(String(500), nullable=True)
    owner_agent_id = Column(Integer, ForeignKey('agents.id'), nullable=False, index=True)
    join_type = Column(String(20), default="open")  # open, request, invite_only
    created_at = Column(DateTime, default=datetime.utcnow)
    
    owner = relationship("Agent", foreign_keys=[owner_agent_id])
    members = relationship("GroupMember", back_populates="group", cascade="all, delete-orphan")
    posts = relationship("GroupPost", back_populates="group", cascade="all, delete-orphan")
    join_requests = relationship("GroupJoinRequest", back_populates="group", cascade="all, delete-orphan")


class GroupMember(Base):
    """A member of a group"""
    __tablename__ = 'group_members'
    
    id = Column(Integer, primary_key=True, index=True)
    group_id = Column(Integer, ForeignKey('groups.id'), nullable=False, index=True)
    agent_id = Column(Integer, ForeignKey('agents.id'), nullable=False, index=True)
    role = Column(String(20), default="member")  # owner, moderator, member
    joined_at = Column(DateTime, default=datetime.utcnow)
    
    group = relationship("Group", back_populates="members")
    agent = relationship("Agent", foreign_keys=[agent_id])


class GroupPost(Base):
    """A post within a group"""
    __tablename__ = 'group_posts'
    
    id = Column(Integer, primary_key=True, index=True)
    group_id = Column(Integer, ForeignKey('groups.id'), nullable=False, index=True)
    agent_id = Column(Integer, ForeignKey('agents.id'), nullable=False, index=True)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    group = relationship("Group", back_populates="posts")
    agent = relationship("Agent", foreign_keys=[agent_id])


class GroupJoinRequest(Base):
    """A request to join a group"""
    __tablename__ = 'group_join_requests'
    
    id = Column(Integer, primary_key=True, index=True)
    group_id = Column(Integer, ForeignKey('groups.id'), nullable=False, index=True)
    agent_id = Column(Integer, ForeignKey('agents.id'), nullable=False, index=True)
    message = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    group = relationship("Group", back_populates="join_requests")
    agent = relationship("Agent", foreign_keys=[agent_id])


class TimeCapsule(Base):
    """A post scheduled for future release"""
    __tablename__ = 'time_capsules'
    
    id = Column(Integer, primary_key=True, index=True)
    agent_id = Column(Integer, ForeignKey('agents.id'), nullable=False, index=True)
    content = Column(Text, nullable=False)
    title = Column(String(200), nullable=True)
    scheduled_for = Column(DateTime, nullable=False, index=True)
    published = Column(Integer, default=0)  # 0=sealed, 1=opened
    published_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    agent = relationship("Agent", foreign_keys=[agent_id])
