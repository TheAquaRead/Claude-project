"""Three original sprites drawn with explicit pixel coordinates.
No procedural texture noise, voxel renderer, antialiasing or image generation.
"""
from pathlib import Path
from PIL import Image, ImageDraw
import json
ROOT=Path(__file__).resolve().parents[1]

class Sprite:
    def __init__(self):
        self.im=Image.new('RGBA',(48,48));self.d=ImageDraw.Draw(self.im)
    def p(self,pts,c,o=None):self.d.polygon(pts,fill=c,outline=o)
    def r(self,box,c):self.d.rectangle(box,fill=c)
    def l(self,pts,c,w=1):self.d.line(pts,fill=c,width=w)

def island():
    s=Sprite()
    # Stone foundation: broad connected clusters, few controlled accents.
    s.p([(3,22),(22,14),(44,22),(43,30),(38,33),(37,36),(32,37),(30,41),(25,45),(20,42),(17,38),(12,37),(11,33),(6,31)],'#414b43')
    s.p([(4,23),(23,30),(24,43),(20,41),(18,36),(13,35),(12,31),(7,29)],'#85877a')
    s.p([(24,30),(43,23),(42,29),(37,31),(36,35),(31,36),(29,40),(25,43)],'#626f64')
    s.p([(7,26),(11,27),(11,31),(8,30)],'#a4a697')
    s.p([(13,30),(18,32),(18,35),(14,34)],'#9c9e8f')
    s.p([(19,35),(23,36),(23,40),(21,39)],'#6c766b')
    s.p([(31,31),(36,29),(36,32),(32,34)],'#4d5e55')
    s.l([(25,36),(28,35),(28,38)],'#839586')
    # One ore cluster, not a speckled texture.
    s.p([(36,27),(39,26),(39,28),(36,30)],'#427f7b')
    s.l([(36,27),(38,26)],'#98d2bb')
    s.p([(13,34),(15,35),(15,36),(13,35)],'#c9b28a')
    # Grass cap and soil lip, proper isometric footprint.
    s.p([(3,20),(22,11),(44,20),(44,23),(25,32),(3,24)],'#514a2b')
    s.p([(4,21),(24,29),(24,31),(4,23)],'#a57542')
    s.p([(25,29),(43,21),(43,23),(25,31)],'#785430')
    s.p([(4,20),(22,12),(43,20),(24,29)],'#6c9638')
    s.l([(5,20),(22,13),(40,20)],'#a1bd59')
    s.l([(5,21),(24,28),(42,20)],'#507e32')
    s.p([(6,20),(12,18),(15,20),(10,22)],'#83a84b')
    s.p([(28,25),(35,22),(39,22),(31,26)],'#83a84b')
    # Quarry cut: pale stone rim, dark wall and two readable steps.
    s.p([(15,20),(25,15),(36,20),(25,26)],'#3c4c40')
    s.p([(17,20),(25,16),(33,20),(25,24)],'#a3a594')
    s.p([(19,20),(25,17),(31,20),(25,23)],'#626f65')
    s.l([(20,20),(25,18),(29,20)],'#d0ceaf')
    s.p([(22,21),(25,20),(29,21),(25,23)],'#394d42')
    s.l([(24,21),(26,21)],'#b49c61')
    # Small oak: a connected canopy with three lit planes.
    s.p([(11,11),(14,10),(16,11),(16,19),(13,21),(11,19)],'#5b412b')
    s.r((12,12,13,18),'#b58b50');s.l([(14,13),(14,18)],'#7d5a35')
    s.p([(6,6),(13,2),(21,6),(21,12),(14,16),(6,12)],'#3c5d2e')
    s.p([(7,6),(13,3),(20,6),(14,9)],'#91b650')
    s.p([(7,7),(13,10),(13,14),(7,11)],'#6c963a')
    s.p([(14,10),(20,7),(20,11),(14,14)],'#4f7c33')
    s.l([(8,6),(13,4),(17,6)],'#b0cb6a')
    s.r((8,8,10,9),'#83ad44');s.l([(16,11),(18,10)],'#638f37')
    return s.im

def storage():
    s=Sprite()
    # Shaped barrel silhouette. Contours are wood-colored, one pixel wide.
    s.p([(13,12),(21,9),(31,10),(37,14),(40,23),(39,35),(36,41),(29,45),(19,44),(11,40),(8,32),(8,23)],'#543a28')
    s.p([(10,23),(13,17),(19,15),(28,15),(36,18),(38,24),(37,35),(34,40),(28,43),(19,42),(13,38),(10,31)],'#9e6b3d')
    s.p([(11,24),(14,19),(18,18),(17,38),(19,41),(14,38),(11,31)],'#c39357')
    s.p([(19,17),(24,17),(24,43),(20,42),(19,36)],'#b18047')
    s.p([(26,17),(32,17),(35,20),(35,38),(29,42),(26,43)],'#88582f')
    s.p([(36,21),(38,24),(37,34),(35,38)],'#70472b')
    # Staves and sparse, long wood-grain clusters.
    s.l([(17,18),(16,28),(17,39)],'#8d5a31')
    s.l([(25,18),(25,42)],'#75492a')
    s.l([(32,19),(33,30),(32,39)],'#6b4329')
    s.l([(12,26),(12,30),(13,32)],'#ddb175')
    s.l([(21,31),(21,37),(22,38)],'#c69454')
    s.l([(29,22),(29,26)],'#a9773e')
    # Two curved iron hoops with a consistent top-left highlight.
    for y in (21,34):
        s.p([(9,y),(14,y+3),(23,y+4),(33,y+2),(39,y-1),(39,y+3),(34,y+6),(24,y+8),(14,y+7),(9,y+4)],'#414d50')
        s.p([(10,y+1),(15,y+4),(23,y+5),(33,y+3),(38,y+1),(38,y+3),(33,y+5),(24,y+7),(15,y+6),(10,y+3)],'#8a9899')
        s.l([(11,y+1),(15,y+3),(23,y+4),(31,y+3)],'#d0d8d6')
        s.l([(34,y+3),(37,y+2)],'#a7b9b7')
        s.r((15,y+4,15,y+4),'#52666b');s.r((33,y+4,33,y+4),'#52666b')
    # Opening is a shallow oval, with resources emerging from it.
    s.p([(10,15),(14,11),(22,9),(31,10),(37,14),(37,18),(32,21),(23,23),(14,21),(10,18)],'#65462a')
    s.p([(12,15),(16,12),(23,11),(30,12),(35,15),(34,17),(29,19),(22,20),(15,18)],'#3e3c2d')
    s.l([(12,15),(16,12),(23,11),(30,12)],'#d0a16a')
    s.l([(12,18),(16,20),(23,22),(31,20),(35,18)],'#bd8d52')
    # Iron ingot on the left.
    s.p([(13,12),(18,7),(26,7),(29,10),(29,14),(24,17),(16,16),(13,14)],'#63766c')
    s.p([(15,12),(19,8),(25,8),(27,10),(23,13),(17,13)],'#dedfd8')
    s.p([(15,13),(18,15),(24,16),(28,13),(28,11),(24,14),(18,14)],'#a4b3a2')
    s.l([(19,9),(24,9)],'#f2eed9')
    # Single teal crystal: identifiable, restrained accent.
    s.p([(28,5),(34,5),(38,10),(36,16),(31,19),(26,14),(25,10)],'#376a64')
    s.p([(28,6),(33,6),(36,10),(31,12),(27,10)],'#7bd7c5')
    s.p([(27,11),(30,13),(30,17),(27,14)],'#39aa99')
    s.p([(32,13),(36,11),(35,15),(32,17)],'#247f7b')
    s.l([(29,7),(32,7)],'#b7f0da')
    return s.im

def drill():
    s=Sprite()
    # A compact vertical drill rig, matching its role over a quarry.
    # Back support and an isometric stone skid.
    s.p([(4,37),(25,30),(44,37),(44,41),(25,47),(4,41)],'#46524c')
    s.p([(5,37),(25,31),(42,37),(25,43)],'#9a9d8b')
    s.p([(5,38),(24,44),(24,46),(5,40)],'#727e70')
    s.p([(26,44),(43,38),(43,40),(26,45)],'#596a5e')
    s.l([(7,37),(24,32),(39,37)],'#c4c8ad')
    # Dark oak A-frame: kept narrow so the drill remains the focal point.
    s.p([(8,17),(11,16),(13,38),(9,40),(7,39)],'#5c4229')
    s.p([(9,18),(10,18),(12,37),(10,38)],'#b28b4d')
    s.p([(34,15),(37,16),(40,36),(36,38)],'#5c4229')
    s.p([(35,17),(36,18),(38,35),(36,36)],'#9b733e')
    s.p([(8,14),(27,8),(37,12),(37,17),(17,23),(8,19)],'#5d452d')
    s.p([(9,14),(27,9),(35,12),(17,18)],'#bd9453')
    s.p([(9,15),(17,19),(35,13),(35,16),(17,21),(9,18)],'#906a39')
    s.l([(11,14),(27,10),(32,12)],'#dfb975')
    # Copper motor block, compact and bevelled, on the crossbeam.
    s.p([(16,8),(26,4),(34,8),(34,19),(25,23),(16,19)],'#71462f')
    s.p([(17,8),(26,5),(32,8),(24,11)],'#e3af72')
    s.p([(17,9),(24,12),(24,21),(17,18)],'#bf7e49')
    s.p([(25,12),(33,9),(33,18),(25,21)],'#945632')
    s.l([(18,10),(18,16)],'#e2a66b')
    s.p([(19,12),(22,13),(22,16),(19,15)],'#5a593c')
    s.l([(20,13),(21,13)],'#a5c86b')
    s.l([(27,13),(31,11)],'#6a4630');s.l([(27,16),(31,14)],'#6a4630')
    # Exhaust cap.
    s.p([(27,3),(30,2),(32,3),(32,6),(29,8),(27,6)],'#46594f')
    s.l([(28,3),(30,3)],'#a0b2a0');s.l([(28,4),(28,6)],'#748a78')
    # Shaft, and a large three-flight silver auger.
    s.p([(22,21),(26,20),(28,22),(28,36),(24,42),(21,36)],'#4a6258')
    s.p([(23,22),(25,22),(25,36),(24,39),(23,35)],'#a6b9a6')
    s.p([(18,24),(25,21),(31,24),(31,27),(24,30),(18,27)],'#3d4b50')
    s.p([(19,24),(25,22),(30,24),(24,27)],'#e5e8e3')
    s.p([(19,25),(24,28),(30,25),(30,27),(24,29),(19,27)],'#8c9a9d')
    s.p([(18,30),(25,27),(31,30),(31,33),(24,36),(18,33)],'#3d4b50')
    s.p([(19,30),(25,28),(30,30),(24,33)],'#ced8d6')
    s.p([(19,31),(24,34),(30,31),(30,33),(24,35),(19,33)],'#7d8d93')
    s.p([(21,36),(25,33),(29,36),(25,41),(24,43)],'#3d4b50')
    s.p([(22,36),(25,34),(27,36),(24,40)],'#b8c9c8')
    s.l([(22,36),(24,37)],'#f4f4e8')
    return s.im

icons={'island':island(),'drill':drill(),'storage':storage()}
for n,im in icons.items():im.save(ROOT/'png'/f'{n}.png')

# Use the Minecraft bitmap font for the menu study; do not synthesize lettering.
glyphs={}
font_data=json.loads((Path(__file__).parent/'menu-font.json').read_text())
for ch,entry in font_data.items():
    g=Image.new('RGBA',(8,8))
    for y,row in enumerate(entry['rows']):
        for x,v in enumerate(row):
            if v=='1':g.putpixel((x,y),(255,255,255,255))
    glyphs[ch]=(g,entry['width'])
glyphs[' ']=(Image.new('RGBA',(3,8)),3)
def width(t):return sum(glyphs.get(c,glyphs['?'])[1]+1 for c in t)-1
def text(im,t,x,y,c='#383838',center=False):
    if center:x-=width(t)//2
    for ch in t:
        g,w=glyphs.get(ch,glyphs['?']);ink=Image.new('RGBA',g.size,c);ink.putalpha(g.getchannel('A'));im.alpha_composite(ink,(x,y));x+=w+1
def frame(im,box,fill='#c6c6c6'):
    x,y,x2,y2=box;d=ImageDraw.Draw(im);d.rectangle(box,fill='#202020');d.rectangle((x+1,y+1,x2-1,y2-1),fill=fill)
    d.line([(x+1,y2-1),(x+1,y+1),(x2-1,y+1)],fill='#f5f5f5');d.line([(x+2,y2-1),(x2-1,y2-1),(x2-1,y+2)],fill='#656565')

# Main study: icons are displayed at native 48×48, integer zoom only.
panel=Image.new('RGBA',(176,137));frame(panel,(0,24,175,136));frame(panel,(22,2,153,16));text(panel,'PRISONEVO',88,6,center=True)
text(panel,'Основные разделы',7,30,'#5a5a5a')
for x,name,label in [(7,'island','Остров'),(61,'drill','Бур'),(115,'storage','Склад')]:
    frame(panel,(x,42,x+53,113));panel.alpha_composite(icons[name],(x+3,46));text(panel,label,x+27,102,center=True)
text(panel,'Назад',8,122,'#626262');text(panel,'Закрыть',125,122,'#626262')
panel.resize((704,548),Image.Resampling.NEAREST).save(ROOT/'previews/menu.png')

def boardtext(im,t,x,y,color='#e6e7df',scale=2):
    label=Image.new('RGBA',(width(t)+1,8));text(label,t,0,0,color)
    im.alpha_composite(label.resize((label.width*scale,8*scale),Image.Resampling.NEAREST),(x,y))
board=Image.new('RGBA',(1120,670),'#242727');d=ImageDraw.Draw(board)
boardtext(board,'PRISONEVO',32,22,scale=3)
boardtext(board,'Три основные иконки',32,60,'#abb5aa')
for i,(n,label) in enumerate([('island','Остров'),('drill','Бур'),('storage','Хранилище')]):
    x=32+i*366;y=104
    tile=Image.new('RGBA',(324,324));frame(tile,(0,0,323,323));tile.alpha_composite(icons[n].resize((288,288),Image.Resampling.NEAREST),(18,18));board.paste(tile,(x,y),tile)
    boardtext(board,label,x,y+342,'#e4e5dc')
    # Native and 2× sizes are shown separately, on the actual vanilla gray.
    d.rectangle((x,y+394,x+323,y+510),fill='#c6c6c6')
    board.paste(icons[n],(x+23,y+426),icons[n]);board.paste(icons[n].resize((96,96),Image.Resampling.NEAREST),(x+116,y+404),icons[n].resize((96,96),Image.Resampling.NEAREST))
    boardtext(board,'48 x 48',x+24,y+514,'#aab3a9',1);boardtext(board,'x2',x+128,y+514,'#aab3a9',1)
board.convert('RGB').save(ROOT/'previews/three-icons.png')

atlas=Image.new('RGBA',(144,48))
for i,im in enumerate(icons.values()):atlas.alpha_composite(im,(i*48,0))
atlas.save(ROOT/'three-icons.png')
print('Three native 48×48 sprites and previews written.')
