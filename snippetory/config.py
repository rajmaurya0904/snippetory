"""Configuration defaults for Snippetory."""

# Embedding dimensions for the vector store
EMBEDDING_DIMENSIONS = 384

# Maximum number of tokens in a chunk
CHUNK_SIZE = 256

# Overlap between chunks in tokens
OVERLAP = 32

# Default path for the vector database (relative to current working directory)
DATABASE_PATH = ".snippetory/vectors"