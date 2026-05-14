import numpy as np
import faiss
from sentence_transformers import SentenceTransformer
import google.generativeai as genai
from rank_bm25 import BM25Okapi
genai.configure(api_key="AIzaSyDrNgEGwWUUv5NoONCols-gCV2_x2i27hM")
model = SentenceTransformer('all-MiniLM-L6-v2')
gemini_model = genai.GenerativeModel("gemini-2.5-flash")

with open("bio.txt", "r", encoding="utf-8") as f:
    text = f.read()
chunks = []
chunk_size = 200
overlap = 50
start = 0

while start < len(text):
    end = start + chunk_size
    chunks.append(text[start:end])
    start += chunk_size - overlap
 #Vector Serch   
emb = model.encode(chunks).astype("float32")
faiss.normalize_L2(emb)


index=faiss.IndexFlatIP(emb.shape[1])
index.add(emb)
 #bm25
tokenized_chunks = [c.lower().split() for c in chunks]
bm25 = BM25Okapi(tokenized_chunks)
#query
query = input("Ask: ")
q_emb = model.encode([query]).astype("float32")
faiss.normalize_L2(q_emb)

#vector Results
vec_scores, vec_indices = index.search(q_emb, 5)
#BM25 RESULTS
bm25_scores = bm25.get_scores(query.lower().split())
bm25_indices = np.argsort(bm25_scores)[::-1][:5]
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
#prompt
prompt=f"""
Anwer the question ONLY using the context below
context:{top_chunks}
question:{query}
"""
response=gemini_model.generate_content(prompt)
print("Answer")
print(response.text)



