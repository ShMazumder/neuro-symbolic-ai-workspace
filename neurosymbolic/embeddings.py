"""
neurosymbolic/embeddings.py
Task 4.2 — KG Embeddings: TransE, ComplEx, RotatE.

Trains knowledge graph embedding models on the exported triple set.
Uses PyKEEN for standardised KGE training and evaluation.
"""

from __future__ import annotations

import json
import logging
import pickle
from pathlib import Path
from typing import Optional, Literal

logger = logging.getLogger(__name__)

MODELS_DIR = Path("models/embeddings")
KG_EXPORT_DIR = Path("data/kg_export")

EmbeddingModel = Literal["TransE", "ComplEx", "RotatE"]


def _load_triples(kg_path: Path = KG_EXPORT_DIR / "kg_graph.pkl"):
    """Load KGGraph and convert to PyKEEN TriplesFactory."""
    try:
        import pykeen.triples as pkt
    except ImportError:
        raise ImportError(
            "PyKEEN not installed. Run: pip install pykeen"
        )

    with open(kg_path, "rb") as f:
        kg = pickle.load(f)

    # Build string-triple list: [(head_uri, relation, tail_uri)]
    triples = [(s, r, d) for s, r, d in kg.edges]

    if not triples:
        raise ValueError("No triples found in KGGraph. Run kg_export first.")

    import numpy as np
    triple_array = np.array(triples, dtype=str)
    factory = pkt.TriplesFactory.from_labeled_triples(triple_array)
    logger.info("TriplesFactory: %d triples, %d entities, %d relations.",
                factory.num_triples, factory.num_entities, factory.num_relations)
    return factory


def train_embedding(
    model_name: EmbeddingModel = "TransE",
    embedding_dim: int = 128,
    num_epochs: int = 200,
    batch_size: int = 512,
    learning_rate: float = 1e-3,
    kg_path: Path = KG_EXPORT_DIR / "kg_graph.pkl",
    out_dir: Path = MODELS_DIR,
) -> dict:
    """
    Train a KG embedding model using PyKEEN.

    Args:
        model_name:    "TransE" | "ComplEx" | "RotatE"
        embedding_dim: Dimension of entity and relation embeddings.
        num_epochs:    Training epochs.
        batch_size:    Batch size for negative sampling.
        learning_rate: Adam optimizer learning rate.
        kg_path:       Path to exported KGGraph pickle.
        out_dir:       Directory to save model artifacts.

    Returns:
        Dict with training metrics (MRR, Hits@1, Hits@10).
    """
    try:
        from pykeen.pipeline import pipeline as pykeen_pipeline
        from pykeen.triples import TriplesFactory
    except ImportError:
        raise ImportError("PyKEEN not installed. Run: pip install pykeen")

    factory = _load_triples(kg_path)

    # 80/10/10 split
    training, testing, validation = factory.split([0.8, 0.1, 0.1])

    logger.info("Training %s (dim=%d, epochs=%d)…", model_name, embedding_dim, num_epochs)

    result = pykeen_pipeline(
        model=model_name,
        training=training,
        testing=testing,
        validation=validation,
        model_kwargs={"embedding_dim": embedding_dim},
        training_kwargs={
            "num_epochs": num_epochs,
            "batch_size": batch_size,
        },
        optimizer="adam",
        optimizer_kwargs={"lr": learning_rate},
        loss="marginranking" if model_name == "TransE" else "softplus",
        evaluator="rankbased",
        random_seed=42,
        device="cpu",
    )

    # Save model
    out_dir.mkdir(parents=True, exist_ok=True)
    model_path = out_dir / f"{model_name.lower()}_dim{embedding_dim}"
    result.save_to_directory(str(model_path))

    metrics = {
        "model":        model_name,
        "embedding_dim": embedding_dim,
        "num_epochs":   num_epochs,
        "mrr":          result.get_metric("mean_reciprocal_rank"),
        "hits_at_1":    result.get_metric("hits_at_1"),
        "hits_at_10":   result.get_metric("hits_at_10"),
        "model_path":   str(model_path),
    }

    (model_path / "metrics.json").write_text(
        json.dumps(metrics, indent=2), encoding="utf-8"
    )
    logger.info(
        "%s training complete. MRR=%.4f, H@1=%.4f, H@10=%.4f",
        model_name, metrics["mrr"], metrics["hits_at_1"], metrics["hits_at_10"],
    )
    return metrics


def load_embeddings(model_name: EmbeddingModel = "TransE",
                    embedding_dim: int = 128,
                    models_dir: Path = MODELS_DIR):
    """Load a saved PyKEEN model and return entity/relation embedding tensors."""
    try:
        import torch
        from pykeen.models import model_resolver
    except ImportError:
        raise ImportError("PyKEEN / PyTorch not installed.")

    model_path = models_dir / f"{model_name.lower()}_dim{embedding_dim}"
    if not model_path.exists():
        raise FileNotFoundError(
            f"No saved model at {model_path}. Run train_embedding first."
        )

    model = torch.load(model_path / "trained_model.pkl", map_location="cpu")
    entity_emb   = model.entity_representations[0]().detach()
    relation_emb = model.relation_representations[0]().detach()
    logger.info(
        "Loaded %s embeddings: entities=%s, relations=%s",
        model_name, tuple(entity_emb.shape), tuple(relation_emb.shape),
    )
    return entity_emb, relation_emb


def get_similar_entities(
    entity_uri: str,
    model_name: EmbeddingModel = "TransE",
    embedding_dim: int = 128,
    top_k: int = 10,
    models_dir: Path = MODELS_DIR,
    kg_path: Path = KG_EXPORT_DIR / "kg_graph.pkl",
) -> list[tuple[str, float]]:
    """
    Find the top-k most similar entities to a given URI using cosine similarity.

    Returns:
        List of (entity_uri, similarity_score) sorted by decreasing similarity.
    """
    import torch
    import pickle

    with open(kg_path, "rb") as f:
        kg = pickle.load(f)

    entity_emb, _ = load_embeddings(model_name, embedding_dim, models_dir)
    idx = kg.node_index.get(entity_uri)
    if idx is None:
        raise ValueError(f"Entity not in KG: {entity_uri}")

    query_vec = entity_emb[idx].unsqueeze(0)
    sims = torch.nn.functional.cosine_similarity(query_vec, entity_emb, dim=1)
    sims[idx] = -1.0   # exclude self

    top_indices = sims.topk(top_k).indices.tolist()
    idx_to_uri = {v: k for k, v in kg.node_index.items()}

    return [(idx_to_uri[i], round(sims[i].item(), 4)) for i in top_indices]


# Alias for singular import compatibility
load_embedding = load_embeddings


def predict_link(
    head_uri: str,
    relation: str,
    tail_uri: str,
    model_name: EmbeddingModel = "TransE",
    embedding_dim: int = 128,
    model_path: Optional[Path] = None,
    kg_path: Path = KG_EXPORT_DIR / "kg_graph.pkl",
) -> float:
    """
    Predict link plausibility score for a triple (head, relation, tail).
    Returns plausibility probability in [0, 1].
    """
    import pickle
    import torch

    if not kg_path.exists():
        return 0.5

    try:
        with open(kg_path, "rb") as f:
            kg = pickle.load(f)

        models_dir = model_path.parent if model_path else MODELS_DIR
        entity_emb, rel_emb = load_embeddings(model_name, embedding_dim, models_dir=models_dir)

        h_idx = kg.node_index.get(head_uri)
        t_idx = kg.node_index.get(tail_uri)
        r_idx = kg.rel_index.get(relation)
        if h_idx is None or t_idx is None or r_idx is None:
            return 0.5

        h = entity_emb[h_idx]
        t = entity_emb[t_idx]
        r = rel_emb[r_idx]
        diff = torch.norm(h + r - t, p=2)
        score = torch.sigmoid(-diff).item()
        return round(float(score), 4)
    except Exception as exc:
        logger.warning("predict_link failed: %s", exc)
        return 0.5



# ── CLI ───────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import sys
    logging.basicConfig(level=logging.INFO,
                        format="%(asctime)s %(levelname)-8s %(message)s")

    model = sys.argv[1] if len(sys.argv) > 1 else "TransE"
    metrics = train_embedding(model_name=model, num_epochs=100)
    print(json.dumps(metrics, indent=2))
