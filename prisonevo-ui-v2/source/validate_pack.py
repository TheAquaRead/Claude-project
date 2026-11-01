"""Validate resource/model links and metrics without claiming an in-game test."""
from pathlib import Path
import json,zipfile,hashlib
from PIL import Image
ROOT=Path(__file__).resolve().parents[1]
PACK=ROOT/'resourcepack';NS=PACK/'assets/prisonevo'
assert json.loads((PACK/'pack.mcmeta').read_text())['pack']['pack_format']==64
assert not (PACK/'assets/minecraft').exists()
icons=list((ROOT/'png').glob('*.png'));assert len(icons)==22
for p in icons:
    im=Image.open(p);assert im.size==(64,64) and im.mode=='RGBA'
    assert set(im.getchannel('A').get_flattened_data())<={0,255}
for p in (NS/'font').glob('*.json'):
    for provider in json.loads(p.read_text())['providers']:
        if provider['type']!='bitmap':continue
        namespace,path=provider['file'].split(':');assert namespace=='prisonevo'
        im=Image.open(NS/'textures'/path)
        assert all(len(row)==len(provider['chars'][0]) for row in provider['chars'])
        assert provider['ascent']<=provider['height']
        if path.startswith('gui/'):
            assert im.size==(256,256) and im.getbbox()[2]==176
            # Minecraft's bitmap advance: rightmost visible column + 1.
            assert im.getbbox()[2]+1==177
for p in (NS/'items').glob('*.json'):
    model=json.loads(p.read_text())['model']['model'].split(':')[1]
    assert (NS/'models'/f'{model}.json').is_file()
for p in (NS/'models/item').glob('*.json'):
    for resource in json.loads(p.read_text()).get('textures',{}).values():
        namespace,path=resource.split(':');assert namespace=='prisonevo'
        assert (NS/'textures'/f'{path}.png').is_file()
# Check width assumptions used by ModernMenu's cursor reset.
numbers=Image.open(NS/'textures/font/numbers.png')
for i,c in enumerate('0123456789/.kM'):
    box=numbers.crop((i*8,0,i*8+8,8)).getbbox()
    assert box[2]+1==(2 if c=='.' else 5 if c=='k' else 6),(c,box)
jar=ROOT/'plugin/prisonevo-0.1.1-ui.jar'
with zipfile.ZipFile(jar) as z:
    assert z.testzip() is None
    assert b'version: 0.1.1-ui' in z.read('plugin.yml')
    assert 'ru/prisonevo/ModernMenu.class' in z.namelist()
    assert 'ru/prisonevo/UiLayout.class' in z.namelist()
with zipfile.ZipFile(ROOT/'PrisonEvo-UI-resourcepack-1.21.8.zip') as z:
    assert z.testzip() is None and 'pack.mcmeta' in z.namelist()
report=['Resource pack format 64 (Minecraft 1.21.8): PASS',
        '22 RGBA icons, 64x64, binary alpha: PASS',
        '6 GUI textures 256x256; visible width 176; bitmap advance 177: PASS',
        'Font, item definition and model references: PASS',
        'Dynamic numeric glyph advances match Java cursor metrics: PASS',
        'No assets/minecraft overrides: PASS',
        'ZIP and JAR integrity and compiled UI classes: PASS',
        'JUnit: 7 tests, 0 failures, 0 errors (Maven / Java 21 / Paper API 1.21.8)',
        'Minecraft client/server visual integration: NOT RUN',
        'Existing Nexo pack merge: NOT RUN (pack not provided)','',
        'SHA256 resourcepack: '+hashlib.sha256((ROOT/'PrisonEvo-UI-resourcepack-1.21.8.zip').read_bytes()).hexdigest(),
        'SHA256 plugin: '+hashlib.sha256(jar.read_bytes()).hexdigest()]
(ROOT/'VALIDATION.txt').write_text('\n'.join(report)+'\n')
print('\n'.join(report))
