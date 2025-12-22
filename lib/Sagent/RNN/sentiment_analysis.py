#!/usr/bin/env python3
"""
IMDB Sentiment Analysis using RNN
This script trains an RNN model to classify IMDB reviews as positive or negative.
"""

import os
import numpy as np
import pandas as pd
import tensorflow as tf
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Embedding, SimpleRNN, Dense, Dropout, Bidirectional
from tensorflow.keras.callbacks import EarlyStopping, ModelCheckpoint
from sklearn.model_selection import train_test_split
import re
import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
import warnings
warnings.filterwarnings('ignore')

# Download NLTK resources if not already present
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')
try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords')
try:
    nltk.data.find('corpora/wordnet')
except LookupError:
    nltk.download('wordnet')

class IMDBRNN:
    """
    RNN-based sentiment analysis model for IMDB reviews
    """
    
    def __init__(self, max_vocab_size=10000, max_sequence_length=200, embedding_dim=128):
        """
        Initialize the RNN model with preprocessing parameters
        
        Args:
            max_vocab_size: Maximum number of words to keep in vocabulary
            max_sequence_length: Maximum length of text sequences
            embedding_dim: Dimension of word embeddings
        """
        self.max_vocab_size = max_vocab_size
        self.max_sequence_length = max_sequence_length
        self.embedding_dim = embedding_dim
        
        # Initialize preprocessing components
        self.tokenizer = Tokenizer(num_words=max_vocab_size, oov_token='<OOV>')
        self.stop_words = set(stopwords.words('english'))
        self.lemmatizer = WordNetLemmatizer()
        
        # Model will be built later
        self.model = None
        
    def clean_text(self, text):
        """
        Clean and preprocess text data
        """
        if not isinstance(text, str):
            return ""
        
        # Convert to lowercase
        text = text.lower()
        
        # Remove HTML tags
        text = re.sub(r'<.*?>', ' ', text)
        
        # Remove URLs
        text = re.sub(r'https?://\S+|www\.\S+', ' ', text)
        
        # Remove special characters and numbers
        text = re.sub(r'[^a-zA-Z\s]', ' ', text)
        
        # Tokenize
        tokens = nltk.word_tokenize(text)
        
        # Remove stopwords and lemmatize
        tokens = [self.lemmatizer.lemmatize(word) for word in tokens 
                 if word not in self.stop_words and len(word) > 2]
        
        return ' '.join(tokens)
    
    def preprocess_data(self, reviews, labels, fit_tokenizer=True):
        """
        Preprocess reviews and convert to sequences
        """
        # Clean reviews
        print("Cleaning text data...")
        cleaned_reviews = [self.clean_text(review) for review in reviews]
        
        # Fit or use tokenizer
        if fit_tokenizer:
            print("Fitting tokenizer...")
            self.tokenizer.fit_on_texts(cleaned_reviews)
        
        # Convert to sequences
        sequences = self.tokenizer.texts_to_sequences(cleaned_reviews)
        
        # Pad sequences
        padded_sequences = pad_sequences(
            sequences, 
            maxlen=self.max_sequence_length, 
            padding='post', 
            truncating='post'
        )
        
        # Convert labels to numpy array
        label_map = {'positive': 1, 'negative': 0}
        if isinstance(labels[0], str):
            numeric_labels = np.array([label_map[label] for label in labels])
        else:
            numeric_labels = np.array(labels)
        
        return padded_sequences, numeric_labels
    
    def build_model(self):
        """
        Build the RNN model architecture
        """
        model = Sequential([
            # Embedding layer
            Embedding(
                input_dim=self.max_vocab_size, 
                output_dim=self.embedding_dim, 
                input_length=self.max_sequence_length
            ),
            
            # Bidirectional RNN layer
            Bidirectional(SimpleRNN(64, return_sequences=True)),
            Dropout(0.5),
            
            # Second RNN layer
            SimpleRNN(32),
            Dropout(0.5),
            
            # Dense layers
            Dense(16, activation='relu'),
            Dropout(0.3),
            
            # Output layer
            Dense(1, activation='sigmoid')
        ])
        
        # Compile model
        model.compile(
            optimizer='adam',
            loss='binary_crossentropy',
            metrics=['accuracy', tf.keras.metrics.Precision(), tf.keras.metrics.Recall()]
        )
        
        self.model = model
        print("Model built successfully!")
        model.summary()
        return model
    
    def train(self, X_train, y_train, X_val, y_val, epochs=10, batch_size=32):
        """
        Train the RNN model
        """
        if self.model is None:
            self.build_model()
        
        # Callbacks
        callbacks = [
            EarlyStopping(monitor='val_loss', patience=3, restore_best_weights=True),
            ModelCheckpoint(
                './RNN/best_model.h5', 
                monitor='val_accuracy', 
                save_best_only=True,
                verbose=1
            )
        ]
        
        print(f"Training model for {epochs} epochs with batch size {batch_size}...")
        
        history = self.model.fit(
            X_train, y_train,
            epochs=epochs,
            batch_size=batch_size,
            validation_data=(X_val, y_val),
            callbacks=callbacks,
            verbose=1
        )
        
        return history
    
    def evaluate(self, X_test, y_test):
        """
        Evaluate model on test data
        """
        if self.model is None:
            raise ValueError("Model not built or trained yet!")
        
        print("Evaluating model on test data...")
        results = self.model.evaluate(X_test, y_test, verbose=0)
        
        metrics = {
            'loss': results[0],
            'accuracy': results[1],
            'precision': results[2],
            'recall': results[3],
            'f1_score': 2 * (results[2] * results[3]) / (results[2] + results[3] + 1e-7)
        }
        
        return metrics
    
    def predict_sentiment(self, review):
        """
        Predict sentiment for a single review
        """
        if self.model is None:
            raise ValueError("Model not loaded!")
        
        # Preprocess the review
        cleaned_review = self.clean_text(review)
        sequence = self.tokenizer.texts_to_sequences([cleaned_review])
        padded_sequence = pad_sequences(
            sequence, 
            maxlen=self.max_sequence_length, 
            padding='post', 
            truncating='post'
        )
        
        # Make prediction
        prediction = self.model.predict(padded_sequence, verbose=0)[0][0]
        sentiment = "positive" if prediction > 0.5 else "negative"
        confidence = prediction if prediction > 0.5 else 1 - prediction
        
        return {
            'sentiment': sentiment,
            'confidence': float(confidence),
            'raw_score': float(prediction)
        }

def load_and_split_data(file_path='./RNN/IMDB_Dataset.csv', test_size=0.2, random_state=42):
    """
    Load IMDB dataset and split into train/test sets
    """
    print(f"Loading dataset from {file_path}...")
    
    # Load dataset
    df = pd.read_csv(file_path)
    
    # Verify columns
    if 'review' not in df.columns or 'sentiment' not in df.columns:
        raise ValueError("Dataset must contain 'review' and 'sentiment' columns")
    
    print(f"Dataset loaded: {len(df)} samples")
    print(f"Class distribution:{df['sentiment'].value_counts()}")
    
    # Split data
    X = df['review'].values
    y = df['sentiment'].values
    
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, 
        test_size=test_size, 
        random_state=random_state,
        stratify=y
    )
    
    print(f"Training set: {len(X_train)} samples")
    print(f"Test set: {len(X_test)} samples")
    
    return X_train, X_test, y_train, y_test

def main():
    """
    Main execution function
    """
    print("=" * 60)
    print("IMDB Sentiment Analysis with RNN")
    print("=" * 60)
    
    # Load and split data
    try:
        X_train, X_test, y_train, y_test = load_and_split_data()
    except Exception as e:
        print(f"Error loading data: {e}")
        print("Using sample data for demonstration...")
        # Create sample data if actual dataset can't be loaded
        sample_reviews = [
            "This movie was absolutely fantastic! The acting was superb.",
            "Terrible film, waste of time. Poor direction and bad acting.",
            "I enjoyed it quite a bit, though it had some slow parts.",
            "One of the worst movies I've ever seen in my life.",
            "Brilliant cinematography and compelling storyline."
        ]
        sample_labels = ['positive', 'negative', 'positive', 'negative', 'positive']
        X_train, X_test, y_train, y_test = train_test_split(
            sample_reviews, sample_labels, test_size=0.2, random_state=42
        )
    
    # Initialize RNN model
    rnn_model = IMDBRNN(
        max_vocab_size=10000,
        max_sequence_length=200,
        embedding_dim=128
    )
    
    # Preprocess training data
    print("Preprocessing training data...")
    X_train_processed, y_train_processed = rnn_model.preprocess_data(X_train, y_train, fit_tokenizer=True)
    
    # Preprocess test data
    print("Preprocessing test data...")
    X_test_processed, y_test_processed = rnn_model.preprocess_data(X_test, y_test, fit_tokenizer=False)
    
    # Further split training data for validation
    X_train_final, X_val, y_train_final, y_val = train_test_split(
        X_train_processed, y_train_processed, 
        test_size=0.1, 
        random_state=42
    )
    
    print(f"Final dataset sizes:")
    print(f"Training: {len(X_train_final)} samples")
    print(f"Validation: {len(X_val)} samples")
    print(f"Test: {len(X_test_processed)} samples")
    
    # Build and train model
    print("" + "=" * 60)
    print("Building and Training RNN Model")
    print("=" * 60)
    
    history = rnn_model.train(
        X_train_final, y_train_final,
        X_val, y_val,
        epochs=10,
        batch_size=32
    )
    
    # Evaluate model
    print("" + "=" * 60)
    print("Model Evaluation")
    print("=" * 60)
    
    metrics = rnn_model.evaluate(X_test_processed, y_test_processed)
    
    print("Test Set Metrics:")
    for metric, value in metrics.items():
        print(f"  {metric}: {value:.4f}")
    
    # Save evaluation results
    results_file = './RNN/evaluation_results.txt'
    with open(results_file, 'w') as f:
        f.write("IMDB Sentiment Analysis RNN - Evaluation Results")
        f.write("=" * 50 + "")
        f.write(f"Model Architecture: Bidirectional RNN with Embedding")
        f.write(f"Vocabulary Size: {rnn_model.max_vocab_size}")
        f.write(f"Max Sequence Length: {rnn_model.max_sequence_length}")
        f.write(f"Embedding Dimension: {rnn_model.embedding_dim}")
        
        f.write("Test Set Performance:")
        for metric, value in metrics.items():
            f.write(f"  {metric}: {value:.4f}")
    
    print(f"Evaluation results saved to {results_file}")
    
    # Test with sample predictions
    print("" + "=" * 60)
    print("Sample Predictions")
    print("=" * 60)
    
    test_reviews = [
        "This movie was absolutely wonderful! I loved every minute of it.",
        "A complete disaster. The plot made no sense and the acting was terrible.",
        "It was okay, not great but not terrible either."
    ]
    
    for review in test_reviews:
        prediction = rnn_model.predict_sentiment(review)
        print(f"Review: {review[:50]}...")
        print(f"  Sentiment: {prediction['sentiment']}")
        print(f"  Confidence: {prediction['confidence']:.2%}")
    
    print("" + "=" * 60)
    print("Training Complete!")
    print("=" * 60)
    print(f"Files created:")
    print(f"  1. {os.path.abspath('./RNN/sentiment_analysis.py')}")
    print(f"  2. ./RNN/best_model.h5 (saved during training)")
    print(f"  3. {os.path.abspath('./RNN/evaluation_results.txt')}")
    
    # Save the tokenizer for future use
    import pickle
    with open('./RNN/tokenizer.pkl', 'wb') as f:
        pickle.dump(rnn_model.tokenizer, f)
    print(f"  4. ./RNN/tokenizer.pkl (saved tokenizer)")

if __name__ == "__main__":
    main()