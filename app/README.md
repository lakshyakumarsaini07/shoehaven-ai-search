# ShoeHaven - AI-Powered Footwear E-commerce Website

This is an AI-powered shoes e-commerce website featuring shoe products with natural language search capabilities using OpenAI embeddings. Users can search for shoes using natural language queries and interact with an AI assistant.

## Tech Stack

- **Frontend**: HTML, CSS, JavaScript (vanilla, no frameworks)
- **Backend**: FastAPI (Python)
- **AI Feature**: Natural Language Search using OpenAI embeddings (text-embedding-3-small model)

## Project Structure

app/
├── backend/
│ ├── main.py
│ ├── requirements.txt
│ └── .env
├── data/
│ └── products.json
└── frontend/
├── index.html
├── styles.css
└── script.js

## Setup Instructions

### Prerequisites

- Python 3.8 or higher
- OpenAI API key

### Backend Setup

1. Navigate to the backend directory:

   cd app/backend

2. Install the required dependencies:

   pip install -r requirements.txt

3. Set up your OpenAI API key:

   - Open the `.env` file
   - Replace the API key with your valid OpenAI API key
   - Note: If your API key is invalid or not provided, the application will fallback to a simpler keyword-based search instead of using AI embeddings

4. Start the FastAPI server:

   uvicorn main:app --reload --host 0.0.0.0 --port 8000

### Frontend Setup

Since the frontend is built using vanilla HTML, CSS, and JavaScript, you can serve it using any static file server. Here are a few options:

#### Using Python's built-in HTTP server

1. Navigate to the frontend directory:

   cd app/frontend

2. Start a simple HTTP server:

   # For Python 3

   python -m http.server 3000

3. Access the application in your browser at:

   http://localhost:3000

## Usage

1. The application will load with a list of all shoe products.
2. Use the AI search bar to enter natural language queries like:
   - "Show me running shoes under 2000 with good ratings"
   - "Casual shoes with high ratings"
   - "Affordable boots"
3. The system will use AI to understand your query and return the most relevant shoes.

## Features

- **Shoe Products**: A comprehensive catalog of footwear with detailed information and shoe emoji for each product
- **AI-Powered Search**: Users can search for shoes using natural language queries
- **AI Assistant Chat**: Interactive AI chatbot to help users find the perfect shoes
- **Enhanced UI/UX**: Modern, responsive design with intuitive navigation and visual appeal
- **Natural language search** using OpenAI embeddings
- **Semantic understanding** of user queries
- **Relevance-based product ranking**

## Technical Implementation

- The backend loads product data from a JSON file
- Each product's details (name, category, description) are embedded using OpenAI's text-embedding-3-small model
- When a user submits a query, the query is also embedded using the same model
- Cosine similarity is computed between the query embedding and all product embeddings
- Products are ranked by similarity score and the top results are returned
- A fallback keyword-based search is implemented for when the OpenAI API is unavailable or the key is invalid

## Bonus: AI and Blockchain Integration Idea

This AI search system could be enhanced with blockchain by:

- Using on-chain user preferences for personalization
- Offering token-gated pricing or exclusive product tiers
- Enabling loyalty through smart contracts linked to AI-driven engagement
