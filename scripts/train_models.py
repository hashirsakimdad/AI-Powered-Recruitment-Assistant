"""Train resume detector, job category classifier, and neural network."""

from __future__ import annotations

import os
import pickle
import sys

import numpy as np
import pandas as pd
import sklearn
import torch
import torch.nn as nn
import torch.optim as optim
from sklearn.ensemble import RandomForestClassifier
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics import accuracy_score, classification_report
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from torch.utils.data import DataLoader, TensorDataset

# Ensure project root is on path when run as script
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)
sys.path.insert(0, ROOT)

print("=" * 50)
print("AI Recruitment — Model Training Script")
print("=" * 50)

# Load dataset
df = pd.read_csv("training/data/train.csv")
print(f"\nDataset loaded: {df.shape[0]} rows, {df.shape[1]} columns")
print(f"Columns: {list(df.columns)}")
print(f"\nFirst row:\n{df.iloc[0]}")

# Find text column — try common names
text_col = None
for col in [
    "resume_text",
    "text",
    "Text",
    "Resume",
    "resume",
    "content",
    "description",
    "cv_text",
]:
    if col in df.columns:
        text_col = col
        break

if text_col is None:
    text_col = df.columns[0]

print(f"\nUsing text column: {text_col}")

# Find label column
label_col = None
for col in [
    "label",
    "category",
    "Category",
    "Label",
    "class",
    "job_category",
    "type",
]:
    if col in df.columns:
        label_col = col
        break

if label_col is None:
    label_col = df.columns[-1]

print(f"Using label column: {label_col}")

# Clean text
df[text_col] = df[text_col].fillna("").astype(str)
df[text_col] = df[text_col].str.lower().str.strip()

# Remove empty rows
df = df[df[text_col].str.len() > 50]
print(f"\nAfter cleaning: {df.shape[0]} rows")
print(f"\nLabel distribution:\n{df[label_col].value_counts()}")

# ── Resume Detector ──────────────────────────────────────────────────────────
print("\n" + "=" * 50)
print("Training Resume Detector...")
print("=" * 50)

non_resume_texts = [
    "invoice total amount due payment receipt",
    "meeting agenda item discussion point action",
    "product price list catalogue order form",
    "news article published today events",
    "terms and conditions privacy policy legal",
    "bank statement transaction debit credit balance",
    "recipe ingredients cooking instructions method",
    "sports results match score winner",
    "weather forecast temperature rain sunny",
    "advertisement sale discount offer price",
] * 20

resume_texts = df[text_col].tolist()
all_texts = resume_texts + non_resume_texts
all_labels = [1] * len(resume_texts) + [0] * len(non_resume_texts)

print(f"Vectorizing {len(all_texts)} documents...")
vectorizer = TfidfVectorizer(
    max_features=5000,
    ngram_range=(1, 2),
    min_df=2,
    stop_words="english",
)
X = vectorizer.fit_transform(all_texts)

X_train, X_test, y_train, y_test = train_test_split(
    X, all_labels, test_size=0.2, random_state=42
)

detector = RandomForestClassifier(
    n_estimators=100,
    max_depth=15,
    random_state=42,
    n_jobs=1,
)
detector.fit(X_train, y_train)

y_pred = detector.predict(X_test)
accuracy = accuracy_score(y_test, y_pred)
print(f"\nResume Detector Accuracy: {accuracy:.2%}")
print("\nClassification Report:")
print(
    classification_report(y_test, y_pred, target_names=["Not Resume", "Resume"])
)

os.makedirs("training/models", exist_ok=True)
detector_data = {
    "classifier": detector,
    "vectorizer": vectorizer,
    "sklearn_version": sklearn.__version__,
    "accuracy": accuracy,
    "tfidf_only": True,
}
with open("training/models/resume_detector.pkl", "wb") as f:
    pickle.dump(detector_data, f)
print("\nResume detector saved!")

# ── Job Category Classifier ──────────────────────────────────────────────────
print("\n" + "=" * 50)
print("Training Job Category Classifier...")
print("=" * 50)

le = LabelEncoder()
y_encoded = le.fit_transform(df[label_col])
print(f"Categories found: {len(le.classes_)}")
print(f"Categories: {list(le.classes_)}")

job_vectorizer = TfidfVectorizer(
    max_features=10000,
    ngram_range=(1, 2),
    min_df=1,
    stop_words="english",
)
X_job = job_vectorizer.fit_transform(df[text_col])

X_train_j, X_test_j, y_train_j, y_test_j = train_test_split(
    X_job, y_encoded, test_size=0.2, random_state=42, stratify=y_encoded
)

job_clf = RandomForestClassifier(
    n_estimators=200,
    max_depth=20,
    random_state=42,
    n_jobs=1,
)
job_clf.fit(X_train_j, y_train_j)

y_pred_j = job_clf.predict(X_test_j)
job_accuracy = accuracy_score(y_test_j, y_pred_j)
print(f"\nJob Category Classifier Accuracy: {job_accuracy:.2%}")

job_data = {
    "classifier": job_clf,
    "vectorizer": job_vectorizer,
    "label_encoder": le,
    "categories": list(le.classes_),
    "accuracy": job_accuracy,
}
with open("training/models/job_classifier.pkl", "wb") as f:
    pickle.dump(job_data, f)
print("Job classifier saved!")

# ── Neural Network ───────────────────────────────────────────────────────────
print("\n" + "=" * 50)
print("Training Neural Network...")
print("=" * 50)


class ResumeClassifierNN(nn.Module):
    def __init__(self, input_dim, num_classes):
        super().__init__()
        self.network = nn.Sequential(
            nn.Linear(input_dim, 512),
            nn.BatchNorm1d(512),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(512, 256),
            nn.BatchNorm1d(256),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(256, 128),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(128, num_classes),
        )

    def forward(self, x):
        return self.network(x)


nn_vectorizer = TfidfVectorizer(max_features=2000, stop_words="english")
X_nn = nn_vectorizer.fit_transform(df[text_col]).toarray()
y_nn = y_encoded

X_train_nn, X_test_nn, y_train_nn, y_test_nn = train_test_split(
    X_nn, y_nn, test_size=0.2, random_state=42, stratify=y_nn
)

X_train_t = torch.FloatTensor(X_train_nn)
y_train_t = torch.LongTensor(y_train_nn)
X_test_t = torch.FloatTensor(X_test_nn)
y_test_t = torch.LongTensor(y_test_nn)

dataset = TensorDataset(X_train_t, y_train_t)
loader = DataLoader(dataset, batch_size=32, shuffle=True)

num_classes = len(le.classes_)
input_dim = X_nn.shape[1]
nn_model = ResumeClassifierNN(input_dim, num_classes)

criterion = nn.CrossEntropyLoss()
optimizer = optim.Adam(nn_model.parameters(), lr=0.001)
scheduler = optim.lr_scheduler.StepLR(optimizer, step_size=10, gamma=0.5)

print(f"Training NN: {input_dim} inputs -> {num_classes} classes")
print(f"Training samples: {len(X_train_nn)}")

nn_model.train()
for epoch in range(30):
    total_loss = 0.0
    for batch_X, batch_y in loader:
        optimizer.zero_grad()
        outputs = nn_model(batch_X)
        loss = criterion(outputs, batch_y)
        loss.backward()
        optimizer.step()
        total_loss += loss.item()

    scheduler.step()

    if (epoch + 1) % 10 == 0:
        nn_model.eval()
        with torch.no_grad():
            test_out = nn_model(X_test_t)
            _, predicted = torch.max(test_out, 1)
            nn_acc = (predicted == y_test_t).float().mean()
        nn_model.train()
        avg_loss = total_loss / len(loader)
        print(f"Epoch {epoch + 1}/30 | Loss: {avg_loss:.4f} | Accuracy: {nn_acc:.2%}")

nn_model.eval()
with torch.no_grad():
    test_outputs = nn_model(X_test_t)
    _, nn_predicted = torch.max(test_outputs, 1)
    nn_accuracy = (nn_predicted == y_test_t).float().mean().item()

print(f"\nNeural Network Final Accuracy: {nn_accuracy:.2%}")

torch.save(nn_model.state_dict(), "training/models/nn_classifier.pth")

nn_meta = {
    "vectorizer": nn_vectorizer,
    "label_encoder": le,
    "input_dim": input_dim,
    "num_classes": num_classes,
    "categories": list(le.classes_),
    "accuracy": nn_accuracy,
}
with open("training/models/nn_meta.pkl", "wb") as f:
    pickle.dump(nn_meta, f)
print("Neural network saved!")

print("\n" + "=" * 50)
print("All models saved!")
print(f"  Resume Detector:     {accuracy:.2%}")
print(f"  Job Classifier:      {job_accuracy:.2%}")
print(f"  Neural Network:      {nn_accuracy:.2%}")
print("=" * 50)
