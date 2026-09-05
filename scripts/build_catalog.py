#!/usr/bin/env python3
"""Generate the static website and CSV from catalog/artworks.json.

Standard library only. --check verifies the committed output is current.
--exports DIR also creates a local SQLite snapshot and a private photo review.
"""
import argparse
import csv
import html
import io
import json
import os
import re
import shutil
import sqlite3
import tempfile
from datetime import date
from collections import Counter
from pathlib import Path
from urllib.parse import quote

ROOT = Path(__file__).resolve().parents[1]
ORIGIN = 'https://artelle.xyz'
LABELS = {'landscape':'Landscapes','botanical':'Nature','still-life':'Still life','abstract':'Abstracts'}
CSV_FIELDS = ['id','artist','title','title_status','medium','support','height_in','width_in','height_cm','width_cm','year','availability','price','currency','front_photo','reverse_photo','reverse_inscription','review_flags','artwork_url']
PUBLIC_CSV_FIELDS = ['id','artist','title','medium','support','height_in','width_in','height_cm','width_cm','year','artwork_url']


def esc(value):
    return html.escape(str(value),quote=True)


def number(value):
    return f'{value:g}'


def size_text(artwork, units='in'):
    dims = artwork['dimensions']
    if not dims:
        return ''
    factor = 2.54 if units == 'cm' else 1
    return f"{number(round(dims['height']*factor,2))} × {number(round(dims['width']*factor,2))} {units}"


def medium_text(artwork):
    return artwork['medium']+' on paper' if artwork['medium'] else 'Work on paper'


def metadata(artwork):
    return ' · '.join(str(x) for x in [medium_text(artwork),size_text(artwork),artwork['year']] if x)


def artwork_url(artwork):
    return 'work/'+artwork['id'].lower()+'.html'


def image_tag(artwork, base='', thumbnail=False, eager=False):
    img = artwork['image']
    path = img['thumbnail'] if thumbnail else img['path']
    width = img['thumbnail_width'] if thumbnail else img['width']
    height = img['thumbnail_height'] if thumbnail else img['height']
    loading = 'fetchpriority="high"' if eager else 'loading="lazy"'
    return f'<img src="{base}{esc(path)}" alt="{esc(img["alt"])}" width="{width}" height="{height}" {loading} decoding="async">'


def card(artwork):
    return f'''<a class="work" href="{artwork_url(artwork)}" data-id="{artwork['id']}" data-title="{esc(artwork['title'])}" data-meta="{esc(metadata(artwork))}" data-image="{esc(artwork['image']['path'])}" data-cats="{artwork['category']}">
  <figure><div class="plate">{image_tag(artwork,thumbnail=True)}</div>
    <figcaption class="cap"><div><div class="title">{esc(artwork['title'])}</div><div class="meta">{esc(medium_text(artwork))}</div><div class="meta">{esc(' · '.join(str(x) for x in [size_text(artwork),artwork['year']] if x))}</div></div></figcaption>
  </figure></a>'''


LIGHTBOX = '''<div class="lb" id="lightbox" role="dialog" aria-modal="true" aria-label="Artwork viewer" aria-hidden="true">
  <button class="lb-btn lb-x" aria-label="Close">&times;</button>
  <button class="lb-btn lb-prev" aria-label="Previous work">&lsaquo;</button>
  <button class="lb-btn lb-next" aria-label="Next work">&rsaquo;</button>
  <figure class="lb-figure"><div class="lb-frame"></div><figcaption class="lb-cap"><span class="lb-title"></span><span class="lb-meta"></span><a class="lb-detail" href="works.html">View artwork details</a></figcaption></figure>
</div>'''


def page(title,description,body,path,active='works',lightbox=False,og=None,structured=None):
    base = '../' if path.startswith('work/') else ''
    nav = []
    for key,label,target in [('works','Works','works.html'),('editions','Collecting','editions.html'),('about','About','about.html'),('contact','Contact','contact.html')]:
        current = ' aria-current="page"' if key == active else ''
        nav.append(f'<a href="{base}{target}"{current}>{label}</a>')
    values = {'TITLE':esc(title),'DESCRIPTION':esc(description),'CANONICAL':ORIGIN+('/' if path=='index.html' else '/'+path),
              'OG_IMAGE':ORIGIN+'/'+(og or 'assets/img/og.jpg'),'BASE':base,'BODY':body,'NAV':'\n'.join(nav),
              'LIGHTBOX':LIGHTBOX if lightbox else '',
              'STRUCTURED_DATA':'<script type="application/ld+json">'+json.dumps(structured,ensure_ascii=False).replace('<','\\u003c')+'</script>' if structured else ''}
    result = (ROOT/'templates/page.html').read_text()
    for key,value in values.items():
        result = result.replace('{{'+key+'}}',value)
    if re.search(r'\{\{[A-Z_]+\}\}',result):
        raise ValueError('Unresolved template token')
    return result


def validate(data,import_data):
    artworks = data['artworks']
    ids,images,titles = set(),set(),set()
    source_map = {}
    for a in artworks:
        ident = a['id']
        if not re.fullmatch(r'AQ-\d{4}',ident) or ident in ids:
            raise ValueError('Invalid or duplicate artwork ID: '+ident)
        if a['title'] in titles or not a['title'].strip():
            raise ValueError('Duplicate or empty title: '+a['title'])
        if a['image']['path'] in images:
            raise ValueError('Two artwork records use the same photograph')
        ids.add(ident); images.add(a['image']['path']); titles.add(a['title'])
        if a['artist'] != data['artist'] or a['category'] not in LABELS:
            raise ValueError('Invalid artist or category: '+ident)
        if a['year'] is not None and not (1900 <= a['year'] <= date.today().year):
            raise ValueError('Invalid year: '+ident)
        if a['dimensions']:
            dims = a['dimensions']
            if dims['unit'] != 'in' or min(dims['height'],dims['width']) <= 0:
                raise ValueError('Invalid dimensions: '+ident)
            if not a['source_photos']['reverse']:
                raise ValueError('Dimensions require photographic evidence: '+ident)
        if a['medium'] and not a['source_photos']['reverse']:
            raise ValueError('Confirmed medium requires photographic evidence: '+ident)
        for key in ['path','thumbnail']:
            path = ROOT/a['image'][key]
            if not path.is_file() or ROOT not in path.resolve().parents:
                raise ValueError('Missing or invalid image: '+str(path))
        for role in ['front','reverse','additional_reverse']:
            photos = a['source_photos'][role]
            if not isinstance(photos,list):photos=[photos] if photos else []
            for photo in photos:
                if photo in source_map:
                    raise ValueError('Photo assigned twice: '+photo)
                source_map[photo]=(ident,role)
    manifest = import_data['photos']
    if len(manifest) != import_data['photo_count'] or len({p['filename'] for p in manifest}) != len(manifest):
        raise ValueError('Invalid photo manifest count')
    for p in manifest:
        if source_map.get(p['filename']) != (p['artwork_id'],p['role']):
            raise ValueError('Catalog/import mapping mismatch: '+p['filename'])
        if not re.fullmatch('[a-f0-9]{64}',p['sha256']):raise ValueError('Invalid source digest')
    if set(source_map) != {p['filename'] for p in manifest}:
        raise ValueError('Unaccounted source photograph')
    counts=Counter(p['role'] for p in manifest)
    for role in ['front','reverse','additional_reverse']:
        if counts[role] != import_data[role+'_count']:raise ValueError('Photo role count mismatch')


def csv_rows(artworks):
    for a in artworks:
        dims=a['dimensions'] or {}
        yield {'id':a['id'],'artist':a['artist'],'title':a['title'],'title_status':a['title_status'],
               'medium':a['medium'],'support':a['support'],'height_in':dims.get('height'),'width_in':dims.get('width'),
               'height_cm':round(dims['height']*2.54,2) if dims else '', 'width_cm':round(dims['width']*2.54,2) if dims else '',
               'year':a['year'],'availability':a['availability'],'price':a['price'],'currency':a['currency'],
               'front_photo':a['source_photos']['front'],'reverse_photo':a['source_photos']['reverse'],
               'reverse_inscription':a['reverse_inscription'],'review_flags':'; '.join(a['review_flags']),
               'artwork_url':ORIGIN+'/'+artwork_url(a)}


def generate(data):
    artworks=data['artworks']; by_id={a['id']:a for a in artworks}; count=len(artworks)
    outputs={}
    filters='<button class="chip" type="button" data-filter="all" aria-pressed="true">All works</button>'
    filters+=''.join(f'<button class="chip" type="button" data-filter="{key}" aria-pressed="false">{label}</button>' for key,label in LABELS.items())
    body=f'''<section class="section catalog-section"><div class="wrap">
      <p class="eyebrow">Anisa Quraishi</p><div class="section-head"><div><h1>Works</h1><p class="catalog-intro">Landscapes, still life, nature and abstraction.</p></div><a class="text-link" href="catalog.html">View catalog table</a></div>
      <div class="catalog-tools"><div class="filters" aria-label="Filter artworks">{filters}</div><p class="result-count" aria-live="polite"><span id="work-count">{count}</span> works</p></div>
      <div class="works">{''.join(card(a) for a in artworks)}</div>
    </div></section>'''
    outputs['works.html']=page('Works by Anisa Quraishi — Artelle',f'Explore {count} artworks by Anisa Quraishi: landscapes, botanical studies, still life and abstract compositions.',body,'works.html',lightbox=True)
    hero=by_id['AQ-0001']
    selected=[by_id[k] for k in ['AQ-0002','AQ-0021','AQ-0003','AQ-0004','AQ-0023','AQ-0018']]
    body=f'''<section class="hero"><div class="wrap"><div class="hero-copy"><p class="eyebrow">Art by Anisa Quraishi</p><h1>A world<br>on paper.</h1><p class="lede">Landscapes, still life, flowers and abstract forms. Original works by an artist based in Pakistan.</p><div class="actions"><a class="btn" href="works.html">Explore the works</a><a class="btn-ghost" href="about.html">Meet the artist</a></div></div><a class="hero-art" href="{artwork_url(hero)}" aria-label="View Minaret"><div class="plate natural">{image_tag(hero,eager=True)}</div></a></div></section>
      <section class="section"><div class="wrap"><div class="section-head"><h2>Selected works</h2><a class="text-link" href="works.html">View all {count} works</a></div><div class="works">{''.join(card(a) for a in selected)}</div></div></section>
      <section class="band"><div class="wrap band-in"><p class="eyebrow">From the studio</p><h2>A work to live with.</h2><p class="catalog-intro">For prices, availability and delivery enquiries, get in touch with the studio.</p><div class="actions"><a class="btn-ghost" href="editions.html">Collecting a work</a></div></div></section>'''
    outputs['index.html']=page('Artelle — Art by Anisa Quraishi','Original artworks by Anisa Quraishi, an artist based in Pakistan. Explore landscapes, still life, botanical studies and abstract compositions.',body,'index.html',active='',lightbox=True,structured={'@context':'https://schema.org','@type':'WebSite','name':'Artelle','url':ORIGIN,'about':{'@type':'Person','name':'Anisa Quraishi'}})
    table_rows=''.join(f'''<tr data-search="{esc((a['id']+' '+a['title']+' '+(a['medium'] or '')+' '+a['category']+' '+str(a['year'] or '')).lower())}"><td class="inventory-id">{a['id']}</td><td><a class="table-art" href="{artwork_url(a)}">{image_tag(a,thumbnail=True)}<span>{esc(a['title'])}</span></a></td><td>{esc(medium_text(a)) if a['medium'] else 'To confirm'}</td><td class="dimension-cell">{esc(size_text(a)) if a['dimensions'] else 'To confirm'}<small>{esc(size_text(a,'cm'))}</small></td><td>{a['year'] or '—'}</td></tr>''' for a in artworks)
    body=f'''<section class="section catalog-section"><div class="wrap"><p class="eyebrow">Anisa Quraishi</p><div class="section-head"><div><h1>Catalog</h1><p class="catalog-intro">{count} original artworks. Dimensions are height × width.</p></div><a class="btn-ghost" href="catalog/artworks.csv" download>Download spreadsheet</a></div><div class="table-tools"><label for="catalog-search">Find a work<input type="search" id="catalog-search" placeholder="Title, medium, year or reference" autocomplete="off"></label><a class="text-link" href="works.html">Back to gallery</a></div><p class="result-count" aria-live="polite"><span id="table-count">{count}</span> works</p><div class="table-scroll" tabindex="0" role="region" aria-label="Artwork catalog"><table class="catalog-table"><caption class="sr-only">Artworks by Anisa Quraishi</caption><thead><tr><th scope="col">Reference</th><th scope="col">Artwork</th><th scope="col">Medium</th><th scope="col">Size</th><th scope="col">Year</th></tr></thead><tbody>{table_rows}</tbody></table></div><p class="catalog-note">Sizes are transcribed from the artist’s notes; sheet and image-area measurements will be confirmed for a purchase. Prices and availability are available by enquiry.</p></div></section>'''
    outputs['catalog.html']=page('Artwork catalog — Anisa Quraishi — Artelle','A table of artworks by Anisa Quraishi, with medium, dimensions and year where recorded.',body,'catalog.html')
    for a in artworks:
        facts=[('Artist',a['artist']),('Medium',medium_text(a) if a['medium'] else 'To be confirmed')]
        if a['dimensions']:facts.append(('Dimensions',size_text(a)+' / '+size_text(a,'cm')+' (H × W)'))
        if a['year']:facts.append(('Year',str(a['year'])))
        facts.append(('Reference',a['id']))
        detail=''.join(f'<div><dt>{esc(key)}</dt><dd>{esc(value)}</dd></div>' for key,value in facts)
        subject=quote('Artwork enquiry: '+a['title']+' ('+a['id']+')')
        body=f'''<section class="section catalog-section"><div class="wrap"><a class="text-link back-link" href="../works.html">← All works</a><div class="artwork-layout"><div class="plate natural artwork-image">{image_tag(a,base='../',eager=True)}</div><div class="artwork-copy"><p class="eyebrow">Anisa Quraishi</p><h1>{esc(a['title'])}</h1><p class="artwork-description">{esc(a['description'])}</p><dl class="artwork-facts">{detail}</dl><div class="actions"><a class="btn" href="mailto:hello@artelle.xyz?subject={subject}">Enquire about this work</a></div><p class="catalog-note">Contact the studio for price, availability and delivery details.</p></div></div></div></section>'''
        structured={'@context':'https://schema.org','@type':'VisualArtwork','@id':ORIGIN+'/'+artwork_url(a),'name':a['title'],'identifier':a['id'],'creator':{'@type':'Person','name':a['artist']},'image':ORIGIN+'/'+a['image']['path'],'description':a['description'],'artworkSurface':'Paper'}
        if a['medium']:structured['artMedium']=a['medium']
        if a['dimensions']:
            for key in ['height','width']:structured[key]={'@type':'QuantitativeValue','value':a['dimensions'][key],'unitCode':'INH'}
        outputs[artwork_url(a)]=page(a['title']+' — Anisa Quraishi — Artelle',a['description'],body,artwork_url(a),og=a['image']['path'],structured=structured)
    body=f'''<section class="section catalog-section"><div class="wrap split"><div class="plate natural">{image_tag(by_id['AQ-0019'],eager=True)}</div><div><p class="eyebrow">The artist</p><h1>Anisa Quraishi</h1><p class="artwork-description">Anisa Quraishi is an artist based in Pakistan. Her work spans landscapes, still life, botanical studies and abstraction, with works in watercolour, pastel and mixed media.</p><p class="catalog-intro">Artelle brings these works together in one place. The catalog includes quiet studies of leaves and flowers, domestic objects, and experiments in colour and shape.</p><div class="actions"><a class="btn" href="works.html">Explore the works</a><a class="btn-ghost" href="contact.html">Contact the studio</a></div></div></div></section>'''
    outputs['about.html']=page('Anisa Quraishi — About the artist — Artelle','Meet Anisa Quraishi, an artist based in Pakistan working in watercolour, pastel and mixed media.',body,'about.html',active='about')
    body='''<section class="section catalog-section"><div class="narrow"><p class="eyebrow">Collecting</p><h1>Bring a work home.</h1><p class="lede catalog-intro">For an original artwork, start with an enquiry to the studio. Each piece has its own reference in the catalog.</p><ol class="steps"><li><div><strong>Choose a work.</strong><p>Browse the gallery and open the artwork page for its medium, dimensions and year where recorded.</p></div></li><li><div><strong>Contact the studio.</strong><p>Include the title or reference, your country and delivery postcode. We will confirm availability, price and presentation.</p></div></li><li><div><strong>Confirm the details.</strong><p>Payment, packing and delivery arrangements are agreed before a purchase.</p></div></li></ol><div class="actions"><a class="btn" href="works.html">Browse works</a><a class="btn-ghost" href="contact.html">Contact the studio</a></div></div></section>'''
    outputs['editions.html']=page('Collecting an artwork — Artelle','Enquire about original artworks by Anisa Quraishi, including prices, availability and delivery.',body,'editions.html',active='editions')
    body='''<section class="section catalog-section"><div class="narrow"><p class="eyebrow">Artelle · Anisa Quraishi</p><h1>Contact the studio.</h1><p class="lede catalog-intro">For artwork enquiries, prices and availability, email the studio.</p><ul class="contact-list"><li><span class="k">Email</span><a class="v" href="mailto:hello@artelle.xyz?subject=Artwork%20enquiry">hello@artelle.xyz</a></li><li><span class="k">Artist</span><span class="v">Anisa Quraishi</span></li><li><span class="k">Based in</span><span class="v">Pakistan</span></li></ul><p class="catalog-note">Please include the artwork title or reference and your delivery country and postcode.</p></div></section>'''
    outputs['contact.html']=page('Contact — Artelle','Contact the studio of Anisa Quraishi for artwork enquiries, prices and availability.',body,'contact.html',active='contact')
    buffer=io.StringIO(newline='');writer=csv.DictWriter(buffer,fieldnames=PUBLIC_CSV_FIELDS,extrasaction='ignore');writer.writeheader();writer.writerows(csv_rows(artworks))
    outputs['catalog/artworks.csv']='\ufeff'+buffer.getvalue()
    locations=['index.html','works.html','catalog.html','about.html','editions.html','contact.html']+[artwork_url(a) for a in artworks]
    outputs['sitemap.xml']='<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'+''.join('<url><loc>'+ORIGIN+('/' if path=='index.html' else '/'+path)+'</loc></url>\n' for path in locations)+'</urlset>\n'
    outputs['robots.txt']='User-agent: *\nAllow: /\n\nSitemap: '+ORIGIN+'/sitemap.xml\n'
    return outputs


def local_exports(destination,archive,data,import_data):
    destination=destination.expanduser().resolve()
    if destination == ROOT or ROOT in destination.parents:
        raise ValueError('Private exports must be outside the public repository')
    destination.mkdir(parents=True,exist_ok=True)
    buffer=io.StringIO(newline='');writer=csv.DictWriter(buffer,fieldnames=CSV_FIELDS);writer.writeheader();writer.writerows(csv_rows(data['artworks']))
    (destination/'artworks.csv').write_bytes(('\ufeff'+buffer.getvalue()).encode('utf-8'))
    shutil.copyfile(ROOT/'catalog/artworks.json',destination/'artworks.json')
    fd,temp_path=tempfile.mkstemp(prefix='artelle-',suffix='.sqlite',dir=destination)
    os.close(fd)
    db=sqlite3.connect(temp_path)
    db.execute('PRAGMA foreign_keys=ON')
    defs=[]
    for field in CSV_FIELDS:
        dtype='INTEGER' if field=='year' else ('REAL' if field in ['height_in','width_in','height_cm','width_cm','price'] else 'TEXT')
        defs.append('"'+field+'" '+dtype+(' PRIMARY KEY' if field=='id' else ''))
    db.execute('CREATE TABLE artworks ('+', '.join(defs)+')')
    db.executemany('INSERT INTO artworks VALUES ('+','.join('?' for _ in CSV_FIELDS)+')',[[r[k] if r[k]!='' else None for k in CSV_FIELDS] for r in csv_rows(data['artworks'])])
    db.execute('CREATE TABLE photos (filename TEXT PRIMARY KEY, artwork_id TEXT NOT NULL REFERENCES artworks(id), role TEXT NOT NULL, sha256 TEXT NOT NULL)')
    db.executemany('INSERT INTO photos VALUES (?,?,?,?)',[(p['filename'],p['artwork_id'],p['role'],p['sha256']) for p in import_data['photos']])
    db.commit()
    if db.execute('PRAGMA integrity_check').fetchone()[0]!='ok':raise ValueError('SQLite integrity check failed')
    if db.execute('PRAGMA foreign_key_check').fetchall():raise ValueError('Invalid photo foreign key')
    db.close();os.replace(temp_path,destination/'artelle.sqlite')
    cards=[]
    for a in data['artworks']:
        photos=[]
        for role in ['front','reverse']:
            filename=a['source_photos'][role]
            if archive and filename:
                path=archive/'review'/(Path(filename).stem+'.jpg')
                if not path.is_file():raise ValueError('Missing review photograph: '+str(path))
                url=quote(os.path.relpath(path,destination))
                photos.append(f'<figure><a href="{url}"><img src="{url}" alt="{role} photograph for {a["id"]}" loading="lazy"></a><figcaption>{role}: {filename}</figcaption></figure>')
        if not photos:
            url=quote(os.path.relpath(ROOT/a['image']['path'],destination))
            photos=[f'<figure><img src="{url}" alt="{esc(a["title"])}" loading="lazy"><figcaption>Existing website photograph</figcaption></figure>']
        flags=', '.join(a['review_flags']) or 'No transcription gaps'
        cards.append(f'<article id="{a["id"]}"><h2>{a["id"]} · {esc(a["title"])}</h2><p>{esc(metadata(a))}</p><div class="photos">{"".join(photos)}</div><p><b>Reverse:</b> {esc(a["reverse_inscription"] or "Not supplied")}</p><p><b>Review:</b> {esc(flags)}</p><p>{esc(" ".join(a["catalog_notes"]))}</p></article>')
    report='''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Artelle — photo matching and catalog review</title><style>body{font:16px/1.55 system-ui;background:#f4f1e9;color:#1c1712;margin:36px auto;padding:0 24px;max-width:1100px}h1,h2{font-family:Georgia,serif}article{padding:32px 0;border-top:1px solid #ccc}.photos{display:flex;gap:20px;flex-wrap:wrap}figure{margin:0}img{max-width:100%;width:auto;height:330px;object-fit:contain}figcaption{font-size:13px}p{max-width:90ch}</style><h1>Anisa Quraishi — catalog review</h1><p>34 artworks: 31 uploaded fronts, 30 matching reverses, one extra reverse view, and three retained works from the earlier catalog. The usual sequence is reverse, then front. Titles are proposals. Prices, availability and framing remain unconfirmed.</p><p>Local archive and review only. The public site receives cropped front images and public catalog metadata. Artwork is not reconstructed where hands cover the photograph. The SQLite file is a generated snapshot; catalog/artworks.json in the repository is the editable master.</p><p><a href="artworks.csv">Spreadsheet</a> · <a href="artelle.sqlite">SQLite snapshot</a></p>'''+''.join(cards)+'</html>\n'
    (destination/'review.html').write_text(report)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check',action='store_true')
    parser.add_argument('--exports',type=Path)
    parser.add_argument('--archive',type=Path)
    args=parser.parse_args()
    data=json.loads((ROOT/'catalog/artworks.json').read_text())
    import_data=json.loads((ROOT/'catalog/imports/2026-09-06.json').read_text())
    validate(data,import_data)
    outputs=generate(data)
    stale=[]
    for name,content in outputs.items():
        path=ROOT/name
        if args.check:
            if not path.exists() or path.read_bytes()!=content.encode('utf-8'):stale.append(name)
        else:
            path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(content.encode('utf-8'))
    if stale:raise SystemExit('Generated files need rebuilding: '+', '.join(stale))
    if args.exports:
        if args.check:raise SystemExit('--exports cannot be combined with --check')
        local_exports(args.exports,args.archive,data,import_data)
    print(f"{'Verified' if args.check else 'Generated'} {len(data['artworks'])} artworks, {len(import_data['photos'])} photo mappings and {len(outputs)} public files.")
    print('Catalog gaps:',dict(Counter(flag for a in data['artworks'] for flag in a['review_flags'])))


if __name__=='__main__':
    main()
