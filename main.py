import numpy as np
import faiss
from sentence_transformers import SentenceTransformer
from rank_bm25 import BM25Okapi

# ------------------------
# Embedding model
# ------------------------
model = SentenceTransformer('all-MiniLM-L6-v2')

# ------------------------
# Load data
# ------------------------
with open("data.txt", "r", encoding="utf-8") as f:
    text = f.read()

# ------------------------
# Chunking
# ------------------------
chunks = []
chunk_size = 200
overlap = 50
start = 0

while start < len(text):
    end = start + chunk_size
    chunks.append(text[start:end])
    start += chunk_size - overlap

# ------------------------
# VECTOR SEARCH (FAISS)
# ------------------------
embeddings = model.encode(chunks).astype("float32")
faiss.normalize_L2(embeddings)

index = faiss.IndexFlatIP(embeddings.shape[1])
index.add(embeddings)

# ------------------------
# BM25 SETUP
# ------------------------
tokenized_chunks = [c.lower().split() for c in chunks]
bm25 = BM25Okapi(tokenized_chunks)

# ------------------------
# QUERY
# ------------------------
query = input("Ask: ")

# ------------------------
# VECTOR RESULTS
# ------------------------
q_emb = model.encode([query]).astype("float32")
faiss.normalize_L2(q_emb)

vec_scores, vec_indices = index.search(q_emb, 5)

# ------------------------
# BM25 RESULTS
# ------------------------
bm25_scores = bm25.get_scores(query.lower().split())
bm25_indices = np.argsort(bm25_scores)[::-1][:5]
# ------------------------
# MERGE CANDIDATES
# ------------------------
candidate_indices = set(vec_indices[0]) | set(bm25_indices)

# ------------------------
# SIMPLE RERANK (baseline)
# ------------------------
reranked = []

for i in candidate_indices:
    score = vec_scores[0][list(vec_indices[0]).index(i)] if i in vec_indices[0] else 0
    score += bm25_scores[i]
    reranked.append((score, i))

reranked.sort(reverse=True)

top_chunks = [chunks[i] for _, i in reranked[:3]]

# ------------------------
# OUTPUT
# ------------------------
print("\nTOP ANSWER CONTEXT:\n")
for c in top_chunks:
    print(c)
    print("-" * 40)