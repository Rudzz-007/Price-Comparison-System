# import asyncio
# from playwright.async_api import async_playwright

# async def run_final_scraper():
#     async with async_playwright() as p:
#         # Launch browser with headless=False so you can see the magic happen
#         browser = await p.chromium.launch(headless=False)
#         page = await browser.new_page()
        
#         print("Step 1: Opening Blinkit Home to set location framework...")
#         await page.goto("https://blinkit.com/")
#         await page.wait_for_timeout(3000)
        
#         print("Step 2: Hunting for the Location Selector input field...")
#         try:
#             # Look for the input box that asks for location/address
#             loc_input = page.locator("input[placeholder*='Select'], input[placeholder*='location']").first
#             await loc_input.click()
#             await loc_input.fill("Delhi")
#             await page.wait_for_timeout(2000)
            
#             # Press enter to lock in the location choice
#             await page.keyboard.press("Enter")
#             print("[SUCCESS] Location verified!")
#         except Exception as e:
#             print(f"[INFO] Location step bypassed: {e}")
            
#         await page.wait_for_timeout(3000)
        
#         print("Step 3: Navigating to the Maggi search result grid...")
#         await page.goto("https://blinkit.com/s/?q=maggi")
        
#         # Wait for the network calls to finish processing completely
#         await page.wait_for_load_state("networkidle")
#         await page.wait_for_timeout(3000)
        
#         print("Step 4: Parsing text cards from the webpage view...")
#         products = await page.evaluate('''() => {
#             const list = [];
#             // Target every single link card on the webpage
#             document.querySelectorAll('a').forEach(anchor => {
#                 const innerText = anchor.innerText || "";
#                 // If it contains a price tag, grab it
#                 if (innerText.includes('₹')) {
#                     list.push(innerText);
#                 }
#             });
#             return list;
#         }''')
        
#         print(f"\n[PARSING COMPLETE] Found {len(products)} live grocery rows!")
        
#         for index, item_text in enumerate(products[:5]):
#             lines = [l.strip() for l in item_text.split('\n') if l.strip()]
#             print(f"Item {index + 1}: {' | '.join(lines)}")
            
#         await browser.close()

# if __name__ == "__main__":
#     asyncio.run(run_final_scraper())