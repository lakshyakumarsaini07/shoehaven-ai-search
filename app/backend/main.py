import json
import os
import numpy as np
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv
from openai import OpenAI
from sklearn.metrics.pairwise import cosine_similarity

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(title="E-commerce Product Search API")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global flag to check if OpenAI API is working
openai_api_working = False

# Initialize OpenAI client
api_key = os.getenv("OPENAI_API_KEY")
client = None

# Validate API key format (basic check)
if not api_key or len(api_key) < 20 or not api_key.startswith("sk-"):
    print("WARNING: OpenAI API key is missing, too short, or doesn't start with 'sk-'. AI search features will be disabled.")
    print(f"Current API key starts with: {api_key[:10]}..." if api_key else "No API key found")
    openai_api_working = False
else:
    try:
        client = OpenAI(api_key=api_key)
        print("OpenAI client initialized with API key")
    except Exception as e:
        print(f"Failed to initialize OpenAI client: {e}")
        openai_api_working = False

# Data models
class SearchQuery(BaseModel):
    query: str

class Product(BaseModel):
    id: int
    name: str
    price: float
    category: str
    description: str
    rating: float
    image: str

# Load products data from JSON file
def load_products():
    try:
        # Construct path to products.json
        json_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data', 'products.json')
        print(f"Loading products from: {json_path}")
        
        with open(json_path, 'r') as file:
            products = json.load(file)
            print(f"Successfully loaded {len(products)} products from JSON file")
            return products
    except Exception as e:
        print(f"Error loading products from JSON: {e}")
        
        # Return empty list as fallback - we won't use hardcoded products anymore
        print("Returning empty product list due to error")
        return []

# Function to get embeddings
def get_embedding(text) -> Optional[List[float]]:
    global openai_api_working
    
    if not openai_api_working or client is None:
        # Return None if we already know the API isn't working or client is not initialized
        return None
        
    try:
        # Step 4.1: Embed text using OpenAI's text-embedding-3-small model
        response = client.embeddings.create(
            model="text-embedding-3-small",
            input=text
        )
        openai_api_working = True
        print(f"Successfully generated embedding for text: '{text[:30]}...'")
        return response.data[0].embedding
    except Exception as e:
        print(f"Error getting embedding: {e}")
        openai_api_working = False
        return None

# Cache for product embeddings
product_embeddings = {}

# Function to generate product text for embedding
def generate_product_text(product):
    # Create a rich text representation of the product for better semantic matching
    return f"Name: {product['name']}. Category: {product['category']}. Description: {product['description']}. Price: ₹{product['price']}. Rating: {product['rating']} stars."

# Enhanced keyword-based search fallback when OpenAI API is not available
def keyword_search(query: str, products: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    query = query.lower()
    results = []
    
    # Extract potential keywords and constraints from the query
    query_words = query.split()
    price_constraints = []
    category_matches = []
    rating_constraints = []
    style_keywords = ["casual", "formal", "running", "athletic", "sports", "outdoor", "dress", "comfort"]
    found_style_keywords = []
    
    # Check for price constraints with better pattern matching
    # Handle "under X", "less than X", etc.
    if "under" in query:
        for i, word in enumerate(query_words):
            if word == "under" and i + 1 < len(query_words):
                try:
                    price_text = query_words[i+1].replace("₹", "").replace(",", "").replace("rs", "")
                    price = float(price_text)
                    price_constraints.append(("under", price))
                    print(f"Found price constraint: under {price}")
                except ValueError:
                    continue
    
    # Check for "over X", "more than X", etc.
    if any(phrase in query for phrase in ["over", "more than", "above"]):
        for i, word in enumerate(query_words):
            if word in ["over", "above"] and i + 1 < len(query_words):
                try:
                    price_text = query_words[i+1].replace("₹", "").replace(",", "").replace("rs", "")
                    price = float(price_text)
                    price_constraints.append(("over", price))
                    print(f"Found price constraint: over {price}")
                except ValueError:
                    continue
    
    # Check for specific shoe categories
    shoe_categories = ["running", "casual", "formal", "sports", "sneakers", "boots", "sandals", "athletics"]
    for category in shoe_categories:
        if category in query:
            category_matches.append(category)
            print(f"Found category: {category}")
    
    # Check for style keywords
    for keyword in style_keywords:
        if keyword in query:
            found_style_keywords.append(keyword)
    
    # Check for rating mentions
    rating_keywords = ["rating", "rated", "star", "stars", "review", "reviews", "quality"]
    quality_modifiers = ["high", "good", "best", "top", "excellent", "great"]
    
    for keyword in rating_keywords:
        if keyword in query:
            for modifier in quality_modifiers:
                if modifier in query:
                    rating_constraints.append(("over", 4.0))
                    print("Found high rating constraint")
                    break
    
    print(f"Price constraints: {price_constraints}")
    print(f"Category matches: {category_matches}")
    print(f"Style keywords: {found_style_keywords}")
    print(f"Rating constraints: {rating_constraints}")
    
    # First, filter products that meet hard constraints (price, rating)
    filtered_products = []
    
    for product in products:
        # Check if product meets all hard constraints
        meets_constraints = True
        
        # Check price constraints
        for constraint_type, price_value in price_constraints:
            if constraint_type == "under" and product['price'] > price_value:
                meets_constraints = False
                break
            elif constraint_type == "over" and product['price'] < price_value:
                meets_constraints = False
                break
        
        # Check rating constraints
        for constraint_type, rating_value in rating_constraints:
            if constraint_type == "over" and product['rating'] < rating_value:
                meets_constraints = False
                break
        
        if meets_constraints:
            filtered_products.append(product)
    
    print(f"Products meeting hard constraints: {len(filtered_products)}")
    
    # Now score the filtered products based on category/keyword matches
    for product in filtered_products:
        score = 0
        product_text = f"{product['name']} {product['category']} {product['description']}".lower()
        
        # Match query words against product text (basic search)
        for word in query_words:
            if len(word) > 3 and word in product_text:
                score += 1
        
        # Match categories with higher weight
        for category in category_matches:
            if category.lower() in product['category'].lower() or category.lower() in product['description'].lower():
                score += 5  # Higher weight for category matches
        
        # Match style keywords
        for keyword in found_style_keywords:
            if keyword in product_text:
                score += 3  # Higher weight for style matches
        
        # Add to results with score
        results.append((product, score))
    
    # Sort by score (highest first)
    results.sort(key=lambda x: x[1], reverse=True)
    
    # If we have category matches, only return products with category relevance
    if category_matches and results:
        # Filter for products that actually match the requested categories
        category_relevant_results = [item for item in results if item[1] >= 3]  # At least a category match
        if category_relevant_results:
            print(f"Keyword search found {len(category_relevant_results)} category-relevant results")
            return [item[0] for item in category_relevant_results]
    
    # Otherwise, return top scoring results or all if few results
    if results:
        # If we have hard constraints but no category matches, return all filtered results
        if price_constraints or rating_constraints:
            print(f"Keyword search found {len(results)} constraint-matching results")
            return [item[0] for item in results]
        # If no constraints, return top results with some relevance
        else:
            relevant_results = [item for item in results if item[1] >= 2]
            if relevant_results:
                print(f"Keyword search found {len(relevant_results)} relevant results")
                return [item[0] for item in relevant_results]
    
    print("No relevant results found")
    return []  # Return empty list if nothing matches well enough

@app.on_event("startup")
async def startup_event():
    global openai_api_working
    
    print("\n---- SMART NLP SEARCH SYSTEM INITIALIZATION ----")
    print("Step 0: Setup - Checking OpenAI API connection...")
    
    # Try to validate OpenAI API with a simple embedding request
    try:
        embedding = get_embedding("test")
        if embedding is not None:
            openai_api_working = True
            print("OpenAI API connection successful - Using text-embedding-3-small model")
        else:
            openai_api_working = False
            print(" WARNING: OpenAI API not working. Fallback to enhanced keyword search.")
    except Exception as e:
        openai_api_working = False
        print(f"WARNING: OpenAI API error: {e}. Fallback to enhanced keyword search.")
    
    print(f"OpenAI API working: {openai_api_working}")

    # Load products
    products = load_products()
    print(f"roduct catalog loaded: {len(products)} shoes")
    
    # Precompute embeddings for all products if API is working
    if openai_api_working:
        print("\nPre-computing product embeddings...")
        successful_embeddings = 0
        
        for product in products:
            product_text = generate_product_text(product)
            embedding = get_embedding(product_text)
            
            if embedding is not None:
                product_embeddings[product['id']] = embedding
                successful_embeddings += 1
        
        print(f"Successfully loaded embeddings for {successful_embeddings}/{len(products)} products")
        print("\nSystem ready for NLP search queries!")
        print("Example queries:")
        print("  - 'Show me running shoes under 2000 rupees'")
        print("  - 'I need comfortable casual shoes with good ratings'")
        print("  - 'Find me formal shoes for office wear'")
    else:
        print(" Skipping embeddings generation since OpenAI API is not available")
        print("\nSystem ready with keyword search fallback!")
        print("Example search terms:")
        print("  - 'running shoes under 2000'")
        print("  - 'casual sneakers'")
        print("  - 'formal shoes'")
    
    print("\n---- SYSTEM READY ----\n")

@app.get("/")
def read_root():
    return {"message": "E-commerce Product Search API"}

@app.get("/products", response_model=List[Dict[str, Any]])
def get_products():
    products = load_products()
    return products

@app.post("/search", response_model=List[Dict[str, Any]])
def search_products(search_query: SearchQuery):
    query = search_query.query
    
    if not query:
        return load_products()
    
    products = load_products()
    print(f"Searching for: '{query}'")
    
    # Step 4.1: Check if OpenAI API is working
    if not openai_api_working:
        # Fallback to keyword search
        print("OpenAI API not available - Using keyword search fallback")
        return keyword_search(query, products)
    
    # Step 4.1: Get query embedding
    print("Generating embedding for query...")
    query_embedding = get_embedding(query)
    
    # If embedding failed, fallback to keyword search
    if query_embedding is None:
        print("Query embedding failed, using keyword search fallback")
        return keyword_search(query, products)
    
    # Step 4.2: Generate product embeddings if not already cached
    print("Generating product embeddings...")
    for product in products:
        product_id = product['id']
        if product_id not in product_embeddings:
            product_text = generate_product_text(product)
            product_embedding = get_embedding(product_text)
            if product_embedding is not None:
                product_embeddings[product_id] = product_embedding
    
    # Step 5: Compute similarity with all products using cosine similarity
    print("Computing similarity scores...")
    results = []
    
    for product in products:
        product_id = product['id']
        if product_id in product_embeddings:
            # Calculate cosine similarity between query and product embeddings
            similarity = cosine_similarity(
                [query_embedding], 
                [product_embeddings[product_id]]
            )[0][0]
            results.append((product, similarity))
            print(f"Product {product['name']} similarity: {similarity:.4f}")
    
    # If no embeddings were found, fallback to keyword search
    if not results:
        print("No product embeddings available, using keyword search fallback")
        return keyword_search(query, products)
    
    # Step 6: Sort by similarity (highest first)
    results.sort(key=lambda x: x[1], reverse=True)
    
    # Step 7: Filter results by relevance - use a threshold to determine relevance
    # Only return products with similarity above threshold
    relevance_threshold = 0.15  # Adjust this threshold as needed
    relevant_results = [(product, score) for product, score in results if score > relevance_threshold]
    
    if relevant_results:
        # Return all relevant results (not just top 5)
        all_relevant_products = [item[0] for item in relevant_results]
        print(f"Returning {len(all_relevant_products)} relevant results")
        
        # Debug info
        if all_relevant_products:
            print(f"Top match: {all_relevant_products[0]['name']} with similarity score {relevant_results[0][1]:.4f}")
        
        return all_relevant_products
    else:
        # If nothing is relevant enough, return empty list
        print("No results met the relevance threshold")
        return []

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
