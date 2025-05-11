from sentence_transformers import SentenceTransformer

model = SentenceTransformer('all-MiniLM-L6-v2')

def embed_texts(texts):
    return model.encode(texts, convert_to_tensor=True)

def embed_single(text):
    return model.encode(text, convert_to_tensor=True)