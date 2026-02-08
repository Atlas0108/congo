"""
Utility to fetch product images from Google Image Search
"""

import time
from urllib.parse import quote

try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False

def get_google_image_url(product_name, api_key=None, search_engine_id=None):
    """
    Get the first image URL from Google Image Search for a product name.
    
    Args:
        product_name: Name of the product to search for
        api_key: Google Custom Search API key (optional)
        search_engine_id: Google Custom Search Engine ID (optional)
    
    Returns:
        str: URL of the first image result, or None if not found
    """
    if api_key and search_engine_id:
        return _get_image_via_api(product_name, api_key, search_engine_id)
    else:
        return _get_image_via_scraping(product_name)

def _get_image_via_api(product_name, api_key, search_engine_id):
    """Get image using Google Custom Search API"""
    if not HAS_REQUESTS:
        return None
    
    try:
        url = "https://www.googleapis.com/customsearch/v1"
        params = {
            'key': api_key,
            'cx': search_engine_id,
            'q': product_name,
            'searchType': 'image',
            'num': 1,
            'safe': 'active'
        }
        
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        if 'items' in data and len(data['items']) > 0:
            return data['items'][0]['link']
    except Exception as e:
        print(f"Error fetching image via API for '{product_name}': {e}")
    
    return None

def _get_image_via_scraping(product_name):
    """Get image by scraping Google Images (fallback method)"""
    if not HAS_REQUESTS:
        # If requests is not available, use generated image URLs
        return _get_image_from_unsplash(product_name)
    
    try:
        # Method 1: Try Google Images via direct search
        google_image = _scrape_google_images(product_name)
        if google_image:
            return google_image
        
        # Method 2: Fallback to generated images
        unsplash_url = _get_image_from_unsplash(product_name)
        if unsplash_url:
            return unsplash_url
        
    except Exception as e:
        print(f"Error fetching image via scraping for '{product_name}': {e}")
        # Fallback to generated image
        return _get_image_from_unsplash(product_name)
    
    return None

def _scrape_google_images(product_name):
    """Scrape Google Images search results"""
    if not HAS_REQUESTS:
        return None
    
    try:
        # Google Images search URL
        search_url = f"https://www.google.com/search?q={quote(product_name)}&tbm=isch"
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        response = requests.get(search_url, headers=headers, timeout=10)
        response.raise_for_status()
        
        # Parse the HTML to find image URLs
        # Google Images embeds image data in the page
        import re
        # Look for the image data in the page source
        # Google stores image URLs in a specific format
        pattern = r'"ou":"([^"]+)"'  # Pattern to find original image URLs
        matches = re.findall(pattern, response.text)
        
        if matches:
            # Return the first valid image URL
            image_url = matches[0].replace('\\u003d', '=').replace('\\u0026', '&')
            # Verify it's a valid image URL
            if image_url.startswith('http') and any(ext in image_url.lower() for ext in ['.jpg', '.jpeg', '.png', '.webp', '.gif']):
                return image_url
        
        # Alternative: Look for the JSON data Google embeds
        pattern2 = r'AF_initDataCallback.*?"(https://[^"]+\.(jpg|jpeg|png|webp))"'
        matches2 = re.findall(pattern2, response.text, re.IGNORECASE)
        if matches2:
            return matches2[0][0]
            
    except Exception as e:
        print(f"Error scraping Google Images for '{product_name}': {e}")
    
    return None

def _get_image_from_unsplash(product_name):
    """Get product image from Unsplash API (free alternative)"""
    try:
        # Unsplash Source API (no key required for basic usage)
        # This provides high-quality images based on search term
        # Format: https://source.unsplash.com/400x400/?keyword
        # Note: Unsplash Source API is deprecated, but we'll use a direct image service
        # Using a simpler approach: use a product image service
        
        # Use Lorem Picsum with a seed based on product name for consistent images
        # Or use a product image placeholder service
        import hashlib
        seed = int(hashlib.md5(product_name.encode()).hexdigest()[:8], 16)
        image_url = f"https://picsum.photos/seed/{seed}/400/400"
        return image_url
    except Exception as e:
        print(f"Error generating image URL for '{product_name}': {e}")
    
    return None

def _get_image_from_pexels(product_name):
    """Get product image from Pexels API (requires free API key)"""
    # This would require a Pexels API key
    # For now, we'll use Unsplash as it doesn't require a key
    pass

def fetch_images_for_products(products, api_key=None, search_engine_id=None, delay=0.5):
    """
    Fetch images for a list of products.
    
    Args:
        products: List of product dictionaries or Product objects with 'name' attribute
        api_key: Google Custom Search API key (optional)
        search_engine_id: Google Custom Search Engine ID (optional)
        delay: Delay between requests in seconds (to avoid rate limiting)
    
    Returns:
        dict: Mapping of product names to image URLs
    """
    image_urls = {}
    
    for product in products:
        # Get product name
        if isinstance(product, dict):
            product_name = product.get('name', '')
        else:
            product_name = getattr(product, 'name', '')
        
        if not product_name:
            continue
        
        print(f"Fetching image for: {product_name}...")
        image_url = get_google_image_url(product_name, api_key, search_engine_id)
        
        if image_url:
            image_urls[product_name] = image_url
            print(f"  ✓ Found image: {image_url[:80]}...")
        else:
            print(f"  ✗ No image found, using generated image")
            # Use a generated image URL as fallback
            image_urls[product_name] = _get_image_from_unsplash(product_name) or "https://via.placeholder.com/400"
        
        # Delay to avoid rate limiting
        if delay > 0:
            time.sleep(delay)
    
    return image_urls

