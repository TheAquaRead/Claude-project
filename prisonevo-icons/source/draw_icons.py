from PIL import Image, ImageDraw, ImageFont
from pathlib import Path
import zipfile, json

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'png'; OUT.mkdir(exist_ok=True)
INK='#202426'; EDGE='#3a3b36'; HI='#e1e0cc'
WOOD='#98613a'; WOOD_L='#c18a4c'; WOOD_D='#623e2d'
STEEL='#8b989d'; STEEL_L='#c4d0cd'; STEEL_D='#53626b'
GREEN='#669846'; GREEN_L='#9bb85b'; GREEN_D='#3e663d'
GOLD='#d99d3b'; GOLD_L='#f1cf76'; GOLD_D='#966330'
BLUE='#489d9c'; BLUE_L='#9dd5c1'; BLUE_D='#2f616d'

class Sprite:
    def __init__(self):
        self.im=Image.new('RGBA',(32,32)); self.d=ImageDraw.Draw(self.im)
    def p(self,pts,c,outline=None): self.d.polygon(pts,fill=c,outline=outline)
    def r(self,box,c): self.d.rectangle(box,fill=c)
    def l(self,pts,c,w=1): self.d.line(pts,fill=c,width=w)
    def save(self,name): self.im.save(OUT/f'{name}.png'); return self.im

def island():
    s=Sprite()
    # Isometric grassy cap, exposed stone underside and a deliberately stepped silhouette.
    s.p([(3,17),(14,12),(28,16),(28,20),(24,23),(23,26),(19,27),(17,30),(12,28),(10,25),(6,24),(6,21),(3,20)],INK)
    s.p([(4,18),(14,14),(17,18),(17,28),(13,27),(11,24),(7,23),(7,20)],'#7b8078')
    s.p([(17,18),(27,17),(27,20),(23,22),(22,25),(19,26),(18,28)],'#505d59')
    s.p([(4,16),(14,12),(27,15),(29,17),(18,22),(3,18)],INK)
    s.p([(5,16),(14,13),(26,16),(17,20),(5,18)],GREEN)
    s.l([(6,16),(14,14),(24,16)],GREEN_L)
    s.p([(4,18),(17,21),(28,17),(27,19),(17,23),(5,20)],WOOD_D)
    s.l([(5,18),(17,21),(26,18)],WOOD_L)
    # Quarry opening and stone steps.
    s.p([(13,15),(18,14),(24,16),(19,19),(13,18)],'#414e49')
    s.l([(14,15),(18,15),(22,16)],'#a5a79a')
    s.l([(14,16),(18,17),(21,17)],'#717d70')
    s.r((13,23,14,24),BLUE); s.r((14,23,14,23),BLUE_L)
    s.r((20,22,21,23),GOLD); s.r((8,21,9,22),'#b6b6a0')
    s.r((15,27,16,27),'#a1a495')
    # Compact oak tree.
    s.r((8,9,10,15),INK); s.r((9,9,9,14),WOOD); s.r((10,12,10,14),WOOD_D)
    s.p([(3,7),(5,7),(5,4),(8,4),(8,2),(12,2),(12,4),(15,4),(15,8),(13,8),(13,10),(5,10),(5,9),(3,9)],INK)
    s.p([(4,7),(6,7),(6,5),(9,5),(9,3),(11,3),(11,5),(14,5),(14,7),(12,7),(12,9),(6,9),(6,8),(4,8)],GREEN_D)
    s.r((7,5,11,7),GREEN); s.r((9,3,10,5),GREEN_L); s.r((6,6,8,6),GREEN_L)
    # A tiny lantern on a timber post.
    s.r((23,7,24,14),INK); s.r((23,8,23,13),WOOD_L)
    s.r((20,7,23,8),WOOD_D); s.r((20,8,20,9),INK)
    s.r((19,10,21,13),INK); s.r((20,11,20,12),GOLD_L)
    return s

def storage(full=False):
    s=Sprite()
    # Barrel octagonal profile, lid visible, iron hoops.
    s.p([(8,7),(11,5),(22,5),(25,7),(27,11),(27,25),(24,28),(9,28),(5,25),(5,11)],INK)
    s.p([(7,12),(10,9),(23,9),(25,12),(25,24),(23,26),(10,26),(7,24)],WOOD)
    s.p([(18,10),(23,9),(25,12),(25,24),(23,26),(18,26)],WOOD_D)
    s.r((9,13,10,24),WOOD_L); s.r((14,12,14,25),WOOD_D); s.r((19,12,19,25),INK)
    s.l([(8,23),(12,24),(17,24)],WOOD_D)
    for y in (12,21):
        s.p([(6,y),(10,y+1),(22,y+1),(26,y-1),(26,y+2),(22,y+4),(10,y+4),(6,y+2)],INK)
        s.p([(7,y+1),(11,y+2),(21,y+2),(25,y),(25,y+1),(21,y+3),(11,y+3),(7,y+2)],STEEL)
        s.r((9,y+1,10,y+1),STEEL_L); s.r((23,y+1,24,y+1),STEEL_D)
    s.p([(7,8),(11,6),(22,6),(25,8),(23,11),(10,11),(7,9)],INK)
    s.p([(9,8),(12,7),(21,7),(23,8),(21,10),(11,10)],WOOD_L)
    s.l([(12,8),(20,8)],WOOD_D)
    # Visible ores establish that this is a resource store.
    s.p([(10,6),(10,3),(14,2),(18,4),(18,7),(14,9)],INK)
    s.p([(11,4),(14,3),(17,4),(14,6),(11,6)],STEEL_L)
    s.p([(11,6),(14,7),(17,5),(17,7),(14,8)],STEEL_D)
    s.p([(18,7),(18,4),(22,3),(25,5),(25,8),(22,10)],INK)
    s.p([(19,5),(22,4),(24,5),(22,7),(19,7)],GOLD_L)
    s.p([(19,7),(22,8),(24,6),(24,8),(22,9)],GOLD)
    if full:
        s.p([(4,23),(8,20),(12,22),(12,27),(8,30),(4,28)],INK)
        s.p([(5,24),(8,21),(11,23),(8,25)],BLUE_L)
        s.p([(5,25),(8,26),(11,24),(11,27),(8,29),(5,27)],BLUE)
    return s

def drill(active=True):
    s=Sprite()
    # Tracks and squat machine chassis.
    s.p([(3,23),(6,21),(21,21),(24,24),(24,28),(21,30),(5,30),(2,27),(2,25)],INK)
    s.p([(4,24),(6,23),(20,23),(22,25),(22,27),(20,28),(6,28),(4,26)],STEEL_D)
    for x in (6,11,16,20):
        s.r((x,24,x+2,27),INK); s.r((x,25,x+1,26),STEEL)
    s.r((5,21,21,22),GOLD_D)
    s.p([(5,20),(5,10),(8,7),(16,7),(19,10),(19,21),(7,21)],INK)
    s.r((7,10,17,19),GOLD); s.r((7,10,8,18),GOLD_L); s.r((16,10,17,19),GOLD_D)
    s.r((9,9,14,17),INK); s.r((10,10,13,15),STEEL_D); s.r((10,10,12,11),STEEL_L)
    s.r((10,18,12,19),GREEN_L if active else '#a97249')
    s.r((7,6,16,7),INK); s.r((9,5,14,6),STEEL_D); s.r((10,5,13,5),STEEL_L)
    # Motor shaft and a stepped conical drill, facing right.
    s.r((18,12,21,21),INK); s.r((19,13,20,20),GOLD_D)
    s.p([(21,10),(24,10),(24,12),(26,12),(26,14),(28,14),(28,16),(30,17),(30,19),(28,20),(28,22),(24,24),(21,24),(19,22),(19,12)],INK)
    s.p([(21,12),(23,12),(23,14),(25,14),(25,16),(27,16),(27,17),(29,18),(27,19),(27,20),(24,22),(21,22),(20,20),(20,14)],STEEL)
    s.l([(21,12),(21,16),(20,18)],STEEL_L)
    s.l([(23,14),(23,18),(22,21)],STEEL_D,2)
    s.l([(25,16),(25,19),(24,21)],STEEL_L)
    s.r((28,18,29,18),STEEL_L)
    return s

def mine():
    s=Sprite()
    s.p([(3,23),(8,18),(17,18),(22,22),(23,28),(19,30),(4,30),(2,27)],INK)
    s.p([(4,24),(8,20),(16,20),(20,23),(21,27),(18,28),(5,28),(4,27)],STEEL_D)
    s.p([(5,23),(8,21),(15,21),(18,23),(15,25),(6,25)],STEEL)
    for x,y in [(7,23),(15,26),(18,24)]:
        s.r((x,y,x+1,y+1),BLUE); s.r((x,y,x,y),BLUE_L)
    # Diagonal hand-cut handle.
    s.p([(7,24),(9,26),(25,10),(23,8)],INK)
    s.p([(9,23),(10,24),(23,11),(22,10)],WOOD)
    s.l([(9,23),(22,10)],WOOD_L)
    s.p([(8,6),(11,3),(18,3),(23,6),(26,10),(28,15),(26,17),(23,12),(20,9),(16,7),(11,7),(8,9)],INK)
    s.p([(10,6),(12,4),(18,4),(22,7),(25,11),(26,14),(23,10),(20,8),(16,6),(11,6)],BLUE)
    s.l([(12,4),(17,4),(21,6)],BLUE_L)
    s.r((19,7,21,9),GOLD_D); s.r((20,7,21,8),GOLD_L)
    return s

def upgrades():
    s=Sprite()
    pts=[(12,2),(19,2),(19,6),(22,7),(25,5),(28,8),(26,11),(27,14),(30,14),(30,20),(26,20),(25,23),(27,26),(24,29),(21,27),(18,28),(18,31),(12,31),(12,27),(9,26),(6,28),(3,25),(5,22),(4,19),(1,19),(1,13),(5,13),(6,10),(4,7),(7,4),(10,6),(12,5)]
    s.p(pts,INK)
    # Stepped bevel around the ring.
    s.p([(13,3),(18,3),(18,7),(22,9),(25,7),(26,8),(24,11),(25,15),(29,15),(29,18),(25,18),(23,23),(25,26),(24,27),(21,25),(17,26),(17,30),(13,30),(13,26),(9,24),(6,26),(5,25),(7,22),(6,18),(2,18),(2,14),(6,14),(8,10),(6,7),(7,6),(10,8),(13,6)],STEEL)
    s.l([(13,4),(17,4)],STEEL_L); s.l([(7,14),(8,11),(11,9),(14,8),(18,8)],STEEL_L)
    s.p([(12,11),(18,11),(21,14),(21,20),(18,23),(12,23),(9,20),(9,14)],INK)
    s.p([(13,13),(17,13),(19,15),(19,19),(17,21),(13,21),(11,19),(11,15)],STEEL_D)
    # Upgrade arrow in the foreground.
    s.p([(24,15),(31,23),(28,23),(28,30),(21,30),(21,23),(18,23)],INK)
    s.p([(24,17),(29,22),(26,22),(26,28),(23,28),(23,22),(20,22)],GOLD)
    s.l([(24,18),(24,21),(22,21)],GOLD_L); s.r((24,23,24,27),GOLD_L)
    return s

def friends():
    s=Sprite()
    for ox,oy,hair,skin in [(14,4,'#514a3d','#c9a47d'),(3,10,WOOD_D,'#d4b18c')]:
        s.r((ox,oy,ox+12,oy+13),INK); s.r((ox+1,oy+1,ox+11,oy+11),skin)
        s.r((ox+1,oy+1,ox+11,oy+4),hair); s.r((ox+1,oy+4,ox+2,oy+7),hair)
        s.r((ox+4,oy+7,ox+4,oy+8),INK); s.r((ox+9,oy+7,ox+9,oy+8),INK)
        s.r((ox+6,oy+10,ox+8,oy+10),'#9f6e58')
    s.p([(2,26),(6,23),(13,23),(18,26),(18,30),(2,30)],INK)
    s.p([(4,26),(7,24),(12,24),(16,27),(16,28),(4,28)],GREEN)
    s.r((23,20,26,30),INK); s.r((19,24,30,27),INK)
    s.r((24,21,25,29),GREEN_L); s.r((20,25,29,26),GREEN_L)
    return s

def progress():
    s=Sprite()
    for x,top in [(4,22),(12,16),(20,9)]:
        s.r((x,top,x+6,29),INK); s.r((x+1,top+1,x+5,27),GREEN_D)
        s.r((x+1,top+1,x+3,26),GREEN); s.r((x+1,top+1,x+4,top+2),GREEN_L)
    s.l([(3,17),(11,10),(16,12),(26,3)],INK,3)
    s.l([(3,16),(11,9),(16,11),(26,2)],GOLD,1)
    s.p([(21,2),(28,1),(27,8),(25,6),(24,5)],INK)
    s.p([(23,3),(27,2),(26,6)],GOLD_L)
    return s

def helpbook():
    s=Sprite()
    s.p([(4,8),(9,4),(26,4),(28,6),(28,26),(24,29),(5,29),(3,27),(3,9)],INK)
    s.p([(5,9),(9,6),(25,6),(25,25),(7,27),(5,26)],'#735049')
    s.p([(7,8),(10,6),(24,6),(24,23),(8,25),(6,24),(6,9)],'#b77053')
    s.r((8,8,9,22),'#d39567')
    s.p([(7,25),(24,24),(26,22),(26,25),(23,27),(7,27),(5,26)],'#cec7a4')
    s.l([(8,26),(22,26)],'#93896e')
    # Pixel question mark, intentionally drawn; not generated typography.
    s.l([(13,12),(13,10),(19,10),(20,11),(20,14),(17,16),(17,18)],GOLD_L,2)
    s.r((16,20,18,21),GOLD_L)
    return s

def panda():
    s=Sprite()
    s.r((5,4,11,10),INK); s.r((21,4,27,10),INK)
    s.p([(8,7),(23,7),(27,11),(27,24),(23,28),(8,28),(4,24),(4,12)],INK)
    s.p([(9,8),(22,8),(25,11),(25,23),(22,26),(9,26),(6,23),(6,12)],'#cfcec0')
    s.p([(10,8),(21,8),(24,11),(24,20),(21,23),(9,23),(6,20),(6,12)],'#eeedde')
    s.p([(9,12),(13,12),(14,15),(12,19),(8,18),(7,15)],INK)
    s.p([(19,12),(23,13),(24,16),(22,19),(18,18),(17,15)],INK)
    s.r((11,14,12,15),'#eeedde'); s.r((19,14,20,15),'#eeedde')
    s.r((14,20,17,21),INK); s.r((15,22,16,23),INK)
    return s

def resource(kind):
    s=Sprite()
    colors={
        'coal':('#626968','#3d4647','#272f33'),
        'iron':('#e0d7bd','#b8b19e','#827f75'),
        'gold':(GOLD_L,GOLD,GOLD_D),
        'redstone':('#df7561','#b34b44','#703b3d'),
        'lapis':('#8dabc9','#527caa','#38516f'),
        'diamond':(BLUE_L,BLUE,BLUE_D)}
    a,b,c=colors[kind]
    if kind in ('iron','gold'):
        s.p([(4,17),(10,10),(24,10),(28,15),(28,23),(22,27),(7,27),(3,23)],INK)
        s.p([(5,18),(11,12),(23,12),(26,15),(21,20),(7,20)],a)
        s.p([(5,20),(8,22),(21,22),(26,17),(26,22),(21,25),(8,25),(5,23)],b)
        s.l([(22,21),(26,17),(26,22),(22,24)],c)
        s.l([(8,18),(12,14),(21,14)],'#ede5c8' if kind=='iron' else '#ffe2a0')
    elif kind=='diamond':
        s.p([(11,3),(22,3),(28,11),(28,17),(17,29),(13,29),(3,18),(3,11)],INK)
        s.p([(12,5),(20,5),(25,11),(20,15),(10,15),(5,11)],a)
        s.p([(5,13),(10,17),(14,26),(5,17)],b)
        s.p([(11,17),(19,17),(16,26)],a)
        s.p([(21,16),(26,13),(26,16),(18,25)],c)
        s.l([(12,6),(9,11),(18,11)],'#dfecd7')
    else:
        s.p([(7,10),(10,10),(12,5),(20,5),(23,9),(25,10),(25,15),(29,20),(28,25),(23,28),(8,28),(3,23),(3,17)],INK)
        s.p([(8,12),(12,12),(14,7),(19,7),(22,11),(23,15),(27,21),(25,25),(9,26),(5,22),(5,18)],b)
        s.p([(8,13),(13,13),(15,8),(18,8),(19,11),(15,16),(10,17),(6,20)],a)
        s.p([(16,18),(23,15),(27,21),(24,25),(11,25)],c)
        s.r((11,19,13,20),a); s.r((21,12,22,14),a)
    return s

def navigation(kind):
    s=Sprite()
    if kind=='back':
        s.p([(3,15),(14,4),(14,10),(27,10),(27,22),(14,22),(14,28),(3,17)],INK)
        s.p([(5,16),(12,9),(12,12),(25,12),(25,20),(12,20),(12,23)],STEEL)
        s.l([(6,15),(12,9),(12,12),(24,12)],STEEL_L)
    elif kind=='close':
        s.p([(7,3),(15,11),(23,3),(29,9),(21,17),(29,25),(23,31),(15,23),(7,31),(1,25),(9,17),(1,9)],INK)
        s.p([(7,6),(15,14),(23,6),(26,9),(18,17),(26,25),(23,28),(15,20),(7,28),(4,25),(12,17),(4,9)],'#bc6254')
        s.l([(7,6),(15,14),(23,6)],'#e3a27f')
    elif kind=='spawn':
        s.p([(2,15),(15,3),(18,3),(30,15),(27,18),(25,16),(25,29),(7,29),(7,16),(5,18)],INK)
        s.p([(5,14),(16,5),(27,14),(24,14),(16,8),(8,15)],WOOD)
        s.p([(9,16),(16,10),(23,16),(23,27),(9,27)],GREEN)
        s.r((14,19,18,27),INK); s.r((15,20,17,27),WOOD_L)
        s.r((10,17,12,19),GREEN_L)
    else:
        # Coin stack, useful for sell action.
        for x,y in [(14,13),(4,19),(12,3)]:
            s.p([(x,y+3),(x+3,y),(x+10,y),(x+13,y+3),(x+13,y+9),(x+10,y+12),(x+3,y+12),(x,y+9)],INK)
            s.p([(x+1,y+4),(x+4,y+2),(x+9,y+2),(x+12,y+4),(x+12,y+8),(x+9,y+10),(x+4,y+10),(x+1,y+8)],GOLD)
            s.l([(x+2,y+4),(x+5,y+3),(x+9,y+3)],GOLD_L)
            s.l([(x+2,y+8),(x+5,y+9),(x+9,y+9),(x+11,y+7)],GOLD_D)
    return s

sprites={
    'island':island(), 'drill_active':drill(), 'storage':storage(),
    'mine':mine(), 'upgrades':upgrades(), 'friends':friends(),
    'progress':progress(), 'help':helpbook(), 'panda':panda(),
    'drill_idle':drill(False), 'storage_full':storage(True)
}
for kind in ('coal','iron','gold','redstone','lapis','diamond'): sprites[kind]=resource(kind)
for kind in ('back','close','spawn','sell'): sprites[kind]=navigation(kind)
for name,s in sprites.items(): s.save(name)

# Unscaled, transparent atlas: a convenience for inspecting and editing pixels.
atlas=Image.new('RGBA',(32*7,32*3))
for i,s in enumerate(sprites.values()): atlas.paste(s.im,(32*(i%7),32*(i//7)))
atlas.save(ROOT/'atlas.png')

# The preview uses actual PNGs enlarged with nearest-neighbor sampling only.
font='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
font_b='/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
f=ImageFont.truetype(font,20); fb=ImageFont.truetype(font_b,30)
small=ImageFont.truetype(font,16)
canvas=Image.new('RGB',(1200,1190),'#1e2426'); d=ImageDraw.Draw(canvas)
d.text((44,28),'PRISONEVO / ПИКСЕЛЬНЫЕ ИКОНКИ',font=fb,fill='#e2e2d8')
d.text((44,76),'32 × 32 px · ручная отрисовка · PNG с прозрачностью',font=f,fill='#a7b3ad')
labels=[('island','Мой остров'),('drill_active','Бур'),('storage','Хранилище'),('mine','Шахта'),('upgrades','Улучшения'),('friends','Друзья'),('progress','Прогресс'),('help','Помощь'),('panda','Панда')]
for i,(name,label) in enumerate(labels):
    x=44+(i%3)*376; y=130+(i//3)*326
    d.rectangle((x,y,x+359,y+305),fill='#14191b',outline='#414c4c',width=2)
    # Light and dark backing helps inspect silhouette and alpha edges.
    d.rectangle((x+14,y+14,x+345,y+246),fill='#bcbdb5')
    d.line((x+14,y+14,x+345,y+14),fill='#f2f1e3',width=2)
    d.line((x+14,y+14,x+14,y+246),fill='#f2f1e3',width=2)
    icon=sprites[name].im.resize((224,224),Image.Resampling.NEAREST)
    canvas.paste(icon,(x+30,y+18),icon)
    d.rectangle((x+275,y+172,x+330,y+227),fill='#2b3335')
    canvas.paste(sprites[name].im,(x+287,y+184),sprites[name].im)
    d.text((x+18,y+263),label,font=f,fill='#e7e6d9')
    d.text((x+276,y+239),'1:1',font=small,fill='#8f9c95')
d.text((44,1130),'В комплекте также: остановленный бур и заполненное хранилище.',font=f,fill='#acb9af')
canvas.save(ROOT/'preview.png')

# Primary icons at 12×, with no labels to obscure the pixel work.
detail=Image.new('RGB',(1248,456),'#bcbdb5')
for i,name in enumerate(['island','drill_active','storage']):
    im=sprites[name].im.resize((384,384),Image.Resampling.NEAREST)
    detail.paste(im,(16+i*416,24),im)
detail.save(ROOT/'primary-icons.png')

manifest={'canvas':[32,32],'format':'RGBA PNG','scaling':'nearest-neighbor, integer factors only','icons':list(sprites),'status':'art assets only; Nexo configuration requires existing server files'}
(ROOT/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2))
(ROOT/'README.txt').write_text('PrisonEvo — оригинальные пиксельные иконки\n\n21 PNG, каждый 32×32, RGBA с прозрачным фоном.\nВсе формы нарисованы в source/draw_icons.py целочисленными координатами. Генератор изображений не использовался.\n\nДля изменения: Python 3 + Pillow; запустить source/draw_icons.py.\nУвеличивать только nearest-neighbor, в целое число раз.\npreview.png — обзор, primary-icons.png — крупный план, atlas.png — прозрачный атлас 7×3, ячейка 32×32. Порядок ячеек записан в manifest.json, слева направо, сверху вниз.\nЭто графика, не установленный ресурс-пак: реальные пути и настройки Nexo нужно сверить с существующим паком сервера.\n',encoding='utf-8')
with zipfile.ZipFile(ROOT.parent/'prisonevo-icons.zip','w',zipfile.ZIP_DEFLATED) as z:
    for p in sorted(ROOT.rglob('*')):
        relative=p.relative_to(ROOT)
        if p.is_file() and not any(part in {'.git','.venv','__pycache__'} for part in relative.parts):
            z.write(p,'prisonevo-icons/'+str(relative))
print(f'Wrote {len(sprites)} transparent icons, two previews, atlas, editable source and ZIP.')
