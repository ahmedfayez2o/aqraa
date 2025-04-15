from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import pandas as pd
import numpy as np
import joblib
from books.models import Book
from reviews.models import Review
import nltk
from nltk.sentiment import SentimentIntensityAnalyzer

class BookRecommender:
    def __init__(self):
        self.vectorizer = TfidfVectorizer(stop_words='english')
        self.similarity_matrix = None
        self.books_df = None
        
    def prepare_data(self):
        # Get all books from the database
        books = Book.objects.all()
        
        # Create a DataFrame
        self.books_df = pd.DataFrame([{
            'id': str(book.id),
            'title': book.title,
            'author': book.author,
            'genre': book.genre,
            'summary': book.summary or '',  # Handle None values
            'combined_features': f"{book.title} {book.author} {book.genre} {book.summary or ''}"
        } for book in books])
        
        if len(self.books_df) == 0:
            raise ValueError("No books found in the database")
            
        return self.books_df
        
    def train_model(self):
        # Prepare the data
        self.prepare_data()
        
        # Create TF-IDF matrix
        tfidf_matrix = self.vectorizer.fit_transform(self.books_df['combined_features'])
        
        # Calculate similarity matrix
        self.similarity_matrix = cosine_similarity(tfidf_matrix)
        
        return self.similarity_matrix
    
    def get_recommendations(self, book_id, num_recommendations=5):
        if self.similarity_matrix is None:
            self.train_model()
            
        # Find the book index
        try:
            book_idx = self.books_df[self.books_df['id'] == book_id].index[0]
        except IndexError:
            raise ValueError("Book ID not found")
            
        # Get similarity scores
        similarity_scores = list(enumerate(self.similarity_matrix[book_idx]))
        
        # Sort based on similarity scores
        similarity_scores = sorted(similarity_scores, key=lambda x: x[1], reverse=True)
        
        # Get top N similar books (excluding itself)
        similar_books = similarity_scores[1:num_recommendations+1]
        
        # Return recommended book IDs
        recommended_ids = [self.books_df.iloc[idx]['id'] for idx, _ in similar_books]
        return recommended_ids
    
    def save_model(self, filepath='recommendations/ml_models/book_recommender.pkl'):
        """Save the trained model to a pickle file"""
        if self.similarity_matrix is None:
            self.train_model()
            
        model_data = {
            'vectorizer': self.vectorizer,
            'similarity_matrix': self.similarity_matrix,
            'books_df': self.books_df
        }
        
        joblib.dump(model_data, filepath)
        
    def load_model(self, filepath='recommendations/ml_models/book_recommender.pkl'):
        """Load the trained model from a pickle file"""
        try:
            model_data = joblib.load(filepath)
            self.vectorizer = model_data['vectorizer']
            self.similarity_matrix = model_data['similarity_matrix']
            self.books_df = model_data['books_df']
        except FileNotFoundError:
            # If model doesn't exist, train a new one
            self.train_model()
            self.save_model(filepath)

class SentimentAnalyzer:
    def __init__(self):
        # Download required NLTK data (only needed once)
        try:
            nltk.data.find('sentiment/vader_lexicon.zip')
        except LookupError:
            nltk.download('vader_lexicon')
        
        self.sentiment_analyzer = SentimentIntensityAnalyzer()
        
    def analyze_sentiment(self, text):
        """
        Analyze the sentiment of a given text.
        Returns a score between -1 (most negative) and 1 (most positive)
        """
        if not text:
            return 0.0
            
        scores = self.sentiment_analyzer.polarity_scores(text)
        return scores['compound']
        
    def analyze_book_reviews(self, book_id):
        """
        Analyze all reviews for a specific book.
        Returns average sentiment score and sentiment distribution.
        """
        reviews = Review.objects.filter(book=book_id)
        if not reviews:
            return {
                'average_sentiment': 0.0,
                'sentiment_distribution': {
                    'positive': 0,
                    'neutral': 0,
                    'negative': 0
                }
            }
        
        sentiments = []
        distribution = {'positive': 0, 'neutral': 0, 'negative': 0}
        
        for review in reviews:
            sentiment = self.analyze_sentiment(review.comment)
            sentiments.append(sentiment)
            
            # Categorize sentiment
            if sentiment >= 0.05:
                distribution['positive'] += 1
            elif sentiment <= -0.05:
                distribution['negative'] += 1
            else:
                distribution['neutral'] += 1
        
        return {
            'average_sentiment': np.mean(sentiments),
            'sentiment_distribution': distribution
        }