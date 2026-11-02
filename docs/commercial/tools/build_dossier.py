"""Render the bilingual Markdown dossier as one review PDF, without network access.

Requires ReportLab in the authoring environment, not in Cauces. Original licence
texts and machine inventories remain separate files in the documentation ZIP.
"""
import argparse
import html
import json
import re
import textwrap
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    BaseDocTemplate, Frame, PageBreak, PageTemplate, Paragraph, Preformatted,
    Spacer, KeepTogether,
)
from reportlab.platypus.tableofcontents import TableOfContents

ROOT = Path(__file__).resolve().parents[1]
ORDER = [
    'README.md', 'READINESS.md', 'PRODUCT.md', 'USER_GUIDE.md', 'RELEASE_NOTES.md',
    'TERMS_DRAFT.md', 'PRIVACY_DRAFT.md', 'SUPPORT_REFUNDS_DRAFT.md',
    'TECHNICAL_SECURITY.md', 'LICENSES_PROVENANCE.md', 'RELEASE_RUNBOOK.md',
    'VALIDATION_PLAN.md', 'MAINTENANCE_HANDOVER.md', 'LEGAL_REVIEW.md', 'SOURCES.md',
    'templates/OWNERSHIP_DECLARATION_DRAFT.md',
    'templates/ORDER_CONFIRMATION_DRAFT.md', 'templates/ACCEPTANCE_RECORD.md',
    'templates/INCIDENT_RECORD.md',
]
INK = colors.HexColor('#183b3a')
TEAL = colors.HexColor('#176b60')
MUTED = colors.HexColor('#536765')
MINT = colors.HexColor('#d9f4ea')


def anchor(path):
    return 'doc_' + re.sub(r'[^a-zA-Z0-9]', '_', path)


class Dossier(BaseDocTemplate):
    def __init__(self, output, **kwargs):
        super().__init__(str(output), pagesize=A4, leftMargin=49, rightMargin=49,
                         topMargin=55, bottomMargin=49, **kwargs)
        self.page_map = {}
        frame = Frame(self.leftMargin, self.bottomMargin, self.width, self.height,
                      leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0)
        self.addPageTemplates(PageTemplate(id='dossier', frames=[frame], onPage=self.decorate))

    def decorate(self, canvas, doc):
        canvas.saveState()
        canvas.setFillColor(INK)
        canvas.setFont('DocBold', 8)
        canvas.drawString(49, A4[1] - 29, 'CAUCES  |  GuerraMagica Audio')
        canvas.setStrokeColor(colors.HexColor('#b9dcd0'))
        canvas.line(49, A4[1] - 38, A4[0] - 49, A4[1] - 38)
        canvas.setFillColor(MUTED)
        canvas.setFont('Doc', 7.5)
        canvas.drawString(49, 28, 'Borrador de preparación / Preparation draft  |  2026-11-02')
        canvas.drawRightString(A4[0] - 49, 28, str(doc.page))
        canvas.restoreState()

    def afterFlowable(self, flowable):
        if isinstance(flowable, Paragraph) and hasattr(flowable, '_section_file'):
            name = flowable._section_file
            key = anchor(name)
            self.canv.bookmarkPage(key)
            title = flowable.getPlainText()
            self.canv.addOutlineEntry(title, key, level=0, closed=False)
            self.notify('TOCEntry', (0, title, self.page, key))
            self.page_map[name] = self.page


def render(output, font_dir):
    for name, filename in [('Doc', 'Arial.ttf'), ('DocBold', 'Arial Bold.ttf'),
                           ('DocMono', 'Courier New.ttf')]:
        pdfmetrics.registerFont(TTFont(name, str(font_dir / filename)))
    pdfmetrics.registerFontFamily('Doc', normal='Doc', bold='DocBold', italic='Doc', boldItalic='DocBold')
    styles = getSampleStyleSheet()
    body = ParagraphStyle('DocBody', fontName='Doc', fontSize=10.3, leading=14.4,
                          textColor=INK, spaceAfter=7.5, splitLongWords=True)
    h1 = ParagraphStyle('DocH1', parent=body, fontName='DocBold', fontSize=19,
                        leading=23.5, spaceAfter=15, keepWithNext=True)
    h2 = ParagraphStyle('DocH2', parent=body, fontName='DocBold', fontSize=12,
                        leading=16, textColor=TEAL, spaceBefore=12,
                        spaceAfter=7, keepWithNext=True)
    meta = ParagraphStyle('DocMeta', parent=body, fontSize=8, leading=11,
                          textColor=MUTED, spaceAfter=13)
    bullet = ParagraphStyle('DocBullet', parent=body, leftIndent=13, firstLineIndent=0,
                            bulletIndent=1, spaceAfter=5)
    code = ParagraphStyle('DocCode', fontName='DocMono', fontSize=7.8, leading=10.1,
                          textColor=INK, backColor=colors.HexColor('#edf6f2'),
                          borderPadding=7, spaceBefore=7, spaceAfter=11)
    title = ParagraphStyle('CoverTitle', parent=h1, fontSize=40, leading=44)
    subtitle = ParagraphStyle('CoverSubtitle', parent=body, fontSize=18, leading=25,
                              spaceAfter=15)
    small = ParagraphStyle('CoverSmall', parent=body, fontSize=11, leading=16)

    def markup(text, source):
        escaped = html.escape(text)
        def link(match):
            label, target = match.group(1), html.unescape(match.group(2))
            if target.startswith(('https://', 'http://')):
                return '<link href="' + html.escape(target, quote=True) + '" color="#176b60">' + label + '</link>'
            relative = (ROOT / source).parent / target.split('#')[0]
            try:
                key = str(relative.resolve().relative_to(ROOT))
            except ValueError:
                return label
            if key in ORDER:
                return '<link href="#' + anchor(key) + '" color="#176b60">' + label + '</link>'
            return label + ' <font face="DocMono" size="8">(' + html.escape(target) + ')</font>'
        escaped = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', link, escaped)
        escaped = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', escaped)
        escaped = re.sub(r'`([^`]+)`', r'<font face="DocMono" size="8.5">\1</font>', escaped)
        return escaped

    story = [Spacer(1, 46), Paragraph('CAUCES', title),
             Paragraph('Documentación para una posible distribución comercial', subtitle),
             Paragraph('Documentation for a potential commercial release', subtitle),
             Spacer(1, 20), Paragraph('ES / EN  |  Dossier 1.0', small),
             Paragraph('Referencia / Baseline: Cauces 0.4.2, build 6', small),
             Paragraph('GuerraMagica Audio  |  2026-11-02', small), Spacer(1, 28),
             Paragraph('<b>BORRADOR DE PREPARACIÓN / PREPARATION DRAFT</b>', h2),
             Paragraph('Documentos editables y evidencia técnica para revisión. No es una aprobación comercial ni una certificación jurídica.', body),
             Paragraph('Editable documents and technical evidence for review. This is not commercial approval or legal certification.', body),
             Spacer(1, 14), Paragraph('Manuales, licencias, contratos, privacidad, soporte, publicación y mantenimiento. Los modelos y el audio no se incluyen.', body),
             Paragraph('Guides, licences, terms, privacy, support, release and handover. Models and audio are not included.', body), PageBreak(),
             Paragraph('Índice / Contents', h1)]
    toc = TableOfContents()
    toc.levelStyles = [ParagraphStyle('TOC', fontName='Doc', fontSize=9.2, leading=13.5,
                                      textColor=INK, leftIndent=0, firstLineIndent=0,
                                      spaceBefore=4, rightIndent=22)]
    story.append(toc)

    for filename in ORDER:
        story.append(PageBreak())
        lines = (ROOT / filename).read_text().splitlines()
        current = []
        mode = 'paragraph'
        code_lines = None

        def flush():
            nonlocal current, mode
            if current:
                text = ' '.join(current)
                if mode == 'bullet':
                    story.append(Paragraph(markup(text, filename), bullet, bulletText='-'))
                else:
                    story.append(Paragraph(markup(text, filename), body))
            current = []
            mode = 'paragraph'

        for line in lines:
            if line.startswith('```'):
                flush()
                if code_lines is None:
                    code_lines = []
                else:
                    wrapped = []
                    for code_line in code_lines:
                        wrapped.extend(textwrap.wrap(code_line, width=100, replace_whitespace=False,
                                                     drop_whitespace=False, break_long_words=True,
                                                     break_on_hyphens=False) or [''])
                    story.append(Preformatted('\n'.join(wrapped), code))
                    code_lines = None
                continue
            if code_lines is not None:
                code_lines.append(line)
                continue
            if not line.strip():
                flush()
            elif line.startswith('# '):
                flush()
                paragraph = Paragraph(markup(line[2:], filename), h1)
                paragraph._section_file = filename
                story.append(paragraph)
            elif line.startswith('## '):
                flush();story.append(Paragraph(markup(line[3:], filename), h2))
            elif line.startswith('Versión documental /'):
                flush();story.append(Paragraph(html.escape(line), meta))
            elif line.startswith('- '):
                flush();mode='bullet';current=[line[2:]]
            elif re.match(r'^\d+\. ', line):
                flush();current=[line]
            else:
                current.append(line.strip())
        flush()
        if code_lines is not None:
            raise ValueError('Unclosed code fence: ' + filename)

    output.parent.mkdir(parents=True, exist_ok=True)
    document = Dossier(output, title='Cauces - Commercial Documentation / Documentación comercial',
                       author='GuerraMagica Audio', subject='Bilingual preparation dossier; draft, not legal clearance')
    document.multiBuild(story)
    return document.page_map


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--font-dir', type=Path, default=Path('/System/Library/Fonts/Supplemental'))
    parser.add_argument('--page-map', type=Path)
    args = parser.parse_args()
    pages = render(args.output, args.font_dir)
    if args.page_map:
        args.page_map.parent.mkdir(parents=True, exist_ok=True)
        args.page_map.write_text(json.dumps(pages, ensure_ascii=False, indent=2)+'\n')
    print(args.output)
