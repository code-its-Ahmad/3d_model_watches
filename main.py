# main.py
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from bs4 import BeautifulSoup
import logging
from typing import List, Dict
from urllib.parse import urljoin
import json
import re
import os

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(title="Watch Collection API", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific frontend URL, e.g., ["http://localhost:3000"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models
class Product(BaseModel):
    name: str
    image_url: str
    link: str
    slug: str | None = None

class ProductDetails(BaseModel):
    products: List[Product]

class WatchQuery(BaseModel):
    name: str

# Storage utility functions
def generate_slug(name: str) -> str:
    """Generate a URL-friendly slug from the product name."""
    if not name:
        return ''
    slug = re.sub(r'[^\w\s-]', '', name.lower()).strip()
    slug = re.sub(r'[\s-]+', '-', slug)
    return slug.strip('-')

def generate_safe_filename(name: str, category: str) -> str:
    """Generate a safe filename for saving product data."""
    safe_name = re.sub(r'[^\w\s-]', '', name).replace(' ', '_').lower()
    filename = f"data/{safe_name}_{category}.json"
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    return filename

def save_data(data: Product | ProductDetails, filename: str):
    """Save product or product collection data to a JSON file."""
    try:
        serialized_data = data.model_dump(exclude_none=True)
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(serialized_data, f, indent=4)
        logger.info(f"Data saved to {filename}")
    except Exception as e:
        logger.error(f"Error saving data to {filename}: {e}")
        raise

# Sample HTML content (simulating input; in production, fetch from URL)
html_content = '''
<body class="__className_d28b8a">
<div>
    <div>
        <div class="absolute inset-0 bg-white">
            <div class="absolute bottom-0 left-0 right-0 z-50 flex w-full flex-col items-center justify-center pb-6 pt-6">
                <div class="mb-3 px-3 text-center text-zinc-700">
                    <h1 class="text-xl font-semibold">Hublot Mp-10 Tourbillon</h1>
                </div>
                <div class="relative mb-4 w-full overflow-x-hidden py-3 min-h-[60px]">
                    <div class="flex space-x-4 min-h-[60px]">
                        <div class="inline-block"><div class="flex h-16 w-16 items-center justify-center rounded-full bg-white shadow-lg cursor-pointer overflow-hidden"><img src="https://dj5e08oeu5ym4.cloudfront.net/thumb/c2a36185-19be-48dc-80ca-a40cd1e930ce.jpg" alt="Hublot MP-10 Tourbillon" class="h-full w-full object-cover"></div></div>
                        <div class="inline-block"><div class="flex h-16 w-16 items-center justify-center rounded-full bg-white shadow-lg cursor-pointer overflow-hidden"><img src="https://dj5e08oeu5ym4.cloudfront.net/thumb/34b97066-cf29-4941-9d0c-581084f5981e.png" alt="Hublot Spirit Of Big Bang Full Magic Gold" class="h-full w-full object-cover"></div></div>
                        <div class="inline-block"><div class="flex h-16 w-16 items-center justify-center rounded-full bg-white shadow-lg cursor-pointer overflow-hidden"><img src="https://dj5e08oeu5ym4.cloudfront.net/thumb/165c3844-6301-4398-b8fd-7b15f0032e16.jpg" alt="Movado Alta Super Sub Sea Automatic" class="h-full w-full object-cover"></div></div>
                        <div class="inline-block"><div class="flex h-16 w-16 items-center justify-center rounded-full bg-white shadow-lg cursor-pointer overflow-hidden"><img src="https://dj5e08oeu5ym4.cloudfront.net/thumb/12df7df7-fecd-412e-bea5-02e92c312408.webp" alt="Swatch Obsidian Ink" class="h-full w-full object-cover"></div></div>
                        <div class="inline-block"><div class="flex h-16 w-16 items-center justify-center rounded-full bg-white shadow-lg cursor-pointer overflow-hidden"><img src="https://dj5e08oeu5ym4.cloudfront.net/thumb/eb5e18b9-400c-4c14-b752-86d2be88a482.avif" alt="Swatch Caramellissima" class="h-full w-full object-cover"></div></div>
                        <div class="inline-block"><div class="flex h-16 w-16 items-center justify-center rounded-full bg-white shadow-lg cursor-pointer overflow-hidden"><img src="https://dj5e08oeu5ym4.cloudfront.net/thumb/d670348a-0aee-4916-b011-a8943b1d7496.jpg" alt="Swatch Random Ghost" class="h-full w-full object-cover"></div></div>
                        <div class="inline-block"><div class="flex h-16 w-16 items-center justify-center rounded-full bg-white shadow-lg cursor-pointer overflow-hidden"><img src="https://dj5e08oeu5ym4.cloudfront.net/thumb/425b727b-c788-46b3-adb2-4cdfb9a39c2c.png" alt="Swatch Up In Smoke" class="h-full w-full object-cover"></div></div>
                        <div class="inline-block"><div class="flex h-16 w-16 items-center justify-center rounded-full bg-white shadow-lg cursor-pointer overflow-hidden"><img src="https://dj5e08oeu5ym4.cloudfront.net/thumb/cd3708cc-75fc-4f43-a8b3-011b061dba36.webp" alt="Swatch Cobalt Lagoon" class="h-full w-full object-cover"></div></div>
                    </div>
                </div>
            </div>
        </div>
    </div>
</div>
</body>
'''

# Provided watch links
watch_links = [
    'https://www.shopar.ai/collection/watches?product=66618cf59d3fb1edda45d3ba&mode=3d',
    'https://www.shopar.ai/collection/watches?product=65f48bb59ae86ec2a67a435d&mode=3d',
    'https://www.shopar.ai/collection/watches?product=657218fa3c333cddc7d2341c&mode=3d',
    'https://www.shopar.ai/collection/watches?product=66ba01a114de953c80003cfc&mode=3d',
    'https://www.shopar.ai/collection/watches?product=66ba06f314de953c8000719c&mode=3d',
    'https://www.shopar.ai/collection/watches?product=67129023c904b2a2777efe9d&mode=3d',
    'https://www.shopar.ai/collection/watches?product=6712989ac904b2a2777f39ed&mode=3d',
    'https://www.shopar.ai/collection/watches?product=66ba071914de953c8000722f&mode=3d'
]

# Function to extract watch data
def extract_watch_data(html: str, links: List[str]) -> List[Dict]:
    try:
        soup = BeautifulSoup(html, 'html.parser')
        watches = []
        watch_container = soup.find('div', class_='flex space-x-4 min-h-[60px]')
        if not watch_container:
            logger.error("Watch container not found in HTML")
            return []

        watch_items = watch_container.find_all('div', class_='inline-block')
        logger.info(f"Found {len(watch_items)} watch items in HTML")

        if len(watch_items) != len(links):
            logger.warning(f"Mismatch: {len(watch_items)} watch items found, but {len(links)} links provided")

        for i, item in enumerate(watch_items):
            img_tag = item.find('img')
            if img_tag and i < len(links):
                name = img_tag.get('alt', 'Unknown Watch').strip()
                img_url = img_tag.get('src', '').strip()
                if img_url and not img_url.startswith('http'):
                    img_url = urljoin('https://www.shopar.ai', img_url)
                if not img_url:
                    logger.warning(f"No valid image URL for watch: {name}")
                    continue
                link = links[i].strip()
                slug = generate_slug(name)
                watches.append({
                    'name': name,
                    'image_url': img_url,
                    'link': link,
                    'slug': slug
                })
            else:
                logger.warning(f"Skipping watch item {i}: No image or insufficient links")

        logger.info(f"Successfully extracted {len(watches)} watches")
        return watches
    except Exception as e:
        logger.error(f"Error extracting watch data: {str(e)}")
        return []

# API endpoints
@app.get("/watches", response_model=ProductDetails)
async def get_watch_collection():
    watches = extract_watch_data(html_content, watch_links)
    if not watches:
        raise HTTPException(status_code=500, detail="Failed to process watch collection")
    return ProductDetails(products=[Product(**watch) for watch in watches])

@app.post("/watches/by-name", response_model=Product)
async def get_watch_by_name(query: WatchQuery):
    watches = extract_watch_data(html_content, watch_links)
    if not watches:
        raise HTTPException(status_code=500, detail="Failed to process watch collection")
    
    watch_name = query.name.strip().lower()
    for watch in watches:
        if watch['name'].lower().strip() == watch_name:
            return Product(**watch)
    raise HTTPException(status_code=404, detail=f"Watch '{query.name}' not found")

@app.post("/watches/save", response_model=dict)
async def save_watch_collection():
    watches = extract_watch_data(html_content, watch_links)
    if not watches:
        raise HTTPException(status_code=500, detail="Failed to process watch collection")
    
    collection_filename = generate_safe_filename("watch_collection", "watches")
    save_data(ProductDetails(products=[Product(**watch) for watch in watches]), collection_filename)
    
    saved_files = []
    for watch in watches:
        filename = generate_safe_filename(watch['name'], "watch")
        save_data(Product(**watch), filename)
        saved_files.append(filename)
    
    return {"message": f"Watch collection saved to {collection_filename} and individual files: {', '.join(saved_files)}"}

# Run the app
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)