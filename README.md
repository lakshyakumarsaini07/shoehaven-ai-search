# ShoeHaven – Semantic AI Search for Footwear E-commerce

![GitHub repo size](https://img.shields.io/github/repo-size/lakshyakumarsaini07/RAG-Q-A-Chatbot)
![GitHub stars](https://img.shields.io/github/stars/lakshyakumarsaini07/RAG-Q-A-Chatbot?style=social)
![GitHub forks](https://img.shields.io/github/forks/lakshyakumarsaini07/RAG-Q-A-Chatbot?style=social)
![Issues](https://img.shields.io/github/issues/lakshyakumarsaini07/RAG-Q-A-Chatbot)
![License](https://img.shields.io/github/license/lakshyakumarsaini07/RAG-Q-A-Chatbot)

---

## Overview

ShoeHaven is an AI-powered product search system that replaces traditional filter-based e-commerce search with semantic understanding.

Instead of relying on exact keywords, the system interprets user intent using embeddings and returns the most relevant products.

This project demonstrates how retrieval-based AI can be applied to real-world product discovery systems.

---

## Demo

https://github.com/user-attachments/assets/388b7292-147f-4545-8fcc-5fb6aa4ce75c



---

## Key Features

- Semantic product search using natural language  
- Embedding-based similarity ranking  
- FastAPI backend with clean API design  
- Fallback keyword search for reliability  
- Lightweight and extensible architecture  

---

## Tech Stack

### Frontend
- HTML  
- CSS  
- Vanilla JavaScript  

### Backend
- FastAPI (Python)

### AI Layer
- OpenAI Embeddings (`text-embedding-3-small`)  
- Cosine similarity for ranking  

---

## System Architecture

```
                ┌──────────────────────┐
                │     User Query       │
                └─────────┬────────────┘
                          │
                          ▼
                ┌──────────────────────┐
                │   Frontend (JS UI)   │
                └─────────┬────────────┘
                          │ API Call
                          ▼
                ┌──────────────────────┐
                │  FastAPI Backend     │
                └─────────┬────────────┘
                          │
        ┌─────────────────┼─────────────────┐
        ▼                                   ▼
┌──────────────────┐              ┌──────────────────┐
│ Embed User Query │              │ Product Embedding│
│ (OpenAI API)     │              │ (Precomputed)    │
└──────────────────┘              └──────────────────┘
        │                                   │
        └──────────────┬────────────────────┘
                       ▼
            ┌──────────────────────┐
            │ Cosine Similarity    │
            │ + Ranking Engine     │
            └─────────┬────────────┘
                      ▼
            ┌──────────────────────┐
            │  Top-K Products      │
            └─────────┬────────────┘
                      ▼
            ┌──────────────────────┐
            │   Frontend Display   │
            └──────────────────────┘
```

---

## Data Flow

1. Product data is loaded from `products.json`  
2. Each product is converted into embeddings  
3. User query is embedded using the same model  
4. Cosine similarity is computed  
5. Results are ranked and returned  

Fallback:
- If API is unavailable → keyword-based search  

---

## Project Structure

```
app/
├── backend/
│   ├── main.py
│   ├── requirements.txt
│   └── .env
├── data/
│   └── products.json
└── frontend/
    ├── index.html
    ├── styles.css
    └── script.js
```

---

## Setup Instructions

### Prerequisites

- Python 3.8+  
- OpenAI API Key  

---

### Backend Setup

```bash
cd app/backend
pip install -r requirements.txt
```

Create `.env` file:

```
OPENAI_API_KEY=your_api_key_here
```

Run the backend:

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

---

### Frontend Setup

```bash
cd app/frontend
python -m http.server 3000
```

---

## License

This project is licensed under the MIT License.
