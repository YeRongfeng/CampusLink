# -*- coding: utf-8 -*-
"""Build 设计报告-phase2.docx for the CampusLink book-trading module.

Visual style mirrors phase1's 设计报告-phase1-含数据库设计讲解.docx as closely as
python-docx allows: same page size/margins, same Title/Heading1/Heading2/Normal
font choices (黑体 title/headings, 宋体+Times New Roman body), centered cover page,
a real Word TOC field, "Table Grid" tables, and literal 一/二/三.../1.1/1.2... numbering
typed directly into heading text (matches how phase1 actually stores Heading 2 numbers;
simpler and renders identically across Word/WPS/LibreOffice).

Run with: python build_report.py
Output: ../设计报告-phase2.docx (same docs/交付文档 folder as the phase1 report)
"""
from pathlib import Path
from docx import Document
from docx.shared import Pt, Cm, RGBColor, Emu
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

HERE = Path(__file__).resolve().parent
OUT_PATH = HERE.parent / "设计报告-phase2.docx"

FONT_EASTASIA_BODY = "宋体"
FONT_LATIN_BODY = "Times New Roman"
FONT_HEADING = "黑体"
COLOR_HEADING1 = RGBColor(0x18, 0x18, 0x18)
COLOR_BLACK = RGBColor(0x00, 0x00, 0x00)


# ---------------------------------------------------------------------------
# Low-level helpers
# ---------------------------------------------------------------------------

def set_east_asian_font(run, east_asia=FONT_EASTASIA_BODY, ascii_font=FONT_LATIN_BODY):
    run.font.name = ascii_font
    rpr = run._element.get_or_add_rPr()
    rfonts = rpr.find(qn('w:rFonts'))
    if rfonts is None:
        rfonts = OxmlElement('w:rFonts')
        rpr.append(rfonts)
    rfonts.set(qn('w:eastAsia'), east_asia)
    rfonts.set(qn('w:ascii'), ascii_font)
    rfonts.set(qn('w:hAnsi'), ascii_font)


def add_body_paragraph(doc, text, *, align=WD_ALIGN_PARAGRAPH.JUSTIFY, indent_first_line=True,
                        size=12, bold=False, space_after=None):
    p = doc.add_paragraph()
    p.alignment = align
    pf = p.paragraph_format
    pf.line_spacing = 1.5
    if indent_first_line:
        pf.first_line_indent = Pt(size * 2)  # two-character indent
    if space_after is not None:
        pf.space_after = Pt(space_after)
    run = p.add_run(text)
    run.font.size = Pt(size)
    run.font.bold = bold
    set_east_asian_font(run)
    return p


def add_heading1(doc, number, text):
    p = doc.add_paragraph(style='Heading 1')
    p.paragraph_format.space_before = Pt(18)
    p.paragraph_format.space_after = Pt(12)
    p.paragraph_format.keep_with_next = True
    p.paragraph_format.first_line_indent = Pt(0)
    run = p.add_run(f"{number}、{text}")
    run.font.size = Pt(18)
    run.font.bold = True
    run.font.color.rgb = COLOR_HEADING1
    set_east_asian_font(run, FONT_HEADING, FONT_HEADING)
    return p


def add_heading2(doc, number, text):
    p = doc.add_paragraph(style='Heading 2')
    p.paragraph_format.space_before = Pt(13)
    p.paragraph_format.space_after = Pt(13)
    p.paragraph_format.keep_with_next = True
    p.paragraph_format.first_line_indent = Pt(0)
    run = p.add_run(f"{number} {text}")
    run.font.size = Pt(16)
    run.font.bold = False
    run.font.color.rgb = COLOR_BLACK
    set_east_asian_font(run, FONT_HEADING, FONT_HEADING)
    return p


def add_caption(doc, text):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p.add_run(text)
    run.font.size = Pt(10.5)
    run.font.color.rgb = RGBColor(0x59, 0x59, 0x59)
    set_east_asian_font(run)
    return p


def add_picture_centered(doc, path, width_cm):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p.add_run()
    run.add_picture(str(path), width=Cm(width_cm))
    return p


def set_cell_text(cell, text, *, bold=False, size=10.5, align=WD_ALIGN_PARAGRAPH.CENTER, color=None):
    cell.text = ""
    p = cell.paragraphs[0]
    p.alignment = align
    p.paragraph_format.space_before = Pt(2)
    p.paragraph_format.space_after = Pt(2)
    p.paragraph_format.first_line_indent = Pt(0)  # cells otherwise inherit Normal's 2-char indent, causing premature wraps
    p.paragraph_format.line_spacing = 1.0
    run = p.add_run(text)
    run.font.size = Pt(size)
    run.font.bold = bold
    if color:
        run.font.color.rgb = color
    set_east_asian_font(run)


def shade_cell(cell, hex_color):
    shd = OxmlElement('w:shd')
    shd.set(qn('w:val'), 'clear')
    shd.set(qn('w:color'), 'auto')
    shd.set(qn('w:fill'), hex_color)
    cell._tc.get_or_add_tcPr().append(shd)


def set_table_fixed_layout(table):
    """Force a fixed table layout so explicit column widths are honored by Word."""
    tbl_pr = table._tbl.tblPr
    layout = tbl_pr.find(qn('w:tblLayout'))
    if layout is None:
        layout = OxmlElement('w:tblLayout')
        tbl_pr.append(layout)
    layout.set(qn('w:type'), 'fixed')


def set_table_column_widths(table, widths_cm):
    """Set both the tblGrid column definitions and every cell's width (EMU + twips),
    which is what Word actually reads for a fixed-layout table. Setting only
    row.cells[i].width (python-docx default) is silently ignored by Word because
    the table-level tblW stays type="auto"; a truly fixed layout additionally needs
    tblW set to the explicit dxa total, otherwise Word keeps autofitting to content
    and visually wraps "wide" cells like VARCHAR(120) regardless of gridCol/tcW.
    """
    widths = [Cm(w) for w in widths_cm]
    total_twips = sum(w.twips for w in widths)
    tbl_pr = table._tbl.tblPr
    tbl_w = tbl_pr.find(qn('w:tblW'))
    if tbl_w is None:
        tbl_w = OxmlElement('w:tblW')
        tbl_pr.append(tbl_w)
    tbl_w.set(qn('w:w'), str(total_twips))
    tbl_w.set(qn('w:type'), 'dxa')
    grid = table._tbl.find(qn('w:tblGrid'))
    if grid is not None:
        cols = grid.findall(qn('w:gridCol'))
        for col, width in zip(cols, widths):
            col.set(qn('w:w'), str(width.twips))
    for row in table.rows:
        for cell, width in zip(row.cells, widths):
            cell.width = width
            tc_pr = cell._tc.get_or_add_tcPr()
            tc_w = tc_pr.find(qn('w:tcW'))
            if tc_w is None:
                tc_w = OxmlElement('w:tcW')
                tc_pr.append(tc_w)
            tc_w.set(qn('w:w'), str(width.twips))
            tc_w.set(qn('w:type'), 'dxa')


def add_table(doc, headers, rows, col_widths_cm=None, header_fill="D9D9D9"):
    table = doc.add_table(rows=1, cols=len(headers))
    table.style = 'Table Grid'
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.autofit = False
    table.allow_autofit = False
    set_table_fixed_layout(table)
    # Repeat the header row on every page a long table spans across.
    header_tr_pr = table.rows[0]._tr.get_or_add_trPr()
    header_tr_pr.append(OxmlElement('w:tblHeader'))
    for i, h in enumerate(headers):
        cell = table.rows[0].cells[i]
        set_cell_text(cell, h, bold=True)
        shade_cell(cell, header_fill)
    for row in rows:
        cells = table.add_row().cells
        for i, value in enumerate(row):
            set_cell_text(cells[i], value, align=WD_ALIGN_PARAGRAPH.CENTER if i == 0 else WD_ALIGN_PARAGRAPH.LEFT)
    if col_widths_cm:
        set_table_column_widths(table, col_widths_cm)
    doc.add_paragraph().paragraph_format.space_after = Pt(6)
    return table


def add_bullet(doc, text, *, size=12):
    p = doc.add_paragraph(style='List Bullet')
    p.paragraph_format.line_spacing = 1.5
    p.paragraph_format.left_indent = Cm(0.9)
    # Clear any default run created by the style and add our own with explicit font
    for run in list(p.runs):
        run.text = ''
    run = p.add_run(text)
    run.font.size = Pt(size)
    set_east_asian_font(run)
    return p


def add_code_paragraph(doc, text):
    p = doc.add_paragraph()
    p.paragraph_format.left_indent = Cm(0.5)
    p.paragraph_format.space_before = Pt(4)
    p.paragraph_format.space_after = Pt(4)
    run = p.add_run(text)
    run.font.size = Pt(10)
    run.font.name = 'Consolas'
    rpr = run._element.get_or_add_rPr()
    rfonts = rpr.find(qn('w:rFonts'))
    if rfonts is None:
        rfonts = OxmlElement('w:rFonts')
        rpr.append(rfonts)
    rfonts.set(qn('w:eastAsia'), '宋体')
    rfonts.set(qn('w:ascii'), 'Consolas')
    rfonts.set(qn('w:hAnsi'), 'Consolas')
    shd = OxmlElement('w:shd')
    shd.set(qn('w:val'), 'clear')
    shd.set(qn('w:color'), 'auto')
    shd.set(qn('w:fill'), 'F2F2F2')
    p._p.get_or_add_pPr().append(shd)
    return p


def insert_page_break(doc):
    doc.add_page_break()


def insert_toc_field(doc):
    paragraph = doc.add_paragraph()
    run = paragraph.add_run()
    fld_begin = OxmlElement('w:fldChar')
    fld_begin.set(qn('w:fldCharType'), 'begin')
    instr = OxmlElement('w:instrText')
    instr.set(qn('xml:space'), 'preserve')
    instr.text = 'TOC \\o "1-2" \\h \\z \\u'
    fld_sep = OxmlElement('w:fldChar')
    fld_sep.set(qn('w:fldCharType'), 'separate')
    fld_text = OxmlElement('w:t')
    fld_text.text = "请在 Word 中右键点击此处选择“更新域”以生成目录"
    fld_end = OxmlElement('w:fldChar')
    fld_end.set(qn('w:fldCharType'), 'end')
    r_element = run._r
    r_element.append(fld_begin)
    r_element.append(instr)
    r2 = paragraph.add_run()._r
    r2.append(fld_sep)
    r3 = paragraph.add_run()._r
    r3.append(fld_text)
    r4 = paragraph.add_run()._r
    r4.append(fld_end)
    return paragraph


def enable_update_fields_on_open(doc):
    # Ensures Word prompts to update the TOC field on open (matches typical Word-generated reports).
    settings = doc.settings.element
    update = OxmlElement('w:updateFields')
    update.set(qn('w:val'), 'true')
    settings.append(update)


ASSETS = HERE / "assets"

print("Module loaded; use via build_report.py entry point.")
