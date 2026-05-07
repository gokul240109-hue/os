import pickle
import os
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline

models_dir = os.path.join(os.path.dirname(__file__), 'models')

# Keywords for severity mapping
SEVERITY_KEYWORDS = {
    'CRITICAL': ['critical', 'fatal', 'panic', 'crash', 'failure', 'failed', 'error', 'down', 'disk space'],
    'ERROR': ['error', 'failed', 'failure', 'exception', 'warning', 'high', 'above threshold'],
    'WARNING': ['warning', 'high', 'usage', 'temperature', 'slow', 'timeout'],
    'INFO': ['info', 'successful', 'completed', 'started', 'logged']
}

def _try_load(paths):
    for p in paths:
        if os.path.exists(p):
            try:
                return pickle.load(open(p, "rb"))
            except Exception:
                continue
    return None

# Try to load existing model
model = _try_load([os.path.join(models_dir, "ml_model.pkl")])

def train_model_simple(df):
    """Train a simple model using TF-IDF and Naive Bayes"""
    try:
        if df.empty or 'message' not in df.columns or 'level' not in df.columns:
            return False
        
        # Create pipeline
        pipeline = Pipeline([
            ('tfidf', TfidfVectorizer(max_features=100, lowercase=True, stop_words='english')),
            ('clf', MultinomialNB())
        ])
        
        # Train
        pipeline.fit(df['message'].fillna(''), df['level'])
        
        # Save
        os.makedirs(models_dir, exist_ok=True)
        pickle.dump(pipeline, open(os.path.join(models_dir, "ml_model.pkl"), "wb"))
        
        return True
    except Exception as e:
        print(f"Error training model: {e}")
        return False

def keyword_predict(message):
    """Fallback: Predict severity using keywords"""
    msg_lower = message.lower()
    
    for level, keywords in SEVERITY_KEYWORDS.items():
        for keyword in keywords:
            if keyword in msg_lower:
                return level
    
    return 'INFO'  # Default

def model_predict(messages):
    """Predict log severity"""
    global model
    
    if not messages or not messages[0]:
        return ['INFO']
    
    try:
        # Use trained model if available
        if model is not None:
            predictions = model.predict(messages)
            return predictions.tolist()
    except Exception as e:
        print(f"Model prediction error: {e}")
    
    # Fallback to keyword-based prediction
    return [keyword_predict(msg) for msg in messages]

