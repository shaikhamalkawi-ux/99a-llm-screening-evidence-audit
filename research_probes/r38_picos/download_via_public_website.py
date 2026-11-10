#!/usr/bin/env python3
"""Attempt ordinary public user-interface Download All, without login bypass.

Public dataset 10.17632/4bgt2p5hrd.1 (CC BY-NC 4.0).
Raw dataset is kept locally for analysis and never placed in public artifact.
"""
import asyncio, pathlib, zipfile, json, re
from playwright.async_api import async_playwright

URL='https://data.mendeley.com/datasets/4bgt2p5hrd/1'
OUT=pathlib.Path('r38_private');OUT.mkdir(exist_ok=True)

async def main():
    async with async_playwright() as p:
        browser=await p.chromium.launch(headless=True,args=['--no-sandbox'])
        ctx=await browser.new_context(accept_downloads=True,user_agent='Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/131.0.0.0 Safari/537.36')
        page=await ctx.new_page()
        failed=[]
        page.on('requestfailed',lambda req: failed.append(req.url.split('?')[0]))
        try:
            res=await page.goto(URL,wait_until='domcontentloaded',timeout=45000)
            await page.wait_for_timeout(7000)
            print('PAGE',res.status if res else None,'TITLE',await page.title())
            print('BUTTONS',str((await page.locator('button').all_inner_texts())[:50])[:2500])
            print('TEXT PREVIEW',repr((await page.locator('body').inner_text())[:1400]))
            print('FAILED REQUESTS',failed[:8])
            b=page.get_by_role('button',name=re.compile('Download All',re.I))
            if await b.count()==0:b=page.get_by_text('Download All',exact=True)
            print('DOWNLOAD BUTTONS',await b.count())
            if await b.count():
                try:
                    async with page.expect_download(timeout=45000) as di:
                        await b.first.click(timeout=15000)
                    d=await di.value
                    fn=OUT / d.suggested_filename
                    await d.save_as(str(fn))
                    print('UI DOWNLOAD SUCCESS',fn.name,fn.stat().st_size)
                    if zipfile.is_zipfile(fn):
                        with zipfile.ZipFile(fn) as z:
                            for name in z.namelist():
                                if name.lower().endswith('.csv') and 'screening' in name.lower():
                                    dest=OUT/'Screening_articles_and_decisions.csv'
                                    dest.write_bytes(z.read(name))
                                    print('EXTRACT CSV',name,dest.stat().st_size)
                                    break
                    elif fn.suffix.lower()=='.csv':
                        dest=OUT/'Screening_articles_and_decisions.csv'
                        if dest != fn:dest.write_bytes(fn.read_bytes())
                except Exception as e:print('PUBLIC UI DOWNLOAD HOLD',type(e).__name__,str(e)[:450])
            else:
                print('NO PUBLIC BUTTON: H O L D; do not bypass login')
        finally:
            await browser.close()

if __name__=='__main__':asyncio.run(main())
