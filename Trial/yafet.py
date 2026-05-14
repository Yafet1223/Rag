import numpy as np
import faiss
from sentence_transformers import SentenceTransformer

model = SentenceTransformer('all-MiniLM-L6-v2')
#load data
with open("data.txt","r", encoding="utf-8") as f:
    text=f.read()
#chunking
chunks=[]
chunk_size=200
overlap=50
start=0
while start<len(text):
    end=start + chunk_size
    chunks.append(text[start:end])
    start +=  chunk_size-overlap
 #vector Search
 emb=model.encode(chunks).astype("float32")
 faiss.normalize_L2(emb)
 index=faiss.IndexFlatIP(embeddings.shape[1])
 index.add(embeddings)

#BM25SETUP
tokenized_chunks = [c.lower().split() for c in chunks]
bm25 = BM25Okapi(tokenized_chunks)
#query
query=input("Ask:")
#vector Result
q_emb = model.encode([query]).astype("float32")
faiss.normalize_L2(q_emb)

vec_scores, vec_indices = index.search(q_emb, 5)
#BM25 RESULTS
candidate_indices = set(vec_indices[0]) | set(bm25_indices)
print("\nTOP ANSWER CONTEXT:\n")
for c in top_chunks:
    print(c)
    print("-" * 40)