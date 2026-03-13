import hashlib



def embed_chunks(chunks: list[str], vector_dim: int = 8) -> list[list[float]]:
    """Create deterministic lightweight embeddings for scaffolding.

    Baseline uses SHA256 digest slices to produce stable numeric vectors.
    Extension point: replace with real embedding model provider.
    """
    if vector_dim <= 0:
        raise ValueError("vector_dim must be > 0")

    vectors: list[list[float]] = []
    for chunk in chunks:
        digest = hashlib.sha256(chunk.encode("utf-8")).digest()
        values = [digest[i] / 255.0 for i in range(vector_dim)]
        vectors.append(values)
    return vectors
