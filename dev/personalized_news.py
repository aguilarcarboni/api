from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from collections import Counter

# Download required NLTK data
nltk.download('punkt')
nltk.download('stopwords')

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///news_aggregator.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Association tables for many-to-many relationships
user_interests = db.Table('user_interests',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('interest_id', db.Integer, db.ForeignKey('interest.id'))
)

article_interests = db.Table('article_interests',
    db.Column('article_id', db.Integer, db.ForeignKey('article.id')),
    db.Column('interest_id', db.Integer, db.ForeignKey('interest.id'))
)

# Database Models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    interests = db.relationship('Interest', secondary=user_interests, 
                              backref=db.backref('users', lazy='dynamic'))

    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'interests': [interest.name for interest in self.interests]
        }

class Interest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    articles = db.relationship('Article', secondary=article_interests,
                             backref=db.backref('interests', lazy='dynamic'))

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name
        }

class Article(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    url = db.Column(db.String(500), unique=True, nullable=False)
    source = db.Column(db.String(100), nullable=False)
    published_date = db.Column(db.DateTime, nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'content': self.content,
            'url': self.url,
            'source': self.source,
            'published_date': self.published_date.isoformat(),
            'interests': [interest.name for interest in self.interests]
        }

def analyze_content(title: str, content: str) -> list:
    """Analyze article content to determine relevant interests."""
    # Combine title and content for analysis
    text = f"{title} {content}".lower()
    
    # Tokenize and remove stopwords
    stop_words = set(stopwords.words('english'))
    tokens = word_tokenize(text)
    tokens = [word for word in tokens if word.isalnum() and word not in stop_words]
    
    # Get most common words as potential interests
    word_freq = Counter(tokens)
    return [word for word, freq in word_freq.most_common(5)]

# Routes
@app.route('/users', methods=['POST'])
def create_user():
    data = request.get_json()
    if not data or 'username' not in data:
        return jsonify({'error': 'Username is required'}), 400

    try:
        user = User(username=data['username'])
        db.session.add(user)
        db.session.commit()
        return jsonify(user.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400

@app.route('/users/<int:user_id>/interests', methods=['POST'])
def add_user_interest(user_id):
    data = request.get_json()
    if not data or 'name' not in data:
        return jsonify({'error': 'Interest name is required'}), 400

    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404

    try:
        # Get or create interest
        interest = Interest.query.filter_by(name=data['name']).first()
        if not interest:
            interest = Interest(name=data['name'])
            db.session.add(interest)

        user.interests.append(interest)
        db.session.commit()
        return jsonify(user.to_dict()), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400

@app.route('/articles', methods=['POST'])
def create_article():
    data = request.get_json()
    required_fields = ['title', 'content', 'url', 'source']
    if not data or not all(field in data for field in required_fields):
        return jsonify({'error': 'Missing required fields'}), 400

    try:
        article = Article(
            title=data['title'],
            content=data['content'],
            url=data['url'],
            source=data['source'],
            published_date=datetime.fromisoformat(data.get('published_date', datetime.now().isoformat()))
        )
        db.session.add(article)

        # Analyze content and add interests
        relevant_topics = analyze_content(article.title, article.content)
        for topic in relevant_topics:
            interest = Interest.query.filter_by(name=topic).first()
            if interest:
                article.interests.append(interest)

        db.session.commit()
        return jsonify({
            'status': 'success',
            'article': article.to_dict(),
            'detected_interests': relevant_topics
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400

@app.route('/users/<int:user_id>/feed')
def get_user_feed(user_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404

    # Get user's interests
    user_interests = [interest.id for interest in user.interests]

    # Query articles that match user's interests
    articles = Article.query\
        .join(article_interests)\
        .join(Interest)\
        .filter(Interest.id.in_(user_interests))\
        .order_by(Article.published_date.desc())\
        .limit(20)\
        .all()

    return jsonify([article.to_dict() for article in articles])

# Error handlers
@app.errorhandler(404)
def not_found_error(error):
    return jsonify({'error': 'Not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, host='0.0.0.0', port=10000)