# tools/web_controller.py

import logging
import os
import asyncio
from playwright.async_api import async_playwright, Browser, Page, Playwright

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class WebController:
    """
    A production-grade controller using Playwright to reliably control the user's
    existing, installed Chrome browser with their user profile.
    """
    def __init__(self):
        self.p: Playwright = None
        self.browser: Page = None
        self.page: Page = None

    async def connect(self):
        user_data_dir = os.getenv("CHROME_USER_DATA_DIR")
        profile_name = os.getenv("CHROME_PROFILE", "Default")

        if not user_data_dir or not os.path.exists(user_data_dir):
            logger.error("❌ CHROME_USER_DATA_DIR not set or path is invalid. Cannot launch browser with profile.")
            return False
        
        try:
            self.p = await async_playwright().start()
            self.browser = await self.p.chromium.launch_persistent_context(
                user_data_dir=user_data_dir, headless=False, channel="chrome",
                args=[f'--profile-directory={profile_name}']
            )
            if self.browser.pages:
                self.page = self.browser.pages[0]
            else:
                self.page = await self.browser.new_page()
                
            logger.info(f"✅ WebController launched existing Chrome browser using profile '{profile_name}'.")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to launch browser with Playwright: {e}", exc_info=True)
            if self.p: await self.p.stop()
            return False

    async def browse(self, url: str):
        if not self.page: return logger.error("Page not available.")
        logger.info(f"Navigating to {url}")
        await self.page.goto(url, wait_until="domcontentloaded", timeout=60000)

    async def extract_full_dom_with_bounding_rects(self) -> list[dict] | None:
        if not self.page or self.page.is_closed(): return None
        try:
            js_script = """
            () => {
                const elements = document.querySelectorAll('a, button, input, textarea, [role="button"], [role="link"], [data-testid]');
                const results = [];
                for (const el of elements) {
                    const rect = el.getBoundingClientRect();
                    if (rect.width > 0 && rect.height > 0 && rect.top >= 0 && rect.left >= 0) {
                        results.push({
                            tagName: el.tagName.toLowerCase(),
                            text: el.innerText ? el.innerText.substring(0, 100) : '',
                            attributes: {
                                'id': el.id,
                                'class': el.className,
                                'role': el.getAttribute('role'),
                                'aria-label': el.getAttribute('aria-label'),
                                'data-testid': el.getAttribute('data-testid')
                            }
                        });
                    }
                }
                return results;
            }
            """
            return await self.page.evaluate(js_script)
        except Exception as e:
            logger.error(f"Failed to extract DOM tree: {e}")
            return None
    
    async def get_text_content(self, selector: str = "body") -> str:
        if not self.page or self.page.is_closed(): return ""
        try:
            element = self.page.locator(selector).first
            return await element.inner_text()
        except Exception as e:
            logger.error(f"Failed to get text content for selector '{selector}': {e}")
            return ""

    # MODIFIED: The click method now accepts a 'force' parameter
    async def click(self, selector: str, timeout: int = 15000, force: bool = False):
        """Clicks an element using a CSS selector, with an option to force the click."""
        if not self.page or self.page.is_closed(): return
        try:
            action = "Force-clicking" if force else "Attempting to click"
            logger.info(f"{action} element with selector: '{selector}'")
            # Use the force parameter here
            await self.page.locator(selector).first.click(timeout=timeout, force=force)
            logger.info(f"Successfully clicked '{selector}'")
        except Exception as e:
            logger.error(f"Failed to click element with selector '{selector}': {e}")
            raise

    async def click_by_text(self, text: str, timeout: int = 15000):
        if not self.page or self.page.is_closed(): return
        try:
            logger.info(f"Attempting to click element with text: '{text}'")
            await self.page.get_by_text(text, exact=False).first.click(timeout=timeout)
            logger.info(f"Successfully clicked element with text '{text}'")
        except Exception as e:
            logger.error(f"Failed to click element with text '{text}': {e}")
            raise

    async def type(self, selector: str, text: str, delay: int = 50):
        if not self.page or self.page.is_closed(): return
        try:
            logger.info(f"Attempting to type into element: '{selector}'")
            await self.page.locator(selector).first.type(text, delay=delay)
            logger.info(f"Successfully typed into '{selector}'")
        except Exception as e:
            logger.error(f"Failed to type into element '{selector}': {e}")
            raise

    # NEW: A method to verify success by waiting for a URL change.
    async def wait_for_url(self, url_pattern: str, timeout: int = 10000):
        """Waits for the page URL to match a specific pattern (glob format)."""
        if not self.page or self.page.is_closed(): return
        try:
            logger.info(f"Waiting for URL to match pattern: '{url_pattern}'")
            await self.page.wait_for_url(url_pattern, timeout=timeout)
            logger.info(f"URL successfully changed to match '{url_pattern}'. Current URL: {self.page.url}")
        except Exception as e:
            logger.error(f"Timed out waiting for URL to match '{url_pattern}'")
            raise

    async def close(self):
        if self.browser: await self.browser.close()
        if self.p: await self.p.stop()
        logger.info("Browser closed and Playwright instance stopped.")