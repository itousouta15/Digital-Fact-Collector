# python quote_collector.py

import requests
import json
from datetime import datetime, timezone
import os

# --- Configuration (Updated for Quotes API) ---
QUOTES_FILE = "quotes.json"
API_URL = "https://zenquotes.io/api/random"

def fetch_random_quote():
    """Connects to the Zen Quotes API and fetches a random quote and author."""
    try:
        response = requests.get(API_URL)
        response.raise_for_status()
        # This API returns a list with one quote object inside, e.g., [{"q": "...", "a": "..."}]
        data = response.json()
        
        if data and isinstance(data, list) and len(data) > 0:
            quote_data = data[0]
            quote = quote_data.get('q')
            author = quote_data.get('a', 'Unknown Author') # Provide a default value
            return quote, author
        else:
            print("⚠️ API returned unexpected data format.")
            return None, None
            
    except requests.exceptions.RequestException as e:
        print(f"⚠️ Error connecting to API: {e}")
        return None, None
    except json.JSONDecodeError:
        print("⚠️ Error decoding API response.")
        return None, None

def load_collection(filename):
    """Loads a collection from a JSON file."""
    if not os.path.exists(filename):
        return []
    
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        return []

def save_collection(filename, collection):
    """Saves a collection to a JSON file."""
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(collection, f, indent=4, ensure_ascii=False)

# --- Main execution block ---
if __name__ == "__main__":
    print("🚀 Running the Inspirational Quote Collector...")

    # 1. Load existing quotes
    print(f"Loading existing quotes from {QUOTES_FILE}...")
    quote_collection = load_collection(QUOTES_FILE)
    print(f"Found {len(quote_collection)} quotes in the collection.")
    
    # Create a set of existing quote texts for fast duplicate checks
    existing_quote_texts = {item['quote'] for item in quote_collection}

    # 2. Fetch a new quote
    print("Fetching a new quote from the API...")
    new_quote_text, new_quote_author = fetch_random_quote()

    if new_quote_text:
        # 3. Check for duplicates
        if new_quote_text in existing_quote_texts:
            print(f"\n🟡 Duplicate quote found. No action taken.")
            print(f"   \"{new_quote_text}\" - {new_quote_author}")
        else:
            # 4. Add the new, unique quote to our collection
            print("\n✅ New unique quote found! Adding to collection.")
            
            new_quote_entry = {
                "quote": new_quote_text,
                "author": new_quote_author,
                "added_at": datetime.now(timezone.utc).isoformat()
            }
            quote_collection.append(new_quote_entry)
            
            # 5. Save the updated collection
            save_collection(QUOTES_FILE, quote_collection)
            print(f"   \"{new_quote_text}\" - {new_quote_author}")
            print(f"   Collection saved. Total quotes: {len(quote_collection)}")
    else:
        print("\n❌ Could not fetch a new quote. Please check your connection or the API status.")
