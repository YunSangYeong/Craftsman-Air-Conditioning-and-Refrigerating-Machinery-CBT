import { test, expect, type Page } from '@playwright/test';
async function boundsVisible(page:Page, selector:string) {
 const box=await page.locator(selector).boundingBox(); expect(box).not.toBeNull();
 expect(box!.y).toBeGreaterThanOrEqual(0);expect(box!.y+box!.height).toBeLessThanOrEqual(page.viewportSize()!.height);
}
for(const viewport of [{width:390,height:480},{width:740,height:360}]) {
 test(`작은 메뉴 ${viewport.width}×${viewport.height} 휠·터치·확대·도구 입력`, async({browser},testInfo)=>{
  test.skip(testInfo.project.name!=='mobile','mobile emulation in the mobile project');
  const context=await browser.newContext({viewport,isMobile:true,hasTouch:true,deviceScaleFactor:1,acceptDownloads:true});
  const page=await context.newPage();const cdp=await context.newCDPSession(page);
  await page.goto('http://127.0.0.1:4173/Craftsman-Air-Conditioning-and-Refrigerating-Machinery-CBT/');
  await page.evaluate(()=>document.documentElement.style.fontSize='125%');
  await page.getByRole('button',{name:'메뉴 열기'}).click();await page.waitForTimeout(400);
  const menu=page.locator('.sidebar');
  expect(await menu.evaluate(e=>e.scrollHeight>e.clientHeight)).toBe(true);
  const box=(await menu.boundingBox())!;const x=box.x+box.width*.65;
  await page.mouse.move(x,Math.min(viewport.height-30,box.height*.65));
  await page.mouse.wheel(0,1600);await page.waitForTimeout(250);
  expect(await menu.evaluate(e=>e.scrollTop)).toBeGreaterThan(0);
  await boundsVisible(page,'.sidebar-bottom');
  const download=page.waitForEvent('download');await page.getByRole('button',{name:'학습 기록 백업',exact:true}).click();expect((await download).suggestedFilename()).toContain('.json');
  await page.getByRole('button',{name:'데이터 초기화',exact:true}).click();await expect(page.getByRole('dialog')).toBeVisible();
  await page.getByRole('button',{name:'돌아가기',exact:true}).click();
  // Keep sidebar open; modal can cause view transitions but no programmatic scroll.
  if(!(await menu.evaluate(e=>e.classList.contains('open')))) await page.getByRole('button',{name:'메뉴 열기'}).click();
  await page.mouse.move(x,Math.min(viewport.height-30,box.height*.65));await page.mouse.wheel(0,-2000);await page.waitForTimeout(300);
  await boundsVisible(page,'.sidebar nav button:first-child');
  expect(await menu.evaluate(e=>e.scrollTop)).toBe(0);
  async function swipe(up:boolean) {
   const start=viewport.height*(up?.82:.25),end=viewport.height*(up?.25:.82);
   await cdp.send('Input.dispatchTouchEvent',{type:'touchStart',touchPoints:[{x,y:start}]});
   for(let i=1;i<=12;i++) { await cdp.send('Input.dispatchTouchEvent',{type:'touchMove',touchPoints:[{x,y:start+(end-start)*i/12}]});await page.waitForTimeout(20); }
   await cdp.send('Input.dispatchTouchEvent',{type:'touchEnd',touchPoints:[]});await page.waitForTimeout(180);
  }
  // Real browser touch input, separately from wheel. No scrollTop assignment.
  for(let i=0;i<4;i++) await swipe(true);
  expect(await menu.evaluate(e=>e.scrollTop)).toBeGreaterThan(0);
  await boundsVisible(page,'.sidebar-bottom');
  await page.screenshot({path:`test-results/menu-${viewport.width}-bottom.png`});
  const touchDownload=page.waitForEvent('download');await page.getByRole('button',{name:'학습 기록 백업',exact:true}).tap();await touchDownload;
  for(let i=0;i<5;i++) await swipe(false);
  await boundsVisible(page,'.sidebar nav button:first-child');expect(await menu.evaluate(e=>e.scrollTop)).toBe(0);
  await page.getByRole('navigation').getByRole('button',{name:'학습 대시보드',exact:true}).tap();
  await expect(menu).not.toHaveClass(/open/);await expect(page.getByRole('heading',{name:'공조냉동기계기사 필기 CBT',exact:true})).toBeVisible();
  expect(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth)).toBe(true);
  await context.close();
 });
}
test('상단 배너와 학습기준 메뉴 부재, 저장 실패 경고 유지',async({page})=>{
 await page.goto('');await expect(page.locator('.criteria-note')).toHaveCount(0);await expect(page.getByLabel('학습 기준')).toHaveCount(0);
 for(const label of ['모의시험 시작하기','문제풀이 시작하기']) {
  await page.getByRole('button',{name:label,exact:true}).click();await expect(page.locator('.criteria-note')).toHaveCount(0);
  if(await page.getByRole('button',{name:'메뉴 열기'}).isVisible()) await page.getByRole('button',{name:'메뉴 열기'}).click();
  await page.getByRole('navigation').getByRole('button',{name:'학습 대시보드',exact:true}).click();
 }
 await page.addInitScript(()=>{Storage.prototype.setItem=function(){throw new DOMException('quota','QuotaExceededError')};});
 await page.reload();await expect(page.getByRole('alert')).toBeVisible();
});
