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
            # Dataset site exposes the CSV as a row button; clicking can expose preview and download.
            anchors=await page.locator('a').evaluate_all("els=>els.map(e=>({text:(e.innerText||'').slice(0,80),href:e.getAttribute('href')})).filter(z=>(z.text+' '+z.href).toLowerCase().includes('download')||z.href?.includes('file')).slice(0,30)")
            print('CANDIDATE LINKS',str(anchors)[:3500])
            async def download_click(target, tag):
                if await target.count()==0:return False
                print('CLICK TARGET',tag,'COUNT',await target.count())
                try:
                    async with page.expect_download(timeout=20000) as di:
                        await target.first.click(timeout=12000)
                    d=await di.value; fn=OUT / d.suggested_filename
                    await d.save_as(str(fn))
                    print('DOWNLOAD SUCCESS',tag,fn.name,fn.stat().st_size)
                    if zipfile.is_zipfile(fn):
                        with zipfile.ZipFile(fn) as z:
                            for name in z.namelist():
                                if name.lower().endswith('.csv') and 'screening' in name.lower():
                                    dest=OUT/'Screening_articles_and_decisions.csv'
                                    dest.write_bytes(z.read(name));print('EXTRACT CSV',name,dest.stat().st_size)
                                    return True
                    if fn.suffix.lower()=='.csv':
                        dest=OUT/'Screening_articles_and_decisions.csv'
                        if fn != dest:dest.write_bytes(fn.read_bytes())
                        return True
                except Exception as e:print('CLICK DOWNLOAD not immediate',tag,type(e).__name__,str(e)[:260])
                return False
            ok=await download_click(page.get_by_role('button',name=re.compile('Download All',re.I)),'download_all_button')
            if not ok:ok=await download_click(page.get_by_role('link',name=re.compile('Download All',re.I)),'download_all_link')
            if not ok:
                row=page.get_by_role('button',name=re.compile('Screening_articles and decisions.csv',re.I))
                ok=await download_click(row,'csv_file_row')
                print('AFTER ROW CLICK visible BODY tail',repr((await page.locator('body').inner_text())[-1300:]))
                print('AFTER ROW CLICK buttons',str((await page.locator('button').all_inner_texts())[-25:])[:2200])
                print('AFTER ROW CLICK links',str(await page.locator('a').evaluate_all("els=>els.map(e=>({text:(e.innerText||'').slice(0,60),href:e.getAttribute('href')})).filter(z=>(z.text+' '+z.href).toLowerCase().includes('download')).slice(0,15)"))[:2600])
            if not ok:
                for sel in [page.get_by_role('button',name=re.compile('^Download$',re.I)),page.get_by_role('link',name=re.compile('^Download$',re.I)),page.locator('a[download]')]:
                    ok=await download_click(sel,'post_preview_download')
                    if ok:break
            print('FINAL PUBLIC UI SOURCE BYTES', (OUT/'Screening_articles_and_decisions.csv').stat().st_size if (OUT/'Screening_articles_and_decisions.csv').exists() else 'HOLD')
        finally:
            await browser.close()

if __name__=='__main__':asyncio.run(main())
