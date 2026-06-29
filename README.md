# تاریخچه دانشکده علوم ریاضی

GitHub Page of Faculty of Mathematical Sciences, Ferdowsi University of Mashhad

## About

This repository contains the history of the Faculty of Mathematical Sciences at Ferdowsi University of Mashhad, built with [Quarto](https://quarto.org/). The content is extracted from a Microsoft Word document and converted to a modern web book with proper Persian (RTL) typography.

## Structure

| File | Content |
|------|---------|
| `index.qmd` | Title page |
| `01-preface.qmd` | پیشگفتار |
| `02-history.qmd` | تاریخچه دانشکده |
| `03-deans.qmd` | روسای دانشکده |
| `04-admin.qmd` | مدیران و معاونان |
| `05-departments.qmd` | گروه‌های آموزشی |
| `06-honors.qmd` | افتخارات اعضای هیأت علمی |
| `07-student-honors.qmd` | دانشجویان افتخارآفرین |
| `08-research.qmd` | مراكز پژوهشی و قطب‌های علمی |
| `09-library.qmd` | کتابخانه پروفسور فاطمی |
| `10-journals.qmd` | مجلات |
| `11-computing.qmd` | بخش رایانه |
| `12-labs.qmd` | آزمایشگاه‌ها |
| `13-conferences.qmd` | کنفرانس‌ها و سمینارها |
| `14-memorials.qmd` | نکوداشت‌ها و بزرگداشت‌ها |
| `15-books.qmd` | کتاب‌ها |
| `16-appendix.qmd` | ضمایم |
| `17-references.qmd` | مراجع |

## Build Instructions

### Prerequisites

- [Quarto](https://quarto.org/docs/get-started/) v1.4+
- For PDF output: [TeX Live](https://www.tug.org/texlive/) with XeLaTeX and xepersian package

### Build HTML (Website)

```bash
quarto render --to html
```

Output will be in `_book/` directory. Open `_book/index.html` in browser.

### Preview (Live Reload)

```bash
quarto preview
```

### Build PDF (with Persian Support)

```bash
quarto render --to pdf --no-execute
```

Then patch for xepersian:

```bash
# Find the generated .tex file and add after last \usepackage{etoolbox}:
# \usepackage{xepersian}
# \settextfont{Gandom}
# \setlatintextfont{Times New Roman}

# Then run xelatex twice:
xelatex -interaction=nonstopmode <filename>.tex
xelatex -interaction=nonstopmode <filename>.tex
```

Or use the provided script:

```powershell
.\build-pdf.ps1
```

## Automatic Deployment

This site is automatically built and deployed to GitHub Pages via GitHub Actions when changes are pushed to the `main` branch.

## Source

Content extracted from `History.docx` using `build.py`. To regenerate from the Word document:

```bash
python build.py
```

## License

Content: Faculty of Mathematical Sciences, Ferdowsi University of Mashhad
