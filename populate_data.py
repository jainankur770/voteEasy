import os
import sys

# Add the project root to sys.path to allow importing from backend
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from backend.services.scraper import scrape_and_save
from backend.services.rag_pipeline import build_index

def main():
    print("Step 1: Scraping voting data from official sources...")
    scrape_and_save()
    
    print("\nStep 2: Building FAISS vector index...")
    build_index()
    
    print("\nData population complete! You can now start the backend.")

if __name__ == "__main__":
    main()
