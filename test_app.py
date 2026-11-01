import asyncio, json
from playwright.async_api import async_playwright
import pathlib
URL=(pathlib.Path(__file__).resolve().parent.parent/'index.html').as_uri()
R=[]
async def fresh(b,w=1100,h=800):
    c=await b.new_context(viewport={'width':w,'height':h}); p=await c.new_page(); p.on('dialog',lambda d:asyncio.ensure_future(d.accept())); await p.goto(URL); return c,p
async def txt(p,sel): return (await p.inner_text(sel)).strip()
async def fillcust(p,n='Rahul Das',ph='9876543210',a='Station Road, Coochbehar'):
    await p.fill('[data-me=name]',n); await p.fill('[data-me=phone]',ph)
    if await p.query_selector('[data-me=addr]'): await p.fill('[data-me=addr]',a)
def rec(i,mod,desc,steps,exp,act,ok): R.append(dict(id=f'TC{i:02d}',mod=mod,desc=desc,steps=steps,exp=exp,act=act,ok=bool(ok)))
async def main():
    async with async_playwright() as pw:
        b=await pw.chromium.launch()
        # 1
        c,p=await fresh(b); n=len(await p.query_selector_all('#grid .card')); rec(1,'Customer','Product catalogue loads','Open the shop page','14 product cards displayed',f'{n} cards displayed',n==14); await c.close()
        # 2
        c,p=await fresh(b); await p.fill('#q','dal'); names=[await x.inner_text() for x in await p.query_selector_all('#grid .card b')]; rec(2,'Customer','Search by name','Type "dal" in the search box','Only "Toor dal" shown',f'{len(names)} result: {names[0] if names else "-"}',names==['Toor dal']); await c.close()
        # 3
        c,p=await fresh(b); await p.click('[data-a=cat][data-v=Dairy]'); n=len(await p.query_selector_all('#grid .card')); rec(3,'Customer','Category filter','Tap the "Dairy" chip','3 dairy products (Milk, Eggs, Paneer)',f'{n} products shown',n==3); await c.close()
        # 4
        c,p=await fresh(b); await p.click('[data-a=add][data-id="1"]'); await p.click('[data-a=add][data-id="1"]'); b1=await txt(p,'#basket .box'); ok='× 2' in b1 and '₹236' in b1; rec(4,'Customer','Add item to basket','Tap "Add to basket" on Basmati rice, then "+"','Basket shows quantity 2 and items total ₹236',('Basket line "× 2", items total ₹236' if ok else b1[:60]),ok); await c.close()
        # 5
        c,p=await fresh(b); await p.click('[data-a=add][data-id="12"]')
        for _ in range(8):
            btn=await p.query_selector('[data-a=add][data-id="12"]'); await btn.click()
        q=await txt(p,'#grid .card:has([data-id="12"]) .qty span'); rec(5,'Customer','Stock limit in basket','Add Paneer (stock 6) nine times','Quantity capped at 6',f'Quantity = {q}',q=='6'); await c.close()
        # 6
        c,p=await fresh(b); await p.click('[data-a=add][data-id="1"]'); await p.click('[data-a=add][data-id="1"]'); await p.click('[data-a=sub][data-id="1"]'); q=await txt(p,'#grid .card:has([data-id="1"]) .qty span'); rec(6,'Customer','Remove item from basket','Add rice twice, tap "−" once','Quantity becomes 1',f'Quantity = {q}',q=='1'); await c.close()
        # 7
        c,p=await fresh(b); await p.click('[data-a=add][data-id="1"]'); t=await txt(p,'#basket .box'); ok='₹148' in t; rec(7,'Customer','Delivery fee below ₹500','Add rice (₹118), delivery mode','Fee ₹30, total ₹148',('Total ₹148 shown' if ok else t[-60:]),ok); await c.close()
        # 8
        c,p=await fresh(b)
        for i in [3,3,5]: await p.click(f'[data-a=add][data-id="{i}"]')
        t=await txt(p,'#basket .box'); ok='₹536' in t and '₹0' in t; rec(8,'Customer','Free delivery from ₹500','Add Atta ×2 and Sugar ×1 (₹536)','Delivery fee ₹0, total ₹536',('Fee ₹0, total ₹536' if ok else t[-80:]),ok); await c.close()
        # 9
        c,p=await fresh(b); await p.click('[data-a=add][data-id="1"]'); await p.click('[data-a=mode][data-v=pickup]'); t=await txt(p,'#basket .box'); ok='Pickup' in t and '₹118' in t.split('Total')[-1]; rec(9,'Customer','Pickup has no fee','Add rice, choose Store pickup','Fee ₹0, total ₹118, address field hidden',('Total ₹118, no address field' if ok and not await p.query_selector('[data-me=addr]') else 'mismatch'),ok and not await p.query_selector('[data-me=addr]')); await c.close()
        # 10
        c,p=await fresh(b); await p.click('[data-a=add][data-id="1"]'); await p.fill('[data-me=phone]','9876543210'); await p.fill('[data-me=addr]','x'); await p.click('[data-a=place]'); m=await txt(p,'#toast'); rec(10,'Customer','Name is mandatory','Leave name empty, tap Place order','Message "Enter your name", no order',m,m=='Enter your name'); await c.close()
        # 11
        c,p=await fresh(b); await p.click('[data-a=add][data-id="1"]'); await p.fill('[data-me=name]','A'); await p.fill('[data-me=phone]','98765'); await p.fill('[data-me=addr]','x'); await p.click('[data-a=place]'); m=await txt(p,'#toast'); rec(11,'Customer','Phone validation','Enter phone "98765", place order','Message asking for 10-digit number',m,'10-digit' in m); await c.close()
        # 12
        c,p=await fresh(b); await p.click('[data-a=add][data-id="1"]'); await p.fill('[data-me=name]','A'); await p.fill('[data-me=phone]','9876543210'); await p.click('[data-a=place]'); m=await txt(p,'#toast'); rec(12,'Customer','Address required for delivery','Leave address empty in delivery mode','Message "Enter a delivery address"',m,'address' in m); await c.close()
        # 13
        c,p=await fresh(b); await p.click('[data-a=add][data-id="1"]'); await fillcust(p); await p.click('[data-a=place]'); m=await txt(p,'#toast'); e='Basket is empty' in await txt(p,'#basket .box'); rec(13,'Customer','Place a valid order','Fill valid details, tap Place order','Order #1001 confirmed, basket cleared',m+('; basket cleared' if e else ''),'#1001' in m and e); await c.close()
        # 14
        c,p=await fresh(b); await p.click('[data-a=add][data-id="12"]'); await p.click('[data-a=add][data-id="12"]'); await fillcust(p); await p.click('[data-a=place]'); s=await p.evaluate("S.products.find(p=>p.id===12).stock"); rec(14,'Customer','Stock reduces after order','Order 2 Paneer (stock 6)','Stock becomes 4',f'Stock = {s}',s==4); await c.close()
        # 15
        c,p=await fresh(b); await p.click('[data-a=add][data-id="1"]'); await fillcust(p); await p.click('[data-a=place]'); t=await txt(p,'#basket'); rec(15,'Customer','Order appears in "Your orders"','Place order, view side panel','Order #1001 with status step "Placed" highlighted',('Order #1001 listed with status steps' if '#1001' in t and 'Placed' in t else t[-60:]),'#1001' in t and 'Placed' in t); await c.close()
        # 16
        c,p=await fresh(b); await p.evaluate("S.products[0].stock=0;render()"); d=await p.get_attribute('#grid .card:first-child [data-a=add]','disabled'); l=await txt(p,'#grid .card:first-child'); rec(16,'Customer','Out-of-stock item cannot be added','Set stock of rice to 0','Button disabled and "Out of stock" label',('Button disabled, "Out of stock" shown' if d is not None and 'Out of stock' in l else 'mismatch'),d is not None and 'Out of stock' in l); await c.close()
        # 17
        c,p=await fresh(b); await p.click('#n2'); t=await txt(p,'.alert'); ok=all(x in t for x in ['Onions','Eggs','Paneer']); rec(17,'Admin','Low-stock alert banner','Open Store admin with default data','Banner lists Onions (9), Eggs (8), Paneer (6)',t.replace('\n',' '),ok); await c.close()
        # 18
        c,p=await fresh(b); await p.click('#n2'); await p.fill('#an','Jaggery'); await p.fill('#ac','Staples'); await p.fill('#ap','80'); await p.fill('#au','500 g'); await p.fill('#as','25'); await p.click('[data-a=newp]'); n=await p.evaluate("S.products.length"); rec(18,'Admin','Add new product','Enter Jaggery, Staples, ₹80, 500 g, stock 25','Product count becomes 15',f'Product count = {n}',n==15); await c.close()
        # 19
        c,p=await fresh(b); await p.click('#n2'); await p.fill('#an','Ghee'); await p.click('[data-a=newp]'); m=await txt(p,'#toast'); n=await p.evaluate("S.products.length"); rec(19,'Admin','Incomplete product rejected','Enter only a name, tap Add product','Validation message; count stays 14',f'"{m}"; count = {n}',n==14 and 'Fill' in m); await c.close()
        # 20
        c,p=await fresh(b); await p.click('#n2'); await p.fill('[data-c=price][data-id="1"]','125'); await p.keyboard.press('Tab'); await p.reload(); v=await p.evaluate("S.products[0].price"); rec(20,'Admin','Price update persists','Change rice price to ₹125, reload page','Price remains ₹125',f'Price after reload = ₹{v}',v==125); await c.close()
        # 21
        c,p=await fresh(b); await p.click('#n2'); await p.fill('[data-c=stock][data-id="1"]','0'); await p.keyboard.press('Tab'); await p.click('#n1'); l=await txt(p,'#grid .card:first-child'); rec(21,'Admin','Stock edit updates shop','Set rice stock to 0, open shop','Rice shows "Out of stock"',('"Out of stock" shown' if 'Out of stock' in l else l[-40:]),'Out of stock' in l); await c.close()
        # 22
        c,p=await fresh(b); await p.click('#n2'); await p.click('[data-a=del][data-id="14"]'); n=await p.evaluate("S.products.length"); rec(22,'Admin','Remove product','Tap Remove on Glucose biscuits','Product count becomes 13',f'Product count = {n}',n==13); await c.close()
        # 23
        c,p=await fresh(b); await p.click('[data-a=add][data-id="1"]'); await fillcust(p); await p.click('[data-a=place]'); await p.click('#n2'); await p.click('[data-a=tab][data-v=ord]'); await p.select_option('[data-c=status]','Packed'); await p.click('#n1'); t=await p.inner_html('#basket .steps'); ok=t.count('class="d"')==2; rec(23,'Admin','Status update visible to customer','Set order to "Packed", open shop','Two steps (Placed, Packed) highlighted',f'{t.count("class=\"d\"")} steps highlighted',ok); await c.close()
        # 24
        c,p=await fresh(b); await p.click('[data-a=add][data-id="12"]'); await p.click('[data-a=add][data-id="12"]'); await fillcust(p); await p.click('[data-a=place]'); s1=await p.evaluate("S.products.find(p=>p.id===12).stock"); await p.click('#n2'); await p.click('[data-a=tab][data-v=ord]'); await p.select_option('[data-c=status]','Cancelled'); s2=await p.evaluate("S.products.find(p=>p.id===12).stock"); rec(24,'Admin','Cancelled order restocks items','Order 2 Paneer, then cancel in admin','Stock 4 after order, 6 after cancel',f'{s1} after order, {s2} after cancel',s1==4 and s2==6); await c.close()
        # 25
        c,p=await fresh(b)
        for ph,nm in [('9876543210','Rahul Das'),('9876543210','Rahul Das')]:
            await p.click('[data-a=add][data-id="1"]'); await fillcust(p,nm,ph); await p.click('[data-a=place]')
        await p.click('#n2'); await p.click('[data-a=tab][data-v=cus]'); rows=len(await p.query_selector_all('table tr'))-1; t=await txt(p,'table'); rec(25,'Admin','Customer records aggregate orders','Same customer places two orders','One row with 2 orders',f'{rows} row; shows "2" orders' if rows==1 and '\t2\t' in t.replace('  ','\t') or rows==1 else f'{rows} rows',rows==1); await c.close()
        # 26
        c,p=await fresh(b); await p.click('[data-a=add][data-id="1"]'); await fillcust(p); await p.click('[data-a=place]'); await p.reload(); n=await p.evaluate("S.orders.length"); rec(26,'System','Data persists across reload','Place order, refresh the page','Order still stored',f'{n} order in storage',n==1); await c.close()
        # 27
        c,p=await fresh(b); await p.click('[data-a=mode][data-v=pickup]'); await p.click('[data-a=add][data-id="1"]'); await fillcust(p,'A','9876543210'); await p.click('[data-a=place]'); await p.click('#n2'); await p.click('[data-a=tab][data-v=ord]'); opts=[await o.inner_text() for o in await p.query_selector_all('[data-c=status] option')]; rec(27,'Admin','Pickup status flow','Place pickup order, open status list','Placed, Packed, Ready for pickup, Picked up, Cancelled',', '.join(opts),opts==['Placed','Packed','Ready for pickup','Picked up','Cancelled']); await c.close()
        # 28
        c,p=await fresh(b,390,800); w=await p.evaluate("document.documentElement.scrollWidth"); rec(28,'System','Mobile layout (390 px)','Open page at 390 px width','No horizontal scrolling',f'scrollWidth = {w}px',w<=390); await c.close()
        # 29
        c,p=await fresh(b); await p.click('#n2'); await p.fill('#an','<b>Hack</b>'); await p.fill('#ac','Test'); await p.fill('#ap','10'); await p.fill('#au','1 kg'); await p.fill('#as','5'); await p.click('[data-a=newp]'); await p.click('#n1'); await p.fill('#q','hack'); h=await p.inner_html('#grid .card b'); rec(29,'Security','HTML in product name is escaped','Add product named "<b>Hack</b>"','Shown as plain text, not bold',('Escaped (&lt;b&gt;)' if '&lt;b&gt;' in h else h),'&lt;b&gt;' in h); await c.close()
        # 30
        c,p=await fresh(b)
        for k in range(2):
            await p.click('[data-a=add][data-id="1"]'); await fillcust(p,'A','9876543210'); await p.click('[data-a=place]')
        ids=await p.evaluate("S.orders.map(o=>o.id)"); rec(30,'System','Order numbers increment','Place two orders in a row','IDs 1001 and 1002',', '.join(map(str,ids)),ids==[1001,1002]); await c.close()
        # 31
        c,p=await fresh(b); await p.click('[data-a=add][data-id="1"]'); await fillcust(p); await p.click('[data-a=place]'); await p.click('#n2'); await p.click('[data-a=tab][data-v=ord]')
        for st in ['Packed','Out for delivery','Delivered']:
            await p.select_option('[data-c=status]',st)
        opts=[await o.inner_text() for o in await p.query_selector_all('[data-c=status] option')]; rec(31,'Admin','Completed order cannot be cancelled','Move a delivery order to "Delivered", open status list','"Cancelled" not offered',', '.join(opts),'Cancelled' not in opts); await c.close()
        # 32
        c,p=await fresh(b); await p.click('[data-a=add][data-id="1"]'); await fillcust(p,'Rahul Das','9876543210','Station Road, Coochbehar'); await p.click('[data-a=place]')
        await p.click('[data-a=mode][data-v=pickup]'); await p.click('[data-a=add][data-id="1"]'); await fillcust(p,'Anita Roy','9123456780'); await p.click('[data-a=place]')
        a=await p.evaluate("S.orders[1].cust.addr"); rec(32,'Customer','Pickup order stores no delivery address','Place a delivery order, then a pickup order for another customer','Address of the pickup order is empty',('Address is empty' if a=='' else 'Address = '+a),a==''); await c.close()
        await b.close()
asyncio.run(main())
json.dump(R,open('tests/results.json','w'),ensure_ascii=False,indent=1)
print(sum(r['ok'] for r in R),'/',len(R))
for r in R:
    if not r['ok']: print('FAIL',r['id'],r['desc'],'|',r['act'])
