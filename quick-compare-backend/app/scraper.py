import httpx
from bs4 import BeautifulSoup
from app.schemas import ProductResult

# A standard browser User-Agent header to prevent target web nodes from instantly blocking our request
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

async def scrape_live_platform(query: str, platform_name: str) -> list[ProductResult]:
    """
    Asynchronously requests a target commerce layout, parses its HTML architecture,
    and returns a structured list of clean ProductResult objects.
    """
    # For day 6 simulation/testing against a stable layout, we target a sandbox mock store
    # Swap this URL format out when targeting specific production quick-commerce endpoint routes
    url = f"https://mock-shop.com/search?q={query}&platform={platform_name.lower()}"
    
    results = []
    
    try:
        # Use an async HTTP client session so other backend requests don't pause while waiting for the network
        async with httpx.AsyncClient(headers=HEADERS, timeout=10.0) as client:
            response = await client.get(url)
            
            if response.status_code != 200:
                print(f"[SCRAPER WARNING] Platform {platform_name} responded with status code {response.status_code}")
                return results
                
            html_content = response.text
            
        # Parse the raw HTML text string into a searchable node tree object
        soup = BeautifulSoup(html_content, "html.parser")
        
        # Locate all individual product card wrapper containers matching the target store class layout
        product_cards = soup.find_all("div", class_="product-card")
        
        for card in product_cards:
            # Safely look up text strings within specified HTML structural tags
            title_tag = card.find("h3", class_="product-title")
            price_tag = card.find("span", class_="product-price")
            qty_tag = card.find("span", class_="product-qty")
            img_tag = card.find("img", class_="product-image")
            
            if title_tag and price_tag:
                # Clean strings by stripping whitespace and sanitizing price characters
                title = title_tag.text.strip()
                raw_price = price_tag.text.replace("₹", "").replace(",", "").strip()
                quantity = qty_tag.text.strip() if qty_tag else "1 unit"
                image_url = img_tag["src"] if img_tag else None
                
                results.append(
                    ProductResult(
                        title=title,
                        platform=platform_name,
                        price=float(raw_price),
                        quantity=quantity,
                        image_url=image_url,
                        product_url=url
                    )
                )
    except Exception as e:
        print(f"[SCRAPER ERROR] Exception thrown during execution loop for {platform_name}: {str(e)}")
        
    return results