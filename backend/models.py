from sqlalchemy import Column, Integer, String, Boolean, Text, DateTime, ForeignKey, Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base


class Topic(Base):
    __tablename__ = "topics"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)  # e.g., "OpenAI Sora Release"
    summary = Column(Text)  # AI Summary of the whole topic
    popularity_score = Column(Float, default=0.0)
    created_at = Column(DateTime, server_default=func.now())
    
    # ⭐ REQUIRED for clustering
    embedding = Column(Text, nullable=True)  # store vector JSON here

    # Relationship to articles
    articles = relationship("NewsItem", back_populates="topic")



class NewsItem(Base):
    __tablename__ = "news_items"
    id = Column(Integer, primary_key=True, index=True)
    source_id = Column(Integer, ForeignKey("sources.id"))

    # NEW: Link to a Topic
    topic_id = Column(Integer, ForeignKey("topics.id"), nullable=True)
    topic = relationship("Topic", back_populates="articles")

    title = Column(String, nullable=False)
    summary = Column(Text)
    url = Column(String, unique=True, index=True)
    published_at = Column(DateTime)
    is_favorite = Column(Boolean, default=False)
    created_at = Column(DateTime, server_default=func.now())


class Source(Base):
    __tablename__ = "sources"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    url = Column(String, unique=True, nullable=False)
    type = Column(String)
    active = Column(Boolean, default=True)
