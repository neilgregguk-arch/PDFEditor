"""Build-time only. No Python or fontTools is part of the Windows runtime."""
from pathlib import Path
import shutil,sys,hashlib,json
from fontTools import subset
import pypdfium2_raw
root=Path(__file__).resolve().parents[1]; target=root/'runtime'; assets=target/'assets'; assets.mkdir(parents=True,exist_ok=True)
if not (assets/'PrototypeSansAscii.ttf').exists():
    font=subset.load_font(str(root.parent/'assets/Vera.ttf'),subset.Options())
    font.recalcTimestamp=False
    subsetter=subset.Subsetter();subsetter.populate(unicodes=range(32,127));subsetter.subset(font)
    names={1:'Prototype Sans',2:'Regular',3:'PrototypeSans-Regular-ASCII-Phase2',4:'Prototype Sans Regular',6:'PrototypeSans-Regular',16:'Prototype Sans',17:'Regular'}
    for record in font['name'].names:
        if record.nameID in names:record.string=names[record.nameID].encode(record.getEncoding())
    font.save(str(assets/'PrototypeSansAscii.ttf'))
shutil.copyfile(root.parent/'assets/bitstream-vera-license.txt',assets/'FONT-LICENSE.txt')
package=Path(pypdfium2_raw.__file__).parent;shutil.copyfile(package/'pdfium.dll',target/'pdfium.dll')
dist=package.parent/'pypdfium2-5.14.0.dist-info/licenses/data/windows_x64/BUILD_LICENSES'
shutil.copytree(dist,target/'licenses/PDFium',dirs_exist_ok=True)
(target/'native-version.json').write_text(json.dumps({'pdfium':'156.0.8076.0','source_wheel':'pypdfium2 5.14.0 Windows x64','sha256':hashlib.sha256((target/'pdfium.dll').read_bytes()).hexdigest(),'font_sha256':hashlib.sha256((assets/'PrototypeSansAscii.ttf').read_bytes()).hexdigest(),'font':'Prototype Sans, renamed ASCII subset derived from Bitstream Vera; license retained'},indent=2))
print('Prepared native PDFium, ASCII font subset and license texts.')
