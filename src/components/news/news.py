from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session
from typing import List
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
import os

from src.components.news.sources import cnn
from src.utils.logger import logger
from src.utils.response import Response
from src.components.browser import Browser

browser = Browser()
Base = declarative_base()

class Interest(Base):
    __tablename__ = 'interests'
    
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True)
    keywords = Column(String)

class Article(Base):
    __tablename__ = 'articles'
    
    id = Column(Integer, primary_key=True)
    title = Column(String)
    content = Column(String)
    url = Column(String, unique=True)
    source = Column(String)
    published_date = Column(DateTime)
    
class ReadArticle(Base):
    __tablename__ = 'read_articles'
    
    id = Column(Integer, primary_key=True)
    article_id = Column(Integer, ForeignKey('articles.id'))
    read_date = Column(DateTime, default=datetime.utcnow)
    
logger.announcement('Initializing News Aggregator', 'info')

db_path = os.path.join(os.path.dirname(__file__), '..', '..', 'db', 'news.db')
db_url = f'sqlite:///{db_path}'

engine = create_engine(db_url)
Base.metadata.create_all(engine)

nltk.download('punkt')
nltk.download('stopwords')

stop_words = set(stopwords.words('english'))

"""
Sources must have a scrape_articles() method that returns a list of dictionaries with the following keys:
    - title
    - content
    - url
    - source
    - published_date
"""
sources = [
    cnn
]

logger.announcement('Successfully initialized news service', 'success')

def add_interest(interest: str, keywords: List[str]):
    """Add a new interest category with keywords"""
    logger.announcement(f'Adding interest: {interest} with keywords: {keywords}', 'info')
    with Session(engine) as session:
        interest_obj = session.query(Interest).filter_by(name=interest).first()
        if not interest_obj:
            interest_obj = Interest(name=interest, keywords=','.join(keywords))
            session.add(interest_obj)
            session.commit()
            logger.announcement(f'Added interest: {interest} with keywords: {keywords}', 'success')
            return Response.success(f'Added interest: {interest} with keywords: {keywords}')
        else:
            logger.error(f'Interest: {interest} already exists')
            return Response.error(f'Interest: {interest} already exists')

def remove_interest(interest: str):
    """Remove an interest category"""
    logger.announcement(f'Removing interest: {interest}', 'info')
    with Session(engine) as session:
        try:
            interest_obj = session.query(Interest).filter_by(name=interest).first()
            if interest_obj:
                session.delete(interest_obj)
                session.commit()
                logger.success(f'Removed interest: {interest}')
                return Response.announcement(f'Removed interest: {interest}', 'success')
            else:
                logger.error(f'Interest: {interest} does not exist')
                return Response.error(f'Interest: {interest} does not exist')
        except Exception as e:
            logger.error(f'Error removing interest: {interest}: {e}')
            return Response.error(f'Error removing interest: {interest}: {e}')
        
def fetch_news():
    """Fetch articles from RSS feeds and store in database"""
    with Session(engine) as session:
        logger.announcement('Fetching news from all sources', 'info')
        try:
            articles_data = []
            for source in sources:
                articles_data.extend(source.scrape_articles())

            logger.info(f'Scraped {len(articles_data)} articles from {len(sources)} sources')
            
            for article_data in articles_data:
                logger.info(f'Attempting to store news article.')
                existing = session.query(Article).filter_by(url=article_data['url']).first()
                if not existing:
                    article = Article(
                        title=article_data['title'],
                        content=article_data['content'],
                        url=article_data['url'],
                        source=source.url,
                        published_date=datetime.utcnow()
                    )
                    session.add(article)
                    logger.success(f'Stored news article.')
                else:
                    logger.warning(f'News article already exists.')

            session.commit()
            logger.info(f'Stored {len(articles_data)} articles from {len(sources)} sources')
            return Response.success(f'Stored {len(articles_data)} articles from {len(sources)} sources')
        
        except Exception as e:
            logger.error(f'Error fetching and storing articles from {len(sources)} sources: {e}')
            return Response.error(f'Error fetching and storing articles from {len(sources)} sources: {e}')

def get_personalized_news() -> List[dict]:
    """Get news based on stored interests"""
    logger.announcement('Getting personalized news', 'info')
    with Session(engine) as session:
        try:

            # Get all interests and their keywords
            interests = session.query(Interest).all()
            interest_keywords = []
            for interest in interests:
                interest_keywords.extend(interest.keywords.split(','))
            
            # Get all unread articles
            read_article_ids = [ra.article_id for ra in session.query(ReadArticle).all()]
            articles = session.query(Article)\
                .filter(~Article.id.in_(read_article_ids))\
                .order_by(Article.published_date.desc())\
                .all()
            
            # Filter articles based on interests
            personalized_articles = []
            for article in articles:

                # Tokenize and clean article title and content
                text = f"{article.title} {article.content}"
                tokens = word_tokenize(text.lower())
                tokens = [t for t in tokens if t not in stop_words]
                
                # Check if any interest keywords match
                if any(keyword.lower() in tokens for keyword in interest_keywords):
                    personalized_articles.append({
                        'id': article.id,
                        'title': article.title,
                        'content': article.content,
                        'url': article.url,
                        'source': article.source,
                        'published_date': article.published_date
                    })
                    
            logger.announcement(f'Found {len(personalized_articles)} personalized articles', 'success')
            return Response.success(personalized_articles)
                
        except Exception as e:
            logger.error(f'Error getting personalized news: {e}')
            return Response.error(f'Error getting personalized news: {e}')

def mark_article_as_read(article_id: int):
    """Mark an article as read"""
    with Session(engine) as session:
        try:
            read_article = ReadArticle(article_id=article_id)
            session.add(read_article)
            session.commit()
            logger.success(f'Marked article as read: {article_id}')
            return Response.success(f'Marked article as read: {article_id}')
        except Exception as e:
            logger.error(f'Error marking article as read: {article_id}: {e}')
            return Response.error(f'Error marking article as read: {article_id}: {e}')

def get_interests() -> List[dict]:
    """Get all stored interests"""
    with Session(engine) as session:
        try:
            interests = session.query(Interest).all()
            return Response.success([{'name': i.name, 'keywords': i.keywords.split(',')} for i in interests])
        except Exception as e:
            logger.error(f'Error getting interests: {e}')
            return Response.error(f'Error getting interests: {e}')
