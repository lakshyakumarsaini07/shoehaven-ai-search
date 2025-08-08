// API endpoint URLs
const API_BASE_URL = "http://localhost:8001";
const PRODUCTS_ENDPOINT = `${API_BASE_URL}/products`;
const SEARCH_ENDPOINT = `${API_BASE_URL}/search`;

// DOM elements
const productsGrid = document.getElementById("products-grid");
const searchInput = document.getElementById("search-input");
const searchButton = document.getElementById("search-button");
const loadingElement = document.getElementById("loading");
const statusMessage = document.getElementById("status-message");

// Function to generate star rating HTML
function generateStarRating(rating) {
  const fullStars = Math.floor(rating);
  const hasHalfStar = rating % 1 >= 0.5;
  let stars = "";

  for (let i = 0; i < fullStars; i++) {
    stars += "★";
  }

  if (hasHalfStar) {
    stars += "★";
  }

  return stars;
}

// Function to display products
function displayProducts(products) {
  productsGrid.innerHTML = "";

  if (!products || products.length === 0) {
    productsGrid.innerHTML =
      '<div class="no-results"><p>No products match your search criteria.</p><p>Please try different search terms or <button class="reset-search" onclick="fetchProducts()">view all products</button></p></div>';
    return;
  }

  // Show product count with appropriate message
  const countHeader = document.createElement("div");
  countHeader.className = "product-count";

  // Different message if we're showing all products or search results
  const isSearchResult = searchInput.value.trim() !== "";
  if (isSearchResult) {
    countHeader.innerHTML = `<h2>Found ${products.length} matching shoes</h2>`;
  } else {
    countHeader.innerHTML = `<h2>Showing all ${products.length} shoes</h2>`;
  }
  productsGrid.appendChild(countHeader);

  products.forEach((product) => {
    const productCard = document.createElement("div");
    productCard.className = "product-card";

    // Remove emojis from product name
    const cleanName = product.name
      .replace(/[\u{1F600}-\u{1F6FF}]|[\u{2600}-\u{26FF}]/gu, "")
      .trim();

    productCard.innerHTML = `
            <img src="image.png" alt="${cleanName}" class="product-image">
            <div class="product-info">
                <h2 class="product-name">${cleanName}</h2>
                <span class="product-category">${product.category}</span>
                <p class="product-price">₹${product.price.toFixed(2)}</p>
                <p class="product-description">${product.description}</p>
                <div class="product-rating">
                    <span class="stars">${generateStarRating(
                      product.rating
                    )}</span>
                    <span>${product.rating.toFixed(1)}</span>
                </div>
                <button class="add-to-cart-btn">Add to Cart</button>
            </div>
        `;

    productsGrid.appendChild(productCard);
  });
}

// Function to show status message
function showStatusMessage(message, type = "error") {
  statusMessage.textContent = message;
  statusMessage.className = `status-message ${type}`;

  setTimeout(() => {
    statusMessage.className = "status-message";
  }, 5000);
}

// Function to fetch all products
async function fetchProducts() {
  try {
    loadingElement.style.display = "block";

    try {
      const response = await fetch(PRODUCTS_ENDPOINT);

      if (!response.ok) {
        throw new Error(`HTTP error! Status: ${response.status}`);
      }

      const products = await response.json();
      if (products && products.length > 0) {
        displayProducts(products);
        return;
      } else {
        throw new Error("No products returned from API");
      }
    } catch (apiError) {
      console.error("API error, using fallback products:", apiError);
      // Fallback to static products if API fails
      const fallbackProducts = [
        {
          id: 1,
          name: "Nike Air Max 90",
          price: 1899,
          category: "Running Shoes",
          description:
            "Iconic Air Max cushioning with a waffle outsole and premium materials for comfort and style.",
          rating: 4.5,
          image: "image.png",
        },
        {
          id: 2,
          name: "Adidas Ultra Boost",
          price: 2199,
          category: "Running Shoes",
          description:
            "Premium running shoes with responsive boost technology that returns energy with every step you take.",
          rating: 4.7,
          image: "image.png",
        },
        {
          id: 3,
          name: "Puma Suede Classic",
          price: 1599,
          category: "Casual Sneakers",
          description:
            "Iconic casual sneakers with a suede upper and classic design that never goes out of style.",
          rating: 4.2,
          image: "image.png",
        },
        {
          id: 4,
          name: "Cole Haan Oxford Dress Shoes",
          price: 3499,
          category: "Formal Shoes",
          description:
            "Premium leather dress shoes with elegant design, perfect for formal occasions.",
          rating: 4.8,
          image: "image.png",
        },
        {
          id: 5,
          name: "New Balance 574",
          price: 1799,
          category: "Casual Sneakers",
          description:
            "Classic athletic shoes with superior comfort and retro styling.",
          rating: 4.3,
          image: "image.png",
        },
      ];
      displayProducts(fallbackProducts);
    }
  } catch (error) {
    console.error("Error in fetchProducts:", error);
    showStatusMessage("Failed to load products. Using sample data instead.");
  } finally {
    loadingElement.style.display = "none";
  }
}

// Function to search products
async function searchProducts(query) {
  try {
    loadingElement.style.display = "block";

    const response = await fetch(SEARCH_ENDPOINT, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ query }),
    });

    if (!response.ok) {
      throw new Error(`HTTP error! Status: ${response.status}`);
    }

    const products = await response.json();
    displayProducts(products);

    // Show appropriate message
    if (products.length > 0) {
      showStatusMessage(
        `Found ${products.length} shoes matching "${query}".`,
        "success"
      );
    } else {
      showStatusMessage(
        `No shoes found matching "${query}". Try different search terms.`,
        "error"
      );
    }
  } catch (error) {
    console.error("Error searching products:", error);
    showStatusMessage("Search failed. Please try again later.");
  } finally {
    loadingElement.style.display = "none";
  }
}

// Event listener for search button click
searchButton.addEventListener("click", () => {
  const query = searchInput.value.trim();
  if (query) {
    searchProducts(query);
  } else {
    fetchProducts();
  }
});

// Event listener for pressing Enter in search input
searchInput.addEventListener("keypress", (event) => {
  if (event.key === "Enter") {
    const query = searchInput.value.trim();
    if (query) {
      searchProducts(query);
    } else {
      fetchProducts();
    }
  }
});

// Function to use a search example
function useSearchExample(element) {
  const exampleText = element.textContent;
  searchInput.value = exampleText;
  searchProducts(exampleText);
}

// Add the function to the global scope
window.useSearchExample = useSearchExample;

// Initialize the app by loading all products
document.addEventListener("DOMContentLoaded", () => {
  fetchProducts();

  // Show a welcome message explaining the smart search
  setTimeout(() => {
    showStatusMessage(
      "Try our Smart NLP Search! Type naturally like 'Show me running shoes under 2000'",
      "success"
    );
  }, 1500);
});
