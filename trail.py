import asyncio
from playwright.async_api import async_playwright
import nest_asyncio

nest_asyncio.apply()

# 🔴 REQUIRED FUNCTION
async def start(user, wait_time, meetingcode, passcode):
    print(f"[JOINING] {user}")

    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=[
                "--disable-dev-shm-usage",
                "--no-sandbox",
                "--disable-blink-features=AutomationControlled",
                "--use-fake-device-for-media-stream",
                "--use-fake-ui-for-media-stream"
            ]
        )

        context = await browser.new_context(
            viewport={"width": 1280, "height": 720}
        )

        await context.grant_permissions(["microphone"])
        page = await context.new_page()

        try:
            await page.goto(
                f"https://app.zoom.us/wc/join/{meetingcode}",
                wait_until="domcontentloaded",
                timeout=45000
            )

            # Accept popups if any
            for btn in ["#onetrust-accept-btn-handler", "#wc_agree1"]:
                try:
                    await page.click(btn, timeout=2000)
                except:
                    pass

            # Fill name & passcode
            await page.wait_for_selector('input[type="text"]', timeout=25000)
            await page.fill('input[type="text"]', user)
            await page.fill('input[type="password"]', passcode)

            # Join button (FAST SPA CLICK)
            await page.evaluate("""
                () => {
                    const btn = document.querySelector('button.preview-join-button');
                    if (btn) btn.click();
                }
            """)

            print(f"[JOINED] {user}")

            # Join audio (optional)
            try:
                await page.wait_for_selector('button[class*="join-audio"]', timeout=15000)
                await page.click('button[class*="join-audio"]')
                print(f"[MIC OK] {user}")
            except:
                print(f"[MIC SKIPPED] {user}")

            print(f"[ACTIVE] {user}")
            await asyncio.sleep(wait_time)

        except Exception as e:
            print(f"[FAILED] {user} → {e}")

        await browser.close()
        print(f"[END] {user}")
