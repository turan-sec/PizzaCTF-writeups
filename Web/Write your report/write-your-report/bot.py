#!/usr/bin/env python3
"""
Automated XSS-triggering bot for ShaptoliSec:
Logs in as 'teamlead1', navigates to /reports, renders the page to execute any XSS payload.

Usage:
    python bot.py [base_url]

Dependencies:
    playwright

Later, you can add a cron job inside Docker to run this script every minute.
"""
import sys
import asyncio
from playwright.async_api import async_playwright

# Credentials for teamlead1
USERNAME = 'teamlead1'
PASSWORD = 'Il1k3freepizzzzzzaa#$%'

# Default base URL
BASE_URL = sys.argv[1] if len(sys.argv) > 1 else 'http://127.0.0.1:80'

async def run_bot():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        # 1) Navigate to login page
        await page.goto(f"{BASE_URL}/login", wait_until='networkidle')
        # Fill credentials and submit
        await page.fill('input[name="username"]', USERNAME)
        await page.fill('input[name="password"]', PASSWORD)
        await page.click('button[type="submit"]')
        # wait for navigation to complete
        await page.wait_for_load_state('networkidle')

        # 2) Navigate to reports page directly
        await page.goto(f"{BASE_URL}/reports", wait_until='networkidle')
        # allow any XSS to fire
        await asyncio.sleep(5)

        # 3) Save rendered HTML
        content = await page.content()
        with open('reports_dump.html', 'w', encoding='utf-8') as f:
            f.write(content)

        await browser.close()

if __name__ == '__main__':
    asyncio.run(run_bot())
