#!/usr/bin/env python3
"""Create the original HYLOR pixel-art resources deterministically."""
from PIL import Image, ImageDraw, ImageFont
from zipfile import ZipFile, ZIP_DEFLATED
from pathlib import Path
from io import BytesIO
import json, sys
out = Path(sys.argv[1] if len(sys.argv)>1 else 'hylor-resourcepack.zip')
palette={'pink':'#f14582','light':'#ff9cc2','dark':'#711331','gold':'#ffd05c','shade':'#b84371','blue':'#71f3ff','white':'#fff0f6'}
def texture(pattern):
 im=Image.new('RGBA',(16,16)); p=im.load(); colors={'.':None,'P':palette['pink'],'L':palette['light'],'D':palette['dark'],'G':palette['gold'],'S':palette['shade'],'B':palette['blue'],'W':palette['white'],'K':'#29223c'}
 for y,line in enumerate(pattern):
  for x,v in enumerate(line):
   if v!='.':p[x,y]=tuple(bytes.fromhex(colors[v][1:]))+(255,)
 return im
def png(im):
 buf=BytesIO();im.save(buf,format='PNG',optimize=True);return buf.getvalue()
textures={
'nether_star': ['......LL........','.....LPPL.......','.....LPPPL......','L....LPPPL....L.','LL...LPPPL...LL.','.LLL.LPPPL.LLL..','..LLLPPPPPLLL...','...LPPPPPPPL....','LLLPPPPWPPPPLLL.','...LPPPPPPPL....','..LLLPPPPPLLL...','.LLL.LPPPL.LLL..','LL...LPPPL...LL.','L....LPPPL....L.','.....LPPPL......','......LLL.......'],
'emerald':['......LLL.......','....LLPPPLL.....','...LPPPPPPPL....','..LPPPLPPPPPL...','..LPPPLPPPPPL...','.LPPPPLPPPPPPL..','.LPPPLLLPPPPPL..','.LPPPPPPPPPPPL..','.LPPPPPPPPPPPL..','..LPPPPPPPPPL...','..LPPPPPPPPPL...','...LPPPPPPPL....','....LPPPPPL.....','.....LPPPL......','......LLL.......','................'],
'experience_bottle':['......GGG.......','.....GPPPG......','.....GPPPG......','......PPP.......','....LLPPPLL.....','...LPPPPPPPL....','..LPPPPPPPPPL...','..LPLPPPPPPPL...','..LPLPPPPPPPL...','..LPPPPPPPPPL...','..LPPPPLLPPPL...','..LPPPPPPPPPL...','...LPPPPPPPL....','....LLLLLLL.....','................','................'],
'hopper':['................','..LLLLLLLLLLL...','.LPPPPPPPPPPPL..','.LPPPPPPPPPPPL..','..LPPPPPPPPPL...','...LPPPPPPPL....','....LPPPPPL.....','.....LPPPL......','......LPL.......','......LPL.......','......LPL.......','.....LPPPL......','.....LPPPL......','.....LLLLL......','................','................'],
'diamond_pickaxe':['.....LLLLLL.....','...LLBBBBBBLL...','..LBBDDDDBBBBL..','.LBBL....LBBBL..','.LLL......LBBL..','...........LLL..','...........D....','..........DD....','.........DD.....','........DD......','.......DD.......','......DD........','.....DD.........','....DD..........','...DD...........','...D............'],
'paper':['..LLLLLLLLLL....','..LWWWWWWWWL....','..LWPPPPPPWL....','..LWWWWWWWWL....','..LWPPPPPPWL....','..LWWWWWWWWL....','..LWPPPPPPWL....','..LWWWWWWWWL....','..LWPPPPPPWL....','..LWWWWWWWWL....','..LWPPPPPPWL....','..LWWWWWWWWL....','..LWWWWWWWWL....','..LLLLLLLLLL....','................','................'],
}
icon=Image.new('RGB',(128,128),'#1a1224');d=ImageDraw.Draw(icon);d.rounded_rectangle((5,5,122,122),radius=18,fill='#33132d',outline='#f14582',width=5);d.polygon([(64,14),(74,43),(105,43),(80,63),(90,94),(64,77),(38,94),(48,63),(23,43),(54,43)],fill='#f14582',outline='#ff9cc2',width=3);d.rectangle((22,100,106,116),fill='#861e48');font=ImageFont.load_default(size=16);d.text((35,100),'HYLOR',font=font,fill='#fff0f6')
with ZipFile(out,'w',ZIP_DEFLATED) as z:
 z.writestr('pack.mcmeta',json.dumps({'pack':{'pack_format':97,'min_format':[97,0],'max_format':[97,1],'description':'HYLOR | Prison Evo — original pink pixel art'}},ensure_ascii=False))
 z.writestr('pack.png',png(icon))
 for name,pat in textures.items():z.writestr('assets/minecraft/textures/item/'+name+'.png',png(texture(pat)))
print('Created',out)
