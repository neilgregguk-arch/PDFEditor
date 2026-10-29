"""Development fixtures only. Application does not merge PDFs or add graphics."""
from pathlib import Path
import json,hashlib
from pypdf import PdfReader,PdfWriter
from pypdf.generic import NameObject,DecodedStreamObject
R=Path(__file__).resolve().parents[1];O=R/'run/document-corpus'
w=PdfWriter();w.append(PdfReader(O/'mixed.pdf'));w.append(PdfReader(O/'multi-natural.pdf'),pages=[0])
with (O/'mixed-multipage.pdf').open('wb') as f:w.write(f)
w=PdfWriter(clone_from=R/'run/corpus/11-word-letter.pdf');p=w.pages[0];st=DecodedStreamObject();st.set_data(p.get_contents().get_data()+b'\nq 0 0 0 rg 240 755 50 14 re f Q\n');p[NameObject('/Contents')]=w._add_object(st)
with (O/'word-horizontal-obstacle.pdf').open('wb') as f:w.write(f)
(R/'evidence/insertion-corpus.json').write_text(json.dumps(dict(developmentOnly=True,ownershipHints=False,description='Unmodified genuine Word page plus separate natural page; Word page with protected vector obstacle outside original title.',hashes={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in O.glob('*.pdf')}),indent=2),encoding='utf-8')
