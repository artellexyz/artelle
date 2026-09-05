#!/usr/bin/env python3
"""Prepare authentic web photographs from the private archive. Requires Pillow.

No generated painting, colour enhancement, or removal of hands. Original HEICs
and full reverse photographs stay outside the public repository.
"""
import argparse
import io
import json
import math
from pathlib import Path
from PIL import Image, ImageCms, ImageOps

ROOT = Path(__file__).resolve().parents[1]


def srgb(image):
    icc = image.info.get('icc_profile')
    image = ImageOps.exif_transpose(image).convert('RGB')
    if icc:
        image = ImageCms.profileToProfile(
            image, ImageCms.ImageCmsProfile(io.BytesIO(icc)),
            ImageCms.createProfile('sRGB'), outputMode='RGB')
    return image


def coefficients(destination, source):
    """Solve the inverse projective mapping without a numerical dependency."""
    rows = []
    for (x, y), (u, v) in zip(destination, source):
        rows.extend(([x,y,1,0,0,0,-u*x,-u*y,u],
                     [0,0,0,x,y,1,-v*x,-v*y,v]))
    for i in range(8):
        pivot = max(range(i, 8), key=lambda j: abs(rows[j][i]))
        rows[i], rows[pivot] = rows[pivot], rows[i]
        divisor = rows[i][i]
        if abs(divisor) < 1e-10:
            raise ValueError('Degenerate crop quadrilateral')
        rows[i] = [value / divisor for value in rows[i]]
        for j in range(8):
            if i != j:
                factor = rows[j][i]
                rows[j] = [a-factor*b for a,b in zip(rows[j], rows[i])]
    return [row[-1] for row in rows]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--archive', type=Path, required=True)
    args = parser.parse_args()
    catalog_path = ROOT/'catalog/artworks.json'
    catalog = json.loads(catalog_path.read_text())
    recipe = json.loads((ROOT/'catalog/imports/2026-09-06-crops.json').read_text())
    ref_w, ref_h = recipe['reference_size']
    thumb_dir = ROOT/'assets/art/thumbs'
    thumb_dir.mkdir(parents=True, exist_ok=True)
    for artwork in catalog['artworks']:
        path = ROOT/artwork['image']['path']
        if artwork['id'] in recipe['crops']:
            filename = Path(artwork['source_photos']['front']).stem+'.jpg'
            with Image.open(args.archive/'review'/filename) as original:
                image = srgb(original)
            points = [(x*image.width/ref_w,y*image.height/ref_h)
                      for x,y in recipe['crops'][artwork['id']]]
            tl,tr,br,bl = points
            width = (math.dist(tl,tr)+math.dist(bl,br))/2
            height = (math.dist(tl,bl)+math.dist(tr,br))/2
            scale = min(1,2000/max(width,height))
            width,height = round(width*scale),round(height*scale)
            destination = [(0,0),(width,0),(width,height),(0,height)]
            image = image.transform((width,height),Image.Transform.PERSPECTIVE,
                                    coefficients(destination,points),Image.Resampling.BICUBIC)
            rotation = recipe.get('rotation_degrees',{}).get(artwork['id'],0)
            if rotation:
                image = image.rotate(rotation,expand=True)
            image.save(path,quality=92,optimize=True,progressive=True)
        with Image.open(path) as original:
            image = srgb(original)
        artwork['image']['width'],artwork['image']['height'] = image.size
        image.thumbnail((640,900),Image.Resampling.LANCZOS)
        thumb = thumb_dir/(artwork['id'].lower()+'.jpg')
        image.save(thumb,quality=85,optimize=True,progressive=True)
        artwork['image']['thumbnail'] = thumb.relative_to(ROOT).as_posix()
        artwork['image']['thumbnail_width'],artwork['image']['thumbnail_height'] = image.size
    catalog_path.write_text(json.dumps(catalog,ensure_ascii=False,indent=2)+'\n')
    print(f"Prepared {len(recipe['crops'])} artwork photographs and {len(catalog['artworks'])} thumbnails.")


if __name__ == '__main__':
    main()
