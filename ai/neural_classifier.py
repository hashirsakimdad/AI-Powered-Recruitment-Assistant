import logging
import os

import numpy as np
import torch
import torch.nn as nn

from ai.scorer import get_model

logger = logging.getLogger(__name__)


class ResumeMatchNetwork(nn.Module):
    """
    Simple feedforward neural network for resume-job matching.
    Input: concatenated resume + job embeddings (1536 dims for mpnet)
    Output: match probability (0 to 1)
    """

    def __init__(self, input_dim=1536, hidden_dim=256, dropout=0.3):
        super(ResumeMatchNetwork, self).__init__()

        self.network = nn.Sequential(
            nn.Linear(input_dim, hidden_dim),
            nn.BatchNorm1d(hidden_dim),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(hidden_dim, hidden_dim // 2),
            nn.BatchNorm1d(hidden_dim // 2),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(hidden_dim // 2, 64),
            nn.ReLU(),
            nn.Linear(64, 1),
            nn.Sigmoid(),
        )

    def forward(self, x):
        return self.network(x)


def _weights_path() -> str:
    return os.path.join(os.path.dirname(__file__), "models", "resume_classifier.pth")


def get_neural_score(resume_text: str, job_description: str) -> dict:
    """
    Get neural network confidence score for resume-job match.
    Falls back to cosine similarity if model weights not available.
    """
    try:
        model = get_model()
        resume_emb = model.encode(resume_text, convert_to_tensor=True)
        job_emb = model.encode(job_description, convert_to_tensor=True)

        combined = torch.cat(
            [resume_emb.reshape(-1), job_emb.reshape(-1)], dim=0
        ).unsqueeze(0)
        weights_path = _weights_path()

        if os.path.exists(weights_path):
            net = ResumeMatchNetwork(input_dim=combined.shape[-1])
            net.load_state_dict(torch.load(weights_path, map_location=torch.device("cpu")))
            net.eval()

            with torch.no_grad():
                confidence = net(combined).item()

            source = "neural_network"
        else:
            from sentence_transformers import util

            confidence = float(util.cos_sim(resume_emb, job_emb)[0][0])
            confidence = (confidence + 1) / 2
            source = "cosine_similarity_fallback"

        if confidence >= 0.75:
            label = "Strong Match"
            color = "success"
        elif confidence >= 0.50:
            label = "Moderate Match"
            color = "warning"
        else:
            label = "Weak Match"
            color = "danger"

        return {
            "confidence": round(confidence * 100, 1),
            "label": label,
            "color": color,
            "source": source,
        }

    except Exception as e:
        logger.warning("Neural classifier error: %s", e, exc_info=True)
        return {
            "confidence": 50.0,
            "label": "Unable to classify",
            "color": "secondary",
            "source": "error",
        }


def train_on_existing_data():
    """
    Train neural network on existing submissions in database.
    Run this once when you have 50+ submissions.
    Call: python -c "from ai.neural_classifier import train_on_existing_data; train_on_existing_data()"
    """
    try:
        from models import JobPosting, ResumeSubmission, db

        submissions = ResumeSubmission.query.filter(
            ResumeSubmission.score.isnot(None),
            ResumeSubmission.scoring_status == "scored",
        ).all()

        if len(submissions) < 10:
            print(f"Need at least 10 submissions, have {len(submissions)}")
            return False

        print(f"Training on {len(submissions)} submissions...")

        semantic_model = get_model()
        X, y = [], []

        for sub in submissions:
            try:
                job = db.session.get(JobPosting, sub.job_id)
                if not job or not sub.parsed_summary:
                    continue

                resume_text = str(sub.parsed_summary)
                job_text = f"{job.title} {job.description} {job.required_skills}"

                resume_emb = semantic_model.encode(resume_text)
                job_emb = semantic_model.encode(job_text)
                combined = np.concatenate([resume_emb, job_emb])

                X.append(combined)
                y.append(1.0 if sub.score >= 60 else 0.0)

            except Exception:
                continue

        if len(X) < 10:
            print("Not enough valid data")
            return False

        X_tensor = torch.FloatTensor(np.array(X))
        y_tensor = torch.FloatTensor(y).unsqueeze(1)

        input_dim = X_tensor.shape[1]
        net = ResumeMatchNetwork(input_dim=input_dim)
        optimizer = torch.optim.Adam(net.parameters(), lr=0.001)
        criterion = nn.BCELoss()

        net.train()
        for epoch in range(100):
            optimizer.zero_grad()
            outputs = net(X_tensor)
            loss = criterion(outputs, y_tensor)
            loss.backward()
            optimizer.step()

            if (epoch + 1) % 20 == 0:
                print(f"Epoch {epoch + 1}/100, Loss: {loss.item():.4f}")

        models_dir = os.path.join(os.path.dirname(__file__), "models")
        os.makedirs(models_dir, exist_ok=True)
        torch.save(net.state_dict(), _weights_path())
        print("Neural network trained and saved!")
        return True

    except Exception as e:
        print(f"Training error: {e}")
        return False
