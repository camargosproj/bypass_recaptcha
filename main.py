from playwright.async_api import async_playwright
from recaptcha import solve
import asyncio


# Recaptcha tests websites
URL = "https://recaptcha-demo.appspot.com/recaptcha-v2-invisible.php"
URL2 = "https://www.google.com/recaptcha/api2/demo"



async def main():
    async with async_playwright() as playwright:
        browser = await playwright.chromium.launch(headless=False)
        page = await browser.new_page()
        await page.goto(URL)
        await page.click('[data-callback="onSubmit"]')
        await solve(page)
        await page.goto(URL2)
        await solve(page)
        await browser.close()

asyncio.run(main())
