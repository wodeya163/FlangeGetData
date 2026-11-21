# -*- coding: utf-8 -*-
"""Minimal PyInstaller CArchive/PYZ extractor (no external deps).

Usage (must run on the same Python minor version as the target):
    python pyi_extract.py <exe> <outdir>
"""
import struct, os, sys, zlib, marshal

MAGIC = b'MEI\x0c\x0b\x0a\x0b\x0e'


def read_archive(exe):
    data = open(exe, 'rb').read()
    pos = data.rfind(MAGIC)
    if pos < 0:
        raise SystemExit('not a PyInstaller archive')
    pkg_len, toc_off, toc_len, pyver, pylib = struct.unpack('!IIII64s', data[pos+8:pos+88])
    pkg_start = pos + 88 - pkg_len
    toc = data[pkg_start+toc_off:pkg_start+toc_off+toc_len]
    entries, i = [], 0
    while i < len(toc):
        elen, off, dlen, ulen, cflag, typ = struct.unpack('!IIIIBc', toc[i:i+18])
        name = toc[i+18:i+elen].split(b'\0')[0].decode('utf-8', 'replace')
        entries.append((typ.decode('latin1'), name, off, dlen, ulen, cflag))
        i += elen
    return data, pkg_start, pyver, entries


def write(path, blob):
    d = os.path.dirname(path)
    if d:
        os.makedirs(d, exist_ok=True)
    with open(path, 'wb') as f:
        f.write(blob)


def main(exe, outdir):
    data, pkg_start, pyver, entries = read_archive(exe)
    os.makedirs(outdir, exist_ok=True)

    pyz_blob = None
    for typ, name, off, dlen, ulen, cflag in entries:
        if typ == 'z':
            raw = data[pkg_start+off:pkg_start+off+dlen]
            pyz_blob = zlib.decompress(raw) if cflag else raw
            write(os.path.join(outdir, name.replace('\\', os.sep)), pyz_blob)

    magic = pyz_blob[4:8] if pyz_blob else b'\x6f\x0d\x0d\x0a'

    for typ, name, off, dlen, ulen, cflag in entries:
        raw = data[pkg_start+off:pkg_start+off+dlen]
        if cflag:
            raw = zlib.decompress(raw)
        rel = name.replace('\\', os.sep).replace('/', os.sep)
        if typ == 'o':
            continue
        if typ == 's':
            write(os.path.join(outdir, rel + '.pyc'), magic + b'\0'*12 + raw)
        elif typ == 'z':
            continue
        else:
            write(os.path.join(outdir, rel), raw)

    print('extracted %d entries, pyver %d, magic %s' % (len(entries), pyver, magic.hex()))

    if pyz_blob is None:
        return
    tocpos = struct.unpack('!I', pyz_blob[8:12])[0]
    toclist = marshal.loads(pyz_blob[tocpos:])
    pdir = os.path.join(outdir, 'PYZ.pyz_extracted')
    for name, (typ, off, ln) in toclist:
        code = marshal.loads(zlib.decompress(pyz_blob[off:off+ln]))
        p = os.path.join(pdir, name.replace('.', os.sep) + '.pyc')
        write(p, magic + b'\0'*12 + marshal.dumps(code))
    print('pyz modules %d -> %s' % (len(toclist), pdir))


if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])
