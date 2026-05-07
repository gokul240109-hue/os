import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.ensemble import RandomForestClassifier
import pickle
import os

def train_model(df):
    vectorizer = CountVectorizer()
    X = vectorizer.fit_transform(df["message"])
    y = df["level"]

    model = RandomForestClassifier()
    model.fit(X, y)

    # Create models directory if it doesn't exist
    models_dir = os.path.join(os.path.dirname(__file__), 'models')
    os.makedirs(models_dir, exist_ok=True)
    
    pickle.dump(model, open(os.path.join(models_dir, "ml_model.pkl"), "wb"))
    pickle.dump(vectorizer, open(os.path.join(models_dir, "vectorizer.pkl"), "wb"))
