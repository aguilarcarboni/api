from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session
from typing import List
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords

from app.helpers.browser import Browser

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
    def __init__(self, db_url: str):
        self.engine = create_engine(db_url)
        Base.metadata.create_all(self.engine)
        nltk.download('punkt')
        nltk.download('stopwords')
        self.stop_words = set(stopwords.words('english'))
    
    def add_interest(self, interest: str, keywords: List[str]):
        """Add a new interest category with keywords"""
        with Session(self.engine) as session:
            interest_obj = session.query(Interest).filter_by(name=interest).first()
            if not interest_obj:
                interest_obj = Interest(name=interest, keywords=','.join(keywords))
                session.add(interest_obj)
                session.commit()
    
    def remove_interest(self, interest: str):
        """Remove an interest category"""
        with Session(self.engine) as session:
            interest_obj = session.query(Interest).filter_by(name=interest).first()
            if interest_obj:
                session.delete(interest_obj)
                session.commit()
    
    def fetch_and_store_articles(self, sources: List[str]):
        """Fetch articles from RSS feeds and store in database"""
        with Session(self.engine) as session:
            for url in sources:
                soup = Browser().scraper(url)
                # Find the sections containing headlines
                headlines = soup.find_all('div', class_='stack__items')
                for headline in headlines:
                    print(headline.get_text().strip())
                    existing = session.query(Article).filter_by(url=headline.get('href')).first()
                    if not existing:
                        article = Article(
                            title=headline.get_text().strip(),
                            content=headline.get_text().strip(),
                            url=headline.get('href'),
                            source=url,
                            published_date=datetime.utcnow()
                        )
                        session.add(article)
            session.commit()
    
    def get_personalized_news(self) -> List[dict]:
        """Get news based on stored interests"""
        with Session(self.engine) as session:
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
            
            return personalized_articles
    
    def mark_article_as_read(self, article_id: int):
        """Mark an article as read"""
        with Session(self.engine) as session:
            read_article = ReadArticle(article_id=article_id)
            session.add(read_article)
            session.commit()
    
    def get_interests(self) -> List[dict]:
        """Get all stored interests"""
        with Session(self.engine) as session:
            interests = session.query(Interest).all()
            return [{'name': i.name, 'keywords': i.keywords.split(',')} for i in interests]

# Example usage
def main():
    # Initialize the aggregator
    aggregator = NewsAggregator('sqlite:///news.db')
    
    # Add interests
    aggregator.add_interest('Technology', ['AI', 'Python', 'Machine Learning', 'Data Science'])
    aggregator.add_interest('Space', ['NASA', 'SpaceX', 'Astronomy', 'Mars'])
    
    # Example RSS feeds (add your own)
    sources = [
        'https://www.cnn.com',
    ]
    
    # Fetch and store articles
    aggregator.fetch_and_store_articles(sources)
    
    # Get personalized news
    news = aggregator.get_personalized_news()
    for article in news:
        print(f"Title: {article['title']}")
        print(f"Source: {article['source']}")
        print(f"URL: {article['url']}")
        print("---")
        
        # Mark as read
        aggregator.mark_article_as_read(article['id'])
    
    # Show current interests
    interests = aggregator.get_interests()
    print("\nCurrent Interests:")
    for interest in interests:
        print(f"{interest['name']}: {', '.join(interest['keywords'])}")

if __name__ == "__main__":
    main()