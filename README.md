# Code-Chat
RAG on codebase for question answering

# Architecture
```mermaid
flowchart TD
    subgraph Agent [Agent]
    AA2[Query] --> A2
    A2[Groq-Tool LLM] --> B2{Tools}
    B2 --> C2(((Wikipedia)))
    B2 --> D2(((Youtube)))
    B2 --> RAG
    G -->E2[Tool Response]
    C2-->E2
    D2-->E2
    E2 --> F2[Groq-Tool LLM]
    F2 --> G2[Response To User]
    end
    subgraph RAG [Code RAG]
        direction TB
        A[Query] --> |Query Translation| B(CodeLlama LLM)
        B --> C[Query Enhanced for Retrieval]
        C --> |CodeBERT Embedding| D[Query Embedding]
        D1 --> E[[Relevant Code Snippets]]
        E --> F(CodeLlama LLM)
        F --> G[Streamed Output]
    end
    
    subgraph VD [Vector Database]
        D1[(Vector Database)]
        C1[[Files of code]] --> E1{{Language Specific Text Splitter}}
        E1 --> F1[[Documents of code chunks]]
        F1 --> |Summarize Code| G1[CodeLlama LLM]
        G1 --> H1[[Documents of Summaries of Code Snippets]]
        H1 --> |CodeBERT Embeddings|D1
    end

    
    
    D-->|Vector Similarity Search|D1
    
```

# Relevant Papers
- Improving Tool Retrieval by Leveraging Large Language Models for Query Generation [https://arxiv.org/html/2412.03573v1]
- 
## Left to do