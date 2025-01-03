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
from src.utils.database import DatabaseHandler
from src.components.browser import Browser

browser = Browser()
Base = declarative_base()

class Interest(Base):
    __tablename__ = 'interests'
    
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True)
    keywords = Column(String)
    updated = Column(String)
    created = Column(String)
    

class Article(Base):
    __tablename__ = 'articles'
    
    id = Column(Integer, primary_key=True)
    title = Column(String)
    content = Column(String)
    url = Column(String, unique=True)
    source = Column(String)
    published_date = Column(DateTime)
    image = Column(String)
    updated = Column(String)
    created = Column(String)

class ReadArticle(Base):
    __tablename__ = 'read_articles'
    
    id = Column(Integer, primary_key=True)
    article_id = Column(Integer, ForeignKey('articles.id'))
    read_date = Column(String)
    updated = Column(String)
    created = Column(String)
    
logger.announcement('Initializing News Aggregator', 'info')

db_path = os.path.join(os.path.dirname(__file__), '..', '..', 'db', 'news.db')
db_url = f'sqlite:///{db_path}'
engine = create_engine(db_url)

db = DatabaseHandler(base=Base, engine=engine, type='sqlite')

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
    db.create('interests', {'name': interest, 'keywords': ','.join(keywords)})
    return Response.success(f'Added interest: {interest}.')

def remove_interest(interest: str):
    """Remove an interest category"""
    logger.announcement(f'Removing interest: {interest}', 'info')
    db.delete('interests', {'name': interest})
    return Response.success(f'Removed interest: {interest}.')
        
def fetch_news():
    """Fetch articles from RSS feeds and store in database"""
    logger.announcement('Fetching news from all sources', 'info')
    try:
        articles_data = []
        for source in sources:
            articles_data.extend(source.scrape_articles())

        logger.info(f'Scraped {len(articles_data)} articles from {len(sources)} sources')
        
        for article_data in articles_data:
            logger.info(f'Attempting to store news article.')
            response = db.read('articles', {'url': article_data['url']})
            if response['status'] != 'success':
                return Response.error(f'Error getting articles: {response["content"]}')
            if len(response['content']) > 0:
                existing = True
            else:
                existing = False


            if not existing:
                article = {
                    'title': article_data['title'],
                    'content': article_data['content'],
                    'url': article_data['url'],
                    'source': source.url,
                    'published_date': datetime.utcnow(),
                    'image': article_data['image']
                }
                db.create('articles', article)
                logger.success(f'Stored news article.')
            else:
                logger.warning(f'News article already exists.')

        logger.success(f'Stored {len(articles_data)} articles from {len(sources)} sources')
        return Response.success(f'Stored {len(articles_data)} articles from {len(sources)} sources')
    except Exception as e:
        logger.error(f'Error fetching and storing articles from {len(sources)} sources: {e}')
        return Response.error(f'Error fetching and storing articles from {len(sources)} sources: {e}')

def get_personalized_news() -> List[dict]:
    """Get news based on stored interests"""
    logger.announcement('Getting personalized news', 'info')
    try:

        # Get all interests and their keywords
        interests_response = db.read('interests')
        if interests_response['status'] != 'success':
            return Response.error(f'Error getting interests: {interests_response["content"]}')
        
        interests = interests_response['content']
        interest_keywords = []
        for interest in interests:
            interest_keywords.extend(interest['keywords'].split(','))
        
        # Get all unread articles
        read_articles_response = db.read('read_articles')
        if read_articles_response['status'] != 'success':
            return Response.error(f'Error getting read articles: {read_articles_response["content"]}')
        
        read_article_ids = [read_article['article_id'] for read_article in read_articles_response['content']]
        
        articles_response = db.read('articles')
        if articles_response['status'] != 'success':
            return Response.error(f'Error getting articles: {articles_response["content"]}')
        
        articles = articles_response['content']
        
        # Filter articles based on interests
        personalized_articles = []
        for article in articles:
            
            # Tokenize and clean article title and content
            text = f"{article['title']} {article['content']}"
            tokens = word_tokenize(text.lower())
            tokens = [t for t in tokens if t not in stop_words]
            
            # Check if any interest keywords match
            if any(keyword.lower() in tokens for keyword in interest_keywords):
                personalized_articles.append({
                    'id': article['id'],
                    'title': article['title'],
                    'content': article['content'],
                    'url': article['url'],
                    'source': article['source'],
                    'published_date': article['published_date'],
                    'image': article['image']
                })
                
        logger.success(f'Found {len(personalized_articles)} personalized articles')
        return Response.success(personalized_articles)
            
    except Exception as e:
        logger.error(f'Error getting personalized news: {e}')
        return Response.error(f'Error getting personalized news: {e}')

def mark_article_as_read(article_id: int):
    """Mark an article as read"""
    try:
        db.create('read_articles', {'article_id': article_id})
        logger.success(f'Marked article as read: {article_id}')
        return Response.success(f'Marked article as read: {article_id}')
    except Exception as e:
        logger.error(f'Error marking article as read: {article_id}: {e}')
        return Response.error(f'Error marking article as read: {article_id}: {e}')

def get_interests() -> List[dict]:
    """Get all stored interests"""
    try:
        interests_response = db.read('interests')
        if interests_response['status'] != 'success':
            return Response.error(f'Error getting interests: {interests_response["content"]}')
        return Response.success(interests_response['content'])
    except Exception as e:
        logger.error(f'Error getting interests: {e}')
        return Response.error(f'Error getting interests: {e}')
