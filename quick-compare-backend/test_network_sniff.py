import asyncio  #Python's core asynchronous control library to manage time sleeps and event loop executions
from playwright.async_api import async_playwright  #non-blocking asynchronous version of the Playwright browser engine manager

async def intercept_response(response): #Declares a custom background event handler function that will automatically trigger every single time the browser receives any data packet back from the internet
    if "search" in response.url or "layout" in response.url or "v1" in response.url:
        if response.status == 200:
            print(f"\n[FOUND ENDPOINT]: {response.url}")
            try:
                data = await response.json()
                print("[SUCCESS] Packet contains readable structured JSON data!")
                print(str(data)[:300] + "...")
            except Exception:
                print("[INFO] Packet payload format is not raw JSON.")

async def run_sniffer():
    async with async_playwright() as p:  #Initializes the non-blocking automated browser management runtime block
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()
        
        page.on("response", intercept_response)
        
        print("Opening Blinkit...")
        await page.goto("https://blinkit.com/")
        
        print("Waiting 15 seconds for you to select location and type a search query...")
        await asyncio.sleep(15) #Pauses the script code execution for 15 seconds, giving you plenty of time to type your location and search for an item while the script sniffs the active packets in the background
        
        await browser.close()

if __name__ == "__main__":
    asyncio.run(run_sniffer()) #Launches the central asynchronous loop pipeline wrapper when the script file is run directly