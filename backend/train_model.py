# train_model.py
# Trains a classification model (Random Forest, as listed in the synopsis
# "Technologies Used" section) on the synthetic career-skill dataset,
# then saves the trained model to disk so the Flask API can load it.

import os
import sys
import subprocess
import pandas as pd
import joblib
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

sys.path.append(os.path.join(os.path.dirname(__file__), "data"))
from career_skill_map import ALL_SKILLS

BASE = os.path.dirname(__file__)
DATASET_PATH = os.path.join(BASE, "data", "career_dataset.csv")
MODEL_PATH = os.path.join(BASE, "models", "career_model.pkl")


def main():
    if not os.path.exists(DATASET_PATH):
        print("Dataset not found, generating it first...")
        subprocess.run([sys.executable, os.path.join(BASE, "data", "generate_dataset.py")], check=True)

    df = pd.read_csv(DATASET_PATH)
    X = df[ALL_SKILLS]
    y = df["career"]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    model = RandomForestClassifier(
        n_estimators=200,
        max_depth=12,
        random_state=42,
    )
    model.fit(X_train, y_train)

    preds = model.predict(X_test)
    acc = accuracy_score(y_test, preds)
    print(f"Model trained. Test accuracy: {acc*100:.2f}%")

    os.makedirs(os.path.dirname(MODEL_PATH), exist_ok=True)
    joblib.dump({"model": model, "skill_columns": ALL_SKILLS}, MODEL_PATH)
    print(f"Model saved -> {MODEL_PATH}")


if __name__ == "__main__":
    main()
