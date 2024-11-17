from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session
from typing import List
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from app.modules.browser import Browser
from app.helpers.logger import logger
from app.helpers.response import Response
import os

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

class NewsAggregator:

    def __init__(self):
        
        logger.announcement('Initializing News Aggregator Service', 'info')

        db_path = os.path.join(os.path.dirname(__file__), '..', 'db', 'news.db')
        db_url = f'sqlite:///{db_path}'

        self.engine = create_engine(db_url)
        Base.metadata.create_all(self.engine)
        nltk.download('punkt')
        nltk.download('stopwords')
        
        self.stop_words = set(stopwords.words('english'))
        self.sources = [
            CNN()
        ]

        self.add_interest('Technology', ['AI', 'machine learning', 'deep learning', 'neural networks', 'artificial intelligence', 'machine learning', 'deep learning', 'neural networks', 'artificial intelligence'])
        self.add_interest('Business', ['stock market', 'investing', 'finance', 'economy', 'markets', 'business', 'economics', 'market', 'stocks', 'investing', 'finance', 'economy', 'markets', 'business', 'economics', 'market', 'stocks', 'investing', 'finance', 'economy', 'markets', 'business', 'economics', 'market', 'stocks'])

        logger.announcement('News Aggregator Service initialized', 'success')
    
    def add_interest(self, interest: str, keywords: List[str]):
        """Add a new interest category with keywords"""
        logger.announcement(f'Adding interest: {interest} with keywords: {keywords}', 'info')
        with Session(self.engine) as session:
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
    
    def remove_interest(self, interest: str):
        """Remove an interest category"""
        logger.announcement(f'Removing interest: {interest}', 'info')
        with Session(self.engine) as session:
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
            
    def fetch_news(self):
        """Fetch articles from RSS feeds and store in database"""
        with Session(self.engine) as session:
            logger.announcement('Fetching news from all sources', 'info')
            try:
                articles_data = []
                for source in self.sources:
                    articles_data.extend(source.scrape_articles())

                logger.info(f'Scraped {len(articles_data)} articles from {len(self.sources)} sources')
                
                for article_data in articles_data:
                    logger.info(f'Attempting to store article: {article_data}')
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
                        logger.success(f'Stored article.')
                    else:
                        logger.info(f'Article already exists: {article_data["title"]}')

                session.commit()
                logger.info(f'Stored {len(articles_data)} articles from {len(self.sources)} sources')
                return Response.success(f'Stored {len(articles_data)} articles from {len(self.sources)} sources')
            except Exception as e:
                logger.error(f'Error fetching and storing articles from {len(self.sources)} sources: {e}')
                return Response.error(f'Error fetching and storing articles from {len(self.sources)} sources: {e}')

    def get_personalized_news(self) -> List[dict]:
        """Get news based on stored interests"""
        logger.announcement('Getting personalized news', 'info')
        with Session(self.engine) as session:
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
                    tokens = [t for t in tokens if t not in self.stop_words]
                    
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
    
    def mark_article_as_read(self, article_id: int):
        """Mark an article as read"""
        with Session(self.engine) as session:
            try:
                read_article = ReadArticle(article_id=article_id)
                session.add(read_article)
                session.commit()
                logger.success(f'Marked article as read: {article_id}')
                return Response.success(f'Marked article as read: {article_id}')
            except Exception as e:
                logger.error(f'Error marking article as read: {article_id}: {e}')
                return Response.error(f'Error marking article as read: {article_id}: {e}')
    
    def get_interests(self) -> List[dict]:
        """Get all stored interests"""
        with Session(self.engine) as session:
            try:
                interests = session.query(Interest).all()
                return Response.success([{'name': i.name, 'keywords': i.keywords.split(',')} for i in interests])
            except Exception as e:
                logger.error(f'Error getting interests: {e}')
                return Response.error(f'Error getting interests: {e}')

class CNN:

    def __init__(self):

        logger.info('Initializing CNN')
        self.url = 'https://www.cnn.com'
        self.max_articles = 5
        logger.success('CNN initialized')

    def scrape_articles(self):

        all_data = []
        soup = browser.scraper(self.url)
        article_urls = set()
        
        for a in soup.find_all('a', href=True):
            href = a['href']
            if href and href.startswith('/') and href != '#':
                full_url = f"{self.url}{href}"
            else:
                full_url = href
                
            if self.url_is_article(full_url):
                article_urls.add(full_url)
            
            if len(article_urls) >= self.max_articles:
                break
                
        for article_url in list(article_urls)[:self.max_articles]:
            parsed_data = self.parse(article_url)
            all_data.append(parsed_data)
            
        return all_data
    
    def url_is_article(self, url, current_year='2024'):
        if url:
            if 'cnn.com/{}/'.format(current_year) in url and '/gallery/' not in url:
                return True
        return False
    
    def return_text_if_not_none(self, element):
        if element:
            return element.text.strip()
        else:
            return ''

    def parse(self, article_url):
        soup = browser.scraper(article_url)
        title = self.return_text_if_not_none(soup.find('h1', {'class': 'headline__text'}))
        author = soup.find('span', {'class': 'byline__name'})
        if not author:
            author = soup.find('span', {'class': 'byline__names'})
        author = self.return_text_if_not_none(author)
        article_content = self.return_text_if_not_none(soup.find('div', {'class': 'article__content'}))
        timestamp = self.return_text_if_not_none(soup.find('div', {'class': 'timestamp'}))
        
        timestamp_data = self.parse_timestamp(timestamp) if timestamp else ['', '', '', '']
        
        return {
            'title': title.strip(),
            'author': author.strip(),
            'content': article_content.strip(),
            'url': article_url,
            'timestamp_type': timestamp_data[0],
            'time': timestamp_data[1],
            'day': timestamp_data[2],
            'year': timestamp_data[3]
        }

    def parse_timestamp(self, timestamp):
        if 'Published' in timestamp:
            timestamp_type = 'Published'
        elif 'Updated' in timestamp:
            timestamp_type = 'Updated'
        else:
            timestamp_type = ''

        article_time, article_day, article_year = timestamp.replace('Published', '').replace('Updated', '').split(', ')
        return timestamp_type, article_time.strip(), article_day.strip(), article_year.strip()