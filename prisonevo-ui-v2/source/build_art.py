"""Deterministic Minecraft-style UI. No image-generation model or antialiasing.

Uses the client's own textures to render custom voxel objects and the client's
bitmap font to typeset UI. Pass an official 1.21.8 client.jar as first argument.
Only rendered UI assets are written to the output, never the client archive.
"""
import json, math, sys, zipfile
from pathlib import Path
from PIL import Image, ImageDraw, ImageEnhance

ROOT=Path(__file__).resolve().parents[1]
JAR=Path(sys.argv[1])
z=zipfile.ZipFile(JAR)
def load(p):
    import io
    return Image.open(io.BytesIO(z.read('assets/minecraft/'+p))).convert('RGBA')
def tex(name): return load('textures/block/'+name+'.png')
def tint(im,c):
    out=im.copy(); px=out.load()
    for y in range(out.height):
        for x in range(out.width):
            r,g,b,a=px[x,y];v=(r+g+b)/765;px[x,y]=(int(c[0]*v),int(c[1]*v),int(c[2]*v),a)
    return out
def shade(c,s): return tuple(min(255,int(v*s)) for v in c[:3])+(c[3],)
def poly(im,pts,c): ImageDraw.Draw(im).polygon(pts,fill=c)

class Iso:
    def __init__(self,scale=7,origin=(48,69),size=96):
        self.s=scale;self.o=origin;self.im=Image.new('RGBA',(size,size));self.jobs=[];self.depth=[[-1e9]*size for _ in range(size)]
    def pos(self,p):
        x,y,h=p;return (self.o[0]+(x-y)*self.s,self.o[1]+(x+y)*self.s*.5-h*self.s)
    def face(self,points,texture,brightness=1):
        pts=[self.pos(p) for p in points]
        # Affine nearest-neighbor sampling into a discrete polygon mask.
        mask=Image.new('1',self.im.size);ImageDraw.Draw(mask).polygon(pts,fill=1)
        a,b,_,d=pts; ux,uy=b[0]-a[0],b[1]-a[1];vx,vy=d[0]-a[0],d[1]-a[1]
        det=ux*vy-uy*vx
        if abs(det)<.01:return
        pix=self.im.load(); m=mask.load();t=texture.load()
        for py in range(max(0,int(min(p[1] for p in pts))),min(self.im.height,math.ceil(max(p[1] for p in pts))+1)):
            for px in range(max(0,int(min(p[0] for p in pts))),min(self.im.width,math.ceil(max(p[0] for p in pts))+1)):
                if not m[px,py]:continue
                dx,dy=px+.5-a[0],py+.5-a[1]
                u=(dx*vy-dy*vx)/det;v=(dy*ux-dx*uy)/det
                c=t[min(texture.width-1,max(0,int(u*texture.width))),min(texture.height-1,max(0,int(v*texture.height)))]
                world=[points[0][i]+u*(points[1][i]-points[0][i])+v*(points[3][i]-points[0][i]) for i in range(3)]
                depth=sum(world)
                if c[3] and depth>=self.depth[py][px]-.001:
                    pix[px,py]=shade(c,brightness);self.depth[py][px]=depth
    def box(self,x,y,h,w,d,ht,top,side=None,front=None):
        side=side or top;front=front or side
        # Painter's order: each face gets a world-depth key.
        faces=[([(x,y+d,h),(x+w,y+d,h),(x+w,y+d,h+ht),(x,y+d,h+ht)],front,.82),
               ([(x+w,y,h),(x+w,y+d,h),(x+w,y+d,h+ht),(x+w,y,h+ht)],side,.61),
               ([(x,y,h+ht),(x+w,y,h+ht),(x+w,y+d,h+ht),(x,y+d,h+ht)],top,1.0)]
        for pts,t,b in faces:self.jobs.append((sum(p[0]+p[1]+p[2]*.08 for p in pts)/4,pts,t,b))
    def finish(self):
        for _,pts,t,b in sorted(self.jobs,key=lambda j:j[0]):self.face(pts,t,b)
        return self.im

stone=tex('stone');dirt=tex('dirt');grass=tint(tex('grass_block_top'),(117,171,70))
grassside=tex('grass_block_side'); overlay=tint(tex('grass_block_side_overlay'),(117,171,70));grassside.alpha_composite(overlay)
oak=tex('oak_planks');log=tex('oak_log');iron=tex('iron_block');black=tex('deepslate_tiles');gold=tex('gold_block')
leaves=tint(tex('oak_leaves'),(100,155,57)); darkoak=tex('dark_oak_planks')
def fit(im,size=64,pad=1):
    bb=im.getbbox();im=im.crop(bb);ratio=min((size-2*pad)/im.width,(size-2*pad)/im.height)
    out=Image.new('RGBA',(size,size));im=im.resize((max(1,round(im.width*ratio)),max(1,round(im.height*ratio))),Image.Resampling.NEAREST)
    out.alpha_composite(im,((size-im.width)//2,(size-im.height)//2));return out

def island():
    r=Iso(7,(48,52))
    # Jagged floating stone foundation; no thick outline or arbitrary shading.
    for x in range(5):
        for y in range(5):
            if (x,y) in [(0,0),(0,4),(4,0),(4,4)]:continue
            depth=1+(1 if 1<=x<=3 and 1<=y<=3 else 0)+(1 if x==2 and y==2 else 0)
            r.box(x-2.5,y-2.5,-depth,1,1,depth,stone,tex('diamond_ore') if (x,y)==(4,2) else stone)
            if not (1<=x<=3 and 1<=y<=3):r.box(x-2.5,y-2.5,0,1,1,.5,grass,grassside)
            else:r.box(x-2.5,y-2.5,-.55,1,1,.2,tex('iron_ore') if (x+y)%2 else stone)
    r.box(-2,-1.8,.5,.55,.55,2.0,tex('oak_log_top'),log)
    r.box(-2.65,-2.45,2.3,1.9,1.9,.9,leaves)
    r.box(-2.3,-2.1,3.2,1.2,1.2,.65,leaves)
    # Timber lamp at the opposite rim.
    r.box(1.2,-1.8,.5,.22,.22,1.8,oak)
    r.box(.7,-1.8,2.15,.7,.22,.2,oak)
    r.box(.7,-1.78,1.45,.35,.35,.6,gold)
    return fit(r.finish())

def barrel(full=False):
    r=Iso(10,(46,39))
    r.box(-1.6,-1.4,-1,3.2,2.8,3.2,tex('barrel_top'),tex('barrel_side'))
    r.box(-.95,-.65,2.2,1.1,1,.35,iron)
    r.box(.35,-.6,2.2,1,.9,.35,gold)
    if full:r.box(-1.8,1.1,-1.2,1.1,1.1,.8,tex('diamond_block'))
    return fit(r.finish())

def drill(active=True):
    r=Iso(8,(45,42))
    # Two long metal-capped track assemblies, timber chassis and piston engine.
    for y in (-1.65,1.0):
        r.box(-2.7,y,-1.2,4.3,.7,.8,black)
        for x in (-2.35,-1.2,-.05,1.1):r.box(x,y+.71,-1.05,.65,.09,.47,iron)
    r.box(-2.3,-1.1,-.4,3.4,2.2,.6,darkoak,oak)
    r.box(-1.8,-.95,.2,2,1.9,1.7,tex('piston_top'),tex('piston_side'))
    r.box(-1.9,-1,1.9,2.2,2.05,.28,iron)
    r.box(-1.5,-.7,2.18,.35,.35,.9,black)
    r.box(.3,-.72,.4,.9,1.45,1.15,iron)
    for i in range(4):
        width=1.8-i*.4
        r.box(.7+i*.6,-width/2,.85-width/2,.58,width,width,iron,tex('smooth_stone'))
    im=r.finish()
    # Little actual status lamp; no drawn letters.
    pos=r.pos((-.7,1.02,1.1));ImageDraw.Draw(im).rectangle((int(pos[0]),int(pos[1]),int(pos[0])+2,int(pos[1])+2),fill='#94b84a' if active else '#7b6655')
    return fit(im)

def cube_icon(name):
    r=Iso(13,(48,44));r.box(-1.2,-1.2,-1.2,2.4,2.4,2.4,tex(name));return fit(r.finish())
def item(name):return fit(load('textures/item/'+name+'.png'),64,4)
def anvil():
    r=Iso(13,(48,46));a=tex('anvil');t=tex('anvil_top')
    r.box(-1.2,-.8,-1.4,2.4,1.6,.35,a)
    r.box(-.6,-.5,-1.05,1.2,1,.9,a)
    r.box(-1.5,-.7,-.15,3,1.4,.65,t,a)
    return fit(r.finish())
def icon_on_cube(name,block):
    im=cube_icon(block); it=item(name).resize((43,43),Image.Resampling.NEAREST);im.alpha_composite(it,(18,17));return im

def friends():
    r=Iso(13,(48,47))
    for name,x,y,h in [('alex',-.5,-1.5,.6),('steve',-.7,.3,-.5)]:
        skin=load(f'textures/entity/player/wide/{name}.png')
        top=skin.crop((8,0,16,8));front=skin.crop((8,8,16,16));side=skin.crop((0,8,8,16))
        r.box(x,y,h,1.7,1.7,1.7,top,side,front)
    return fit(r.finish())

icons={'island':island(),'drill_active':drill(),'storage':barrel(),'mine':icon_on_cube('diamond_pickaxe','diamond_ore'),
       'upgrades':anvil(),'friends':friends(),
       'progress':item('experience_bottle'),'help':item('book'),'panda':None,'drill_idle':drill(False),'storage_full':barrel(True)}
# A panda head is modeled as a small voxel block with deliberately placed eyes.
white=Image.new('RGBA',(16,16),'#deded5');f=ImageDraw.Draw(white);f.rectangle((1,4,5,9),fill='#343332');f.rectangle((10,4,14,9),fill='#343332');f.rectangle((4,5,4,6),fill='#f2f2e9');f.rectangle((11,5,11,6),fill='#f2f2e9');f.rectangle((6,10,9,11),fill='#343332')
r=Iso(14,(48,42));r.box(-1,-1,-1,2,2,2,Image.new('RGBA',(16,16),'#dad9d0'),Image.new('RGBA',(16,16),'#deded5'),white)
r.box(-1,-1,1,.55,.55,.45,black);r.box(.45,-1,1,.55,.55,.45,black);icons['panda']=fit(r.finish())
for n in ['coal','iron','gold','redstone','lapis','diamond']:icons[n]=item({'iron':'iron_ingot','gold':'gold_ingot','lapis':'lapis_lazuli'}.get(n,n))
icons['sell']=item('gold_ingot');icons['spawn']=item('compass_16')
icons['speed']=item('clock_00')
# Navigation is intentionally the low-contrast monochrome pixel language of the server tabs.
for n in ['back','close']:
    im=Image.new('RGBA',(64,64));d=ImageDraw.Draw(im)
    pts=([(14,30),(30,14),(30,24),(49,24),(49,38),(30,38),(30,48)] if n=='back' else [(18,12),(30,24),(42,12),(50,20),(38,32),(50,44),(42,52),(30,40),(18,52),(10,44),(22,32),(10,20)])
    d.polygon(pts,fill='#686967');icons[n]=im

(ROOT/'png').mkdir(exist_ok=True,parents=True)
for n,im in icons.items():im.save(ROOT/'png'/f'{n}.png')

# Minecraft's own bitmap typography: precise glyphs, no generated lettering.
providers=json.loads(z.read('assets/minecraft/font/include/default.json'))['providers'];glyphs={}
for p in providers:
    if p['type']!='bitmap':continue
    sheet=load('textures/'+p['file'].split(':')[1]);rows=p['chars'];cw=sheet.width//len(rows[0]);ch=sheet.height//len(rows)
    for yy,row in enumerate(rows):
        for xx,c in enumerate(row):
            if c=='\0':continue
            g=sheet.crop((xx*cw,yy*ch,(xx+1)*cw,(yy+1)*ch));bb=g.getbbox()
            if bb:
                if cw!=8 or ch!=8:g=g.resize((8,8),Image.Resampling.NEAREST)
                glyphs[c]=(g, max(1,round(bb[2]*8/cw)))
glyphs[' ']=(Image.new('RGBA',(3,8)),3)
def textwidth(t):return sum(glyphs.get(c,glyphs['?'])[1]+1 for c in t)-1
def text(im,t,x,y,color='#343434',center=False,shadow=False):
    if center:x-=textwidth(t)//2
    for c in t:
        g,w=glyphs.get(c,glyphs['?']);ink=Image.new('RGBA',g.size,color);ink.putalpha(g.getchannel('A'))
        if shadow:
            sh=Image.new('RGBA',g.size,'#41413c');sh.putalpha(g.getchannel('A'));im.alpha_composite(sh,(x+1,y+1))
        im.alpha_composite(ink,(x,y));x+=w+1

GRAY='#c6c6c6'; BLACK='#171717'
def bevel(im,box,fill=GRAY,pressed=False):
    d=ImageDraw.Draw(im);x,y,x2,y2=box;d.rectangle(box,fill=BLACK)
    d.rectangle((x+1,y+1,x2-1,y2-1),fill=fill)
    hi,lo=('#f6f6f6','#626262') if not pressed else ('#626262','#f6f6f6')
    d.line([(x+1,y2-1),(x+1,y+1),(x2-1,y+1)],fill=hi)
    d.line([(x+2,y2-1),(x2-1,y2-1),(x2-1,y+2)],fill=lo)

def base(title):
    im=Image.new('RGBA',(256,256))
    bevel(im,(0,24,175,245))
    bevel(im,(22,2,153,16))
    text(im,title,88,6,center=True)
    # Player inventory coordinates exactly match a six-row Java chest screen.
    d=ImageDraw.Draw(im)
    for row in range(3):
        for col in range(9):
            x,y=7+col*18,24+139+row*18;d.rectangle((x,y,x+17,y+17),fill='#8b8b8b');d.line([(x,y+17),(x,y),(x+17,y)],fill='#373737');d.line([(x+1,y+17),(x+17,y+17),(x+17,y+1)],fill='#ffffff')
    for col in range(9):
        x,y=7+col*18,24+197;d.rectangle((x,y,x+17,y+17),fill='#8b8b8b');d.line([(x,y+17),(x,y),(x+17,y)],fill='#373737');d.line([(x+1,y+17),(x+17,y+17),(x+17,y+1)],fill='#ffffff')
    return im
def heading(im,t):
    text(im,t,7,30,'#565656');x=7+textwidth(t)+5
    ImageDraw.Draw(im).line((x,33,167,33),fill='#666666')
def place(im,name,x,y,size):im.alpha_composite(icons[name].resize((size,size),Image.Resampling.NEAREST),(x,y+24))
def card(im,box,name,label,size=40,fill=GRAY):
    x,y,x2,y2=box;bevel(im,(x,y+24,x2,y2+24),fill)
    place(im,name,x+(x2-x+1-size)//2,y+2,size)
    text(im,label,(x+x2)//2,y2+24-9,center=True)
def footer(im,main=False):
    bevel(im,(7,131,60,148))
    text(im,'На сервер' if main else 'Назад',34,137,center=True)
    bevel(im,(151,131,168,148));place(im,'close',154,110,12)

pages={}
im=base('PRISONEVO');heading(im,'Личный остров')
for x,n,l in [(7,'island','Остров'),(61,'drill_active','Бур'),(115,'storage','Склад')]:card(im,(x,17,x+53,70),n,l,40)
for x,n,l in [(7,'mine','Шахта'),(61,'upgrades','Развитие'),(115,'help','Помощь')]:card(im,(x,71,x+53,106),n,l,23)
footer(im,True);place(im,'storage',64,109,14);pages['main']=im

for name,title,hero in [('storage','ХРАНИЛИЩЕ','storage'),('drill','БУР','drill_active'),('mine','ШАХТА','mine')]:
    im=base(title);heading(im,{'storage':'Ресурсы острова','drill':'Автоматическая добыча','mine':'Личный карьер'}[name])
    bevel(im,(7,41,78,130));place(im,hero,12,19,62)
    text(im,{'storage':'Добыто','drill':'За цикл','mine':'Обновление'}[name],43,109,center=True)
    if name=='storage':
        card(im,(79,17,168,70),'sell','Продать всё',36,'#8cb371')
        bevel(im,(79,95,168,130));place(im,'storage_full',82,74,24);text(im,'Улучшить',134,102,center=True);text(im,'склад',134,113,center=True)
    elif name=='drill':
        bevel(im,(79,41,168,94));text(im,'Скорость',86,48);place(im,'speed',139,23,24)
        bevel(im,(79,95,168,130));text(im,'Мощность',86,102)
    else:
        bevel(im,(79,41,168,94));text(im,'Качество',86,48);place(im,'upgrades',139,23,24)
        bevel(im,(79,95,168,130));place(im,'help',82,73,25);text(im,'Помощь',136,109,center=True)
    footer(im);pages[name]=im

im=base('УЛУЧШЕНИЯ');heading(im,'Развитие острова')
for box,n,l in [((7,17,78,70),'progress','Скорость'),((79,17,168,70),'drill_active','Мощность'),((7,71,78,106),'storage','Склад'),((79,71,168,106),'mine','Шахта')]:card(im,box,n,l,36 if box[1]==17 else 23)
footer(im);pages['upgrades']=im
im=base('КАК ИГРАТЬ');heading(im,'Коротко о добыче')
for i,line in enumerate(['Добывай блоки в карьере.','Добыча попадает на склад.','Бур добывает автоматически.','Продажа даёт монеты острова.','Улучшай бур, склад и шахту.','Остров нельзя перестраивать.']):text(im,line,8,45+i*12,'#494949')
footer(im);pages['help']=im

pack=ROOT/'resourcepack';ns=pack/'assets/prisonevo'
for p in ['font','textures/gui','textures/item','textures/font','models/item','items']:(ns/p).mkdir(parents=True,exist_ok=True)
(ns/'font/data_84.json').unlink(missing_ok=True)
(pack/'pack.mcmeta').write_text(json.dumps({'pack':{'pack_format':64,'description':'PrisonEvo UI · Minecraft 1.21.8'}},ensure_ascii=False,indent=2))
def write(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2),encoding='utf-8')
gui=[]
for i,(n,im) in enumerate(pages.items()):
    im.save(ns/'textures/gui'/f'{n}.png');gui.append({'type':'bitmap','file':f'prisonevo:gui/{n}.png','ascent':37,'height':256,'chars':[chr(0xE001+i)]})
write(ns/'font/gui.json',{'providers':gui})
write(ns/'font/spacing.json',{'providers':[{'type':'space','advances':{chr(0xE400+i+512):i for i in range(-512,513)}}]})
# A small, namespaced digit atlas isolates numeric metrics from other server packs.
number_chars='0123456789/.kM'
numbers=Image.new('RGBA',(128,8))
for i,c in enumerate(number_chars):numbers.alpha_composite(glyphs[c][0],(i*8,0))
numbers.save(ns/'textures/font/numbers.png')
for ypos in [49,90,96,113]:
    p={'type':'bitmap','file':'prisonevo:font/numbers.png','height':8,'ascent':13-ypos,'chars':[number_chars+'\0'*(16-len(number_chars))]}
    write(ns/'font'/f'data_{ypos}.json',{'providers':[{'type':'space','advances':{' ':4}},p]})
write(ns/'models/item/ui_button.json',{'elements':[]})
write(ns/'items/ui_button.json',{'model':{'type':'minecraft:model','model':'prisonevo:item/ui_button'}})
for n,im in icons.items():
    im.save(ns/'textures/item'/f'{n}.png')
    write(ns/'models/item'/f'{n}.json',{'parent':'minecraft:item/generated','textures':{'layer0':f'prisonevo:item/{n}'}})
    write(ns/'items'/f'{n}.json',{'model':{'type':'minecraft:model','model':f'prisonevo:item/{n}'}})

# Real-size menu composition. Preview values are explicit sample data only.
samples={ 'main':[(82,113,'640/1000')], 'storage':[(12,96,'640/1000')], 'drill':[(86,49,'1 / 10'),(86,90,'1 / 10'),(30,96,'2')], 'mine':[(99,49,'1 / 10'),(27,96,'04:32')] }
(ROOT/'previews').mkdir(exist_ok=True)
for n,im in pages.items():
    show=im.crop((0,0,176,246)).copy()
    text(show,'Инвентарь',8,152,'#404040')
    for x,y,t in samples.get(n,[]):text(show,t,x,y+24,'#4c4c4c')
    show.resize((704,984),Image.Resampling.NEAREST).save(ROOT/'previews'/f'{n}.png')
sheet=Image.new('RGB',(1536,1152),'#242726');sheetd=ImageDraw.Draw(sheet)
for i,n in enumerate(['main','storage','drill','mine','upgrades','help']):
    thumb=Image.open(ROOT/'previews'/f'{n}.png').resize((352,492),Image.Resampling.NEAREST)
    x=36+(i%3)*508;y=36+(i//3)*558;sheet.paste(thumb,(x+60,y));
sheet.save(ROOT/'previews/menus.png')
# Icons at 3× with a common vanilla gray backing, never smoothed.
board=Image.new('RGBA',(936,760),'#262828')
for i,n in enumerate(['island','drill_active','storage','mine','upgrades','help','panda','storage_full','progress']):
    x=12+(i%3)*308;y=12+(i//3)*246;bevel(board,(x,y,x+295,y+231))
    board.alpha_composite(icons[n].resize((192,192),Image.Resampling.NEAREST),(x+52,y+5))
    text(board,{'island':'Мой остров','drill_active':'Бур','storage':'Хранилище','mine':'Шахта','upgrades':'Улучшения','help':'Помощь','panda':'Панда','storage_full':'Полный склад','progress':'Прогресс'}[n],x+148,y+210,center=True)
board.convert('RGB').save(ROOT/'previews/icons.png')
with zipfile.ZipFile(ROOT/'PrisonEvo-UI-resourcepack-1.21.8.zip','w',zipfile.ZIP_DEFLATED) as out:
    for p in sorted(pack.rglob('*')):
        if p.is_file():out.write(p,p.relative_to(pack))
print(f'Built {len(icons)} textured icons, 6 slot-aligned menus and resource pack format 64.')
