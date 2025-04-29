from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import MinMaxScaler
import pandas as pd
import numpy as np
from books.models import Book
from reviews.models import Review
from orders.models import Order 
from .models import ModelData
import json

class BookRecommender:
    MODEL_NAME = 'book_recommender'
    
    def __init__(self):
        self.vectorizer = TfidfVectorizer(stop_words='english')
        self.similarity_matrix = None
        self.books_df = None
        self.user_ratings_matrix = None
        
    def prepare_data(self):
        """Prepare book data and user interaction data"""
        books = Book.objects.all()
        
        # Create the books DataFrame
        self.books_df = pd.DataFrame([{
            'id': str(book.id),
            'title': book.title,
            'author': book.author,
            'genre': book.genre,
            'summary': book.summary or '',
            'keywords': ' '.join(book.keywords or []),
            'combined_features': f"{book.title} {book.author} {book.genre} {book.summary or ''} {' '.join(book.keywords or [])}"
        } for book in books])
        
        # Get all user interactions
        reviews = Review.objects.all()
        orders = Order.objects.all()
        
        # Create user-item interaction matrix
        interactions = []
        
        # Add review interactions
        for review in reviews:
            interactions.append({
                'user_id': review.user.id,
                'book_id': str(review.book.id),
                'rating': review.rating,
                'interaction_type': 'review'
            })
            
        # Add order interactions
        for order in orders:
            rating = 5 if order.is_purchased else 4
            interactions.append({
                'user_id': order.user.id,
                'book_id': str(order.book.id),
                'rating': rating,
                'interaction_type': 'order'
            })
            
        # Create user-item matrix
        if interactions:
            interactions_df = pd.DataFrame(interactions)
            self.user_ratings_matrix = interactions_df.pivot_table(
                index='user_id',
                columns='book_id',
                values='rating',
                aggfunc='mean'
            ).fillna(0)
        else:
            self.user_ratings_matrix = pd.DataFrame()
            
        return self.books_df
        
    def train_model(self):
        """Train both content-based and collaborative filtering models"""
        self.prepare_data()
        
        if len(self.books_df) == 0:
            raise ValueError("No books found in the database")
            
        # Content-based filtering
        tfidf_matrix = self.vectorizer.fit_transform(self.books_df['combined_features'])
        self.similarity_matrix = cosine_similarity(tfidf_matrix)
        
        # Save model data to database
        model_data = {
            'vectorizer': {
                'vocabulary': self.vectorizer.vocabulary_,
                'idf': self.vectorizer.idf_.tolist(),
                'stop_words': list(self.vectorizer.stop_words_)
            },
            'similarity_matrix': self.similarity_matrix.tolist(),
            'books_data': self.books_df.to_dict(),
            'user_ratings': self.user_ratings_matrix.to_dict() if not self.user_ratings_matrix.empty else {}
        }
        
        ModelData.save_model_data(self.MODEL_NAME, model_data)
        return self.similarity_matrix
    
    def load_model(self):
        """Load model data from database"""
        model_data = ModelData.get_latest_model_data(self.MODEL_NAME)
        if not model_data:
            self.train_model()
            return
            
        # Reconstruct vectorizer
        vectorizer_data = model_data.data['vectorizer']
        self.vectorizer = TfidfVectorizer(stop_words='english')
        self.vectorizer.vocabulary_ = vectorizer_data['vocabulary']
        self.vectorizer.idf_ = np.array(vectorizer_data['idf'])
        self.vectorizer.stop_words_ = set(vectorizer_data['stop_words'])
        
        # Load similarity matrix
        self.similarity_matrix = np.array(model_data.data['similarity_matrix'])
        
        # Load books data
        self.books_df = pd.DataFrame.from_dict(model_data.data['books_data'])
        
        # Load user ratings if they exist
        if model_data.data['user_ratings']:
            self.user_ratings_matrix = pd.DataFrame.from_dict(model_data.data['user_ratings'])
        else:
            self.user_ratings_matrix = pd.DataFrame()
    
    def get_recommendations(self, book_id, num_recommendations=5, user_id=None):
        """Get recommendations using hybrid approach"""
        if self.similarity_matrix is None:
            self.load_model()
            
        try:
            # Content-based recommendations
            book_idx = self.books_df[self.books_df['id'] == book_id].index[0]
            content_scores = list(enumerate(self.similarity_matrix[book_idx]))
            content_scores = sorted(content_scores, key=lambda x: x[1], reverse=True)
            content_recs = [self.books_df.iloc[idx]['id'] for idx, _ in content_scores[1:num_recommendations*2]]
            
            # Collaborative filtering recommendations if we have user data
            if user_id and not self.user_ratings_matrix.empty:
                user_ratings = self.user_ratings_matrix.loc[user_id] if user_id in self.user_ratings_matrix.index else None
                
                if user_ratings is not None:
                    # Find similar users
                    user_similarities = cosine_similarity(
                        self.user_ratings_matrix.loc[user_id].values.reshape(1, -1),
                        self.user_ratings_matrix.values
                    )[0]
                    
                    # Get top similar users
                    similar_users = self.user_ratings_matrix.index[
                        np.argsort(user_similarities)[::-1][1:6]
                    ]
                    
                    # Get books liked by similar users
                    collab_recs = []
                    for similar_user in similar_users:
                        user_books = self.user_ratings_matrix.columns[
                            self.user_ratings_matrix.loc[similar_user] > 3
                        ].tolist()
                        collab_recs.extend(user_books)
                        
                    # Combine recommendations
                    all_recs = []
                    seen = set()
                    
                    # Alternate between content and collaborative recommendations
                    content_idx = 0
                    collab_idx = 0
                    
                    while len(all_recs) < num_recommendations and (content_idx < len(content_recs) or collab_idx < len(collab_recs)):
                        if content_idx < len(content_recs):
                            rec = content_recs[content_idx]
                            if rec not in seen:
                                all_recs.append(rec)
                                seen.add(rec)
                            content_idx += 1
                            
                        if collab_idx < len(collab_recs) and len(all_recs) < num_recommendations:
                            rec = collab_recs[collab_idx]
                            if rec not in seen:
                                all_recs.append(rec)
                                seen.add(rec)
                            collab_idx += 1
                            
                    return all_recs[:num_recommendations]
                    
            # If no user data or collaborative filtering not possible, return content-based recommendations
            return content_recs[:num_recommendations]
            
        except IndexError:
            raise ValueError("Book ID not found")