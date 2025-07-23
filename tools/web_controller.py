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
        """
        Launches the user's installed Chrome browser, configured to
        use a dedicated, non-default user data directory for automation.
        """
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
            self.page = self.browser.pages[0]
            logger.info(f"✅ WebController launched existing Chrome browser using profile '{profile_name}'.")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to launch browser with Playwright: {e}", exc_info=True)
            if self.p: await self.p.stop()
            return False

    async def browse(self, url: str):
        if not self.page: return logger.error("Page not available.")
        logger.info(f"Navigating to {url}")
        await self.page.goto(url, wait_until="networkidle", timeout=60000)

    async def extract_full_dom_with_bounding_rects(self) -> list[dict] | None:
        if not self.page or self.page.is_closed(): return None
        try:
            js_script = """
            () => {
                const elements = document.querySelectorAll('*');
                const results = [];
                for (const el of elements) {
                    const rect = el.getBoundingClientRect();
                    if (rect.width > 0 && rect.height > 0 && rect.top >= 0 && rect.left >= 0) {
                        results.push({
                            tagName: el.tagName.toLowerCase(), id: el.id || '', className: el.className || '',
                            innerText: el.innerText ? el.innerText.substring(0, 200) : '',
                            attributes: {'data-testid': el.getAttribute('data-testid'), 'aria-label': el.getAttribute('aria-label'), 'role': el.getAttribute('role'), 'name': el.getAttribute('name'), 'placeholder': el.getAttribute('placeholder')},
                            rect: el.getBoundingClientRect().toJSON()
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

    # --- ✅ FIX: Added the missing find_element_js function ---
    async def find_element_js(self, selector: str) -> dict | None:
        """Uses JavaScript to get the pixel-perfect coordinates of a single element."""
        if not self.page or self.page.is_closed(): return None
        try:
            await self.page.wait_for_selector(selector, state='visible', timeout=10000)
            element = self.page.locator(selector).first
            rect = await element.evaluate("el => el.getBoundingClientRect().toJSON()")
            if rect:
                logger.info(f"Found element '{selector}' at {rect}")
                return rect
            return None
        except Exception as e:
            logger.error(f"Failed to find element with selector '{selector}': {e}")
            return None

    async def type_text_in_element(self, selector: str, text: str, delay: int = 50):
        if not self.page or self.page.is_closed(): return
        try:
            await self.page.type(selector, text, delay=delay)
            logger.info(f"Typed text into element '{selector}'")
        except Exception as e:
            logger.error(f"Failed to type into element '{selector}': {e}")

    async def close(self):
        if self.browser: await self.browser.close()
        if self.p: await self.p.stop()
        logger.info("Browser closed and Playwright instance stopped.")
