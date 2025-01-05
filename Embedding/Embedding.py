from langchain_core.embeddings.embeddings import Embeddings
from transformers import RobertaTokenizer, RobertaModel
import numpy as np
import torch

class CodeEmbeddingFunction(Embeddings):
    def __init__(self):
        self.tokenizer = RobertaTokenizer.from_pretrained("microsoft/codebert-base")
        self.model = RobertaModel.from_pretrained(
                "microsoft/codebert-base",
                add_pooling_layer=False,
                cache_dir="./model_cache"
            )

        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.device= torch.device("mps" if torch.backends.mps.is_available() else "cpu")
        self.model.to(self.device)

    def embed_documents(self, texts):
        # Get embeddings for each document (text)
        embeddings = np.array([self.embed_single_document(text) for text in texts])
        return embeddings

    def embed_single_document(self, code):
        inputs = self.tokenizer(code, return_tensors="pt", truncation=True, max_length=512, padding="max_length")
        inputs = {key: value.to(self.device) for key, value in inputs.items()}
        
        with torch.no_grad():
            outputs = self.model(**inputs)
        
        # Average pooling of hidden states to get the final embedding
        embedding = outputs.last_hidden_state.mean(dim=1).squeeze().cpu().numpy()
        return embedding
    
    def embed_query(self, query):
        return self.embed_single_document(query)