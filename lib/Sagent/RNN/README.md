# IMDB Sentiment Analysis with RNN

This project implements a Recurrent Neural Network (RNN) for sentiment analysis on the IMDB movie review dataset. The model classifies reviews as positive or negative.

## Project Structure

```
./RNN/
├── IMDB_Dataset.csv          # IMDB dataset (not included in repo due to size)
├── sentiment_analysis.py     # Main Python script
├── requirements.txt          # Python dependencies
├── README.md                 # This file
├── best_model.h5            # Saved model (generated after training)
├── tokenizer.pkl            # Saved tokenizer (generated after training)
└── evaluation_results.txt   # Evaluation metrics (generated after training)
```

## Features

- **Text Preprocessing**: Cleaning, tokenization, lemmatization, stopword removal
- **RNN Architecture**: Bidirectional RNN with embedding layer
- **Model Training**: Early stopping, model checkpointing
- **Evaluation**: Accuracy, precision, recall, F1-score metrics
- **Prediction**: Single review sentiment prediction with confidence scores

## Model Architecture

1. **Embedding Layer**: Converts words to dense vectors (128 dimensions)
2. **Bidirectional RNN Layer**: 64 units with return sequences
3. **Dropout Layer**: 50% dropout for regularization
4. **RNN Layer**: 32 units
5. **Dropout Layer**: 50% dropout
6. **Dense Layer**: 16 units with ReLU activation
7. **Dropout Layer**: 30% dropout
8. **Output Layer**: 1 unit with sigmoid activation

## Installation

1. Clone the repository
2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Download NLTK data:
```python
import nltk
nltk.download('punkt')
nltk.download('stopwords')
nltk.download('wordnet')
```

## Usage

### Training the Model

```bash
cd RNN
python sentiment_analysis.py
```

The script will:
1. Load the IMDB dataset from `IMDB_Dataset.csv`
2. Preprocess the text data
3. Split data into training (80%), validation (10%), and test (10%) sets
4. Train the RNN model for 10 epochs
5. Save the best model to `best_model.h5`
6. Generate evaluation results in `evaluation_results.txt`

### Making Predictions

You can use the trained model to predict sentiment of new reviews:

```python
from sentiment_analysis import IMDBRNN
import pickle

# Load tokenizer
with open('tokenizer.pkl', 'rb') as f:
    tokenizer = pickle.load(f)

# Initialize model (use same parameters as training)
rnn_model = IMDBRNN(max_vocab_size=10000, max_sequence_length=200, embedding_dim=128)
rnn_model.tokenizer = tokenizer

# Load trained model
rnn_model.model = tf.keras.models.load_model('best_model.h5')

# Predict sentiment
review = "This movie was absolutely fantastic!"
prediction = rnn_model.predict_sentiment(review)
print(f"Sentiment: {prediction['sentiment']}")
print(f"Confidence: {prediction['confidence']:.2%}")
```

## Data Split

The dataset is split as follows:
- **Training**: 80% of original data
- **Validation**: 10% of training data (for early stopping)
- **Test**: 20% of original data (held out for final evaluation)

## Performance Metrics

The model evaluates on:
- **Accuracy**: Overall correct predictions
- **Precision**: Correct positive predictions among all positive predictions
- **Recall**: Correct positive predictions among all actual positives
- **F1-Score**: Harmonic mean of precision and recall

## Customization

You can adjust model parameters in the `IMDBRNN` class initialization:

```python
# Example: Larger vocabulary and longer sequences
rnn_model = IMDBRNN(
    max_vocab_size=20000,
    max_sequence_length=300,
    embedding_dim=256
)
```

## Notes

- The IMDB dataset should be in CSV format with columns: `review` and `sentiment`
- The `sentiment` column should contain 'positive' or 'negative' values
- Training may take several hours depending on hardware and dataset size
- Consider using GPU acceleration for faster training

## Dependencies

See `requirements.txt` for complete list of Python packages required.

## License

This project is for educational purposes. The IMDB dataset is available for research use.