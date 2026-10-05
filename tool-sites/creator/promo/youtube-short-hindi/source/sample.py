import sys, asyncio; sys.path.insert(0, sys.argv[1] + '/actest'); from spki import ARGS
from playwright.async_api import async_playwright
TEXT = 'नमस्ते! मैं Creator Bench की AI आवाज़ हूँ। आपकी script, मेरी आवाज़, बिल्कुल free।'
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path='/opt/pw-browsers/chromium-1194/chrome-linux/chrome', args=ARGS)
        pg = await b.new_page(accept_downloads=True)
        await pg.goto('http://localhost:8790/ai-voiceover.html'); await pg.wait_for_timeout(1500)
        await pg.click('#av-voices button[data-v="hf_alpha"]'); await pg.fill('#av-text', TEXT); await pg.click('#av-go')
        await pg.wait_for_function("document.getElementById('av-status').textContent.startsWith('Done')", timeout=400000)
        await pg.select_option('#av-fmt', 'wav')
        async with pg.expect_download() as d: await pg.click('#av-dl')
        await (await d.value).save_as('sample.wav'); print(await pg.inner_text('#av-status')); await b.close()
asyncio.run(main())
