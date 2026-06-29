#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Fresh build: split by Heading 1 boundaries, preserve exact document order.
"""
import docx, os, re, sys
sys.stdout.reconfigure(encoding='utf-8')

INPUT = "C:/temp/claude-code-test/History.docx"
OUT = "C:/temp/faculty-history-final"
IMG_DIR = os.path.join(OUT, "images")
os.makedirs(IMG_DIR, exist_ok=True)

PD = {'0':'۰','1':'۱','2':'۲','3':'۳','4':'۴','5':'۵','6':'۶','7':'۷','8':'۸','9':'۹'}

def fix(t):
    if not t: return t
    t = t.replace('ي','ی').replace('ك','ک')
    def fy(m):
        y=m.group(0)
        if len(y)==4:
            r=y[::-1]
            if r.startswith('13') or r.startswith('14'): return r
        return y
    t = re.sub(r'\b(\d{4})\b', fy, t)
    for e,p in PD.items(): t=t.replace(e,p)
    return t.strip()

def tbl2md(table):
    rows=[]
    for row in table.rows:
        cells=[fix(c.text.replace('\n',' ').strip()) for c in row.cells]
        rows.append(cells)
    if not rows: return ""
    cols=max(len(r) for r in rows)
    for r in rows:
        while len(r)<cols: r.append('')
    lines=['| '+' | '.join(rows[0])+' |','|'+('|'.join(['---']*cols))+'|']
    for r in rows[1:]:
        lines.append('| '+' | '.join(r)+' |')
    return '\n'.join(lines)

def extract_img(drawing_elem, imap):
    for desc in drawing_elem.iter():
        dt = desc.tag.split('}')[-1] if '}' in desc.tag else desc.tag
        if dt == 'blip':
            ea = '{http://schemas.openxmlformats.org/officeDocument/2006/relationships}embed'
            rid = desc.get(ea)
            if rid and rid in imap:
                return imap[rid]
    return None

doc = docx.Document(INPUT)

# Extract images
imap, ic = {}, 0
for rel in doc.part.rels.values():
    if "image" in rel.reltype:
        try:
            d=rel.target_part.blob
            ext=os.path.splitext(rel.target_ref)[1].lower()
            if ext in ['.png','.jpg','.jpeg','.gif','.bmp']:
                n=f"img_{ic:03d}{ext}"
                with open(os.path.join(IMG_DIR,n),'wb') as f: f.write(d)
                imap[rel.rId]=n; ic+=1
        except: pass

# Map paragraphs and tables to indices
para_map = {id(p): i for i, p in enumerate(doc.paragraphs)}
tbl_map = {id(t): i for i, t in enumerate(doc.tables)}

# Chapter name mapping for Heading 1 titles
H1_NAMES = {
    'پیشگفتار': ('01-preface', 'پیشگفتار'),
    'تاریخچه دانشکده': ('02-history', 'تاریخچه دانشکده'),
    'روسای دانشکده': ('03-deans', 'روسای دانشکده'),
    'معاونین پژوهش': ('04-admin', 'معاونان'),
    'معاونان آموزشی': ('04-admin', 'معاونان'),
    'معاونان اداری': ('04-admin', 'معاونان'),
    'معرفی گروه': ('05-departments', 'گروه‌های آموزشی'),
    'افتخارات اعضای': ('06-honors', 'افتخارات اعضای هیأت علمی'),
    'دانشجویان افتخار': ('07-student-honors', 'دانشجویان افتخارآفرین'),
    'قطب‌های علمی': ('08-research', 'مراكز پژوهشی و قطب‌های علمی'),
    'کتابخانه': ('09-library', 'کتابخانه پروفسور فاطمی'),
    'مجلات': ('10-journals', 'مجلات'),
    'بخش رایانه': ('11-computing', 'بخش رایانه'),
    'آزمایشگاه': ('12-labs', 'آزمایشگاه‌ها'),
    'کنفرانس': ('13-conferences', 'کنفرانس‌ها و سمینارها'),
    'نکوداشت': ('14-memorials', 'نکوداشت‌ها و بزرگداشت‌ها'),
    'کتاب\u200cها': ('15-books', 'کتاب‌ها'),
    'کتاب': ('15-books', 'کتاب‌ها'),
    'ضمایم': ('16-appendix', 'ضمایم'),
    'مراجع': ('17-references', 'مراجع'),
}

def get_h1(text):
    for k,v in H1_NAMES.items():
        if k in text: return v
    return (f'h1_{text[:10]}', text[:30])

# Process body elements in document order
chapters = {}  # filename -> list of markdown lines
chapter_order = []
current_file = '00-intro'
current_title = 'مقدمه'

# First paragraph block before any Heading 1 goes to intro
chapters[current_file] = []

body = doc.element.body
for child_elem in body:
    tag = child_elem.tag.split('}')[-1] if '}' in child_elem.tag else child_elem.tag

    if tag == 'p':
        for para in doc.paragraphs:
            if para._element is child_elem:
                text = para.text.strip()
                style = para.style.name

                # Skip TOC dots
                if '...' in text: break

                # Heading 1 = new chapter
                if style == 'Heading 1' and text:
                    fname, title = get_h1(text)
                    current_file = fname
                    current_title = title
                    if current_file not in chapters:
                        chapters[current_file] = []
                        chapter_order.append(current_file)
                    chapters[current_file].append(f"\n# {fix(text)}\n")
                    break

                if current_file not in chapters:
                    chapters[current_file] = []

                has_img = any(c.tag.endswith('}drawing') for run in para.runs for c in run._element)

                if 'Heading' in style and text:
                    level = int(style[-1])
                    chapters[current_file].append(f"\n{'#'*level} {fix(text)}\n")
                elif text:
                    chapters[current_file].append(f"{fix(text)}\n")

                # Images
                if has_img:
                    for run in para.runs:
                        for c in run._element:
                            if c.tag.endswith('}drawing'):
                                img = extract_img(c, imap)
                                if img:
                                    chapters[current_file].append(f"\n![image](images/{img})\n")
                break

    elif tag == 'tbl':
        for table in doc.tables:
            if table._element is child_elem:
                md = tbl2md(table)
                if md:
                    if current_file not in chapters:
                        chapters[current_file] = []
                        chapter_order.append(current_file)
                    chapters[current_file].append(f"\n{md}\n")
                break

# Write files
used = []
for fname in chapter_order:
    content = chapters.get(fname, [])
    if not content: continue

    # Find title from first heading
    title = fname
    for line in content:
        if line.startswith('# '):
            title = line.strip().lstrip('# ')
            break

    filepath = os.path.join(OUT, f"{fname}.qmd")
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(f'---\ntitle: "{fix(title)}"\n---\n\n')
        f.write('\n'.join(content))
    used.append(fname)
    imgs = sum(1 for l in content if '![image]' in l)
    tbls = sum(1 for l in content if l.strip().startswith('|'))
    print(f"  {fname}.qmd: {len(content)} lines, {imgs} imgs, {tbls} tbls")

# Config
ch_yaml = '\n'.join([f"    - {c}.qmd" for c in used])
with open(os.path.join(OUT, "_quarto.yml"), 'w', encoding='utf-8') as f:
    f.write(f"""project:
  type: book
  output-dir: _book
book:
  title: "تاریخچه دانشکده علوم ریاضی"
  subtitle: "دانشگاه فردوسی مشهد"
  author: "تهیه و تدوین: زهره وثاق و وحیده وحیدنیا"
  date: "تیر ماه ۱۴۰۵"
  chapters:
    - index.qmd
{ch_yaml}
dir: rtl
format:
  html:
    theme: cosmo
    toc: true
    code-fold: true
    rtl: true
    linkcolor: "#0066cc"
execute:
  echo: false
""")
print("Done!")
