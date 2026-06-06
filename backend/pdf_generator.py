# pdf_generator.py
# Generates a branded PDF report using ReportLab.

import os
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, KeepTogether
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT

# ── Brand Colors ────────────────────────────────────────────────────────────
BRAND_BLUE   = colors.HexColor('#2563EB')
BRAND_DARK   = colors.HexColor('#0f172a')
BRAND_LIGHT  = colors.HexColor('#dbeafe')
BRAND_ACCENT = colors.HexColor('#0ea5e9')
SUCCESS      = colors.HexColor('#10b981')
MUTED        = colors.HexColor('#64748b')
BORDER       = colors.HexColor('#e2e8f0')
WHITE        = colors.white
TEXT         = colors.HexColor('#1e293b')

# ── Report Output Directory ─────────────────────────────────────────────────
REPORTS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "generated_reports")
os.makedirs(REPORTS_DIR, exist_ok=True)


def generate_pdf(agent_name: str, email: str, zip_code: str,
                 market_data: dict, summary: str) -> str:
    """
    Generate a branded PDF market report.

    Returns the filename (not full path) so FastAPI can serve it via /reports/
    """
    filename  = f"report_{datetime.now().strftime('%Y_%m_%d_%H%M%S')}_{zip_code.replace(' ', '_')}.pdf"
    filepath  = os.path.join(REPORTS_DIR, filename)
    date_str  = datetime.now().strftime("%B %d, %Y")

    doc = SimpleDocTemplate(
        filepath,
        pagesize=letter,
        leftMargin=0.75 * inch,
        rightMargin=0.75 * inch,
        topMargin=0.5 * inch,
        bottomMargin=0.75 * inch,
    )

    styles  = _build_styles()
    story   = []

    # ── Header Banner ────────────────────────────────────────────────────────
    header_data = [[
        Paragraph('<font color="white"><b>Snap</b>Report</font>', styles['brand_name']),
        Paragraph(f'<font color="#93c5fd">AI-Powered Real Estate Market Report</font><br/>'
                  f'<font color="#64748b" size="8">Powered by Redfin Data + Groq AI · Snaphomz</font>',
                  styles['header_sub']),
    ]]
    header_table = Table(header_data, colWidths=[2.2 * inch, 5.1 * inch])
    header_table.setStyle(TableStyle([
        ('BACKGROUND',    (0, 0), (-1, -1), BRAND_DARK),
        ('VALIGN',        (0, 0), (-1, -1), 'MIDDLE'),
        ('LEFTPADDING',   (0, 0), (-1, -1), 16),
        ('RIGHTPADDING',  (0, 0), (-1, -1), 16),
        ('TOPPADDING',    (0, 0), (-1, -1), 18),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 18),
        ('ROUNDEDCORNERS', (0, 0), (-1, -1), [8, 8, 0, 0]),
    ]))
    story.append(header_table)
    story.append(Spacer(1, 2))

    # ── Blue Accent Bar ──────────────────────────────────────────────────────
    accent_bar = Table([[''] * 3],
                       colWidths=[2.5 * inch, 2.4 * inch, 2.4 * inch])
    accent_bar.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, 0), BRAND_BLUE),
        ('BACKGROUND', (1, 0), (1, 0), BRAND_ACCENT),
        ('BACKGROUND', (2, 0), (2, 0), SUCCESS),
        ('ROWBACKGROUNDS', (0, 0), (-1, -1), [None]),
        ('TOPPADDING',    (0, 0), (-1, -1), 3),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
    ]))
    story.append(accent_bar)
    story.append(Spacer(1, 16))

    # ── Report Info Block ────────────────────────────────────────────────────
    info_data = [
        [Paragraph('PREPARED FOR', styles['info_label']),
         Paragraph('MARKET AREA', styles['info_label']),
         Paragraph('REPORT DATE', styles['info_label'])],
        [Paragraph(f'<b>{agent_name}</b><br/>'
                   f'<font color="#64748b">{email}</font>', styles['info_value']),
         Paragraph(f'<b>{zip_code}</b><br/>'
                   f'<font color="#64748b">Local Market</font>', styles['info_value']),
         Paragraph(f'<b>{date_str}</b><br/>'
                   f'<font color="#64748b">Data: Apr 2026</font>', styles['info_value'])],
    ]
    info_table = Table(info_data, colWidths=[2.45 * inch, 2.45 * inch, 2.4 * inch])
    info_table.setStyle(TableStyle([
        ('BACKGROUND',    (0, 0), (-1, -1), BRAND_LIGHT),
        ('BOX',           (0, 0), (-1, -1), 0.5, BORDER),
        ('INNERGRID',     (0, 0), (-1, -1), 0.5, BORDER),
        ('LEFTPADDING',   (0, 0), (-1, -1), 12),
        ('RIGHTPADDING',  (0, 0), (-1, -1), 12),
        ('TOPPADDING',    (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
        ('VALIGN',        (0, 0), (-1, -1), 'TOP'),
        ('ROWBACKGROUNDS', (0, 0), (-1, 0), [colors.HexColor('#eff6ff')]),
    ]))
    story.append(info_table)
    story.append(Spacer(1, 20))

    # ── Section: Market Statistics ───────────────────────────────────────────
    story.append(Paragraph('📊  Market Statistics', styles['section_header']))
    story.append(Spacer(1, 8))

    # Data source note
    ds = market_data.get("data_source", "Redfin Housing Market Data")
    story.append(Paragraph(
        f'<font color="#64748b" size="8">Source: {ds} · Local variance applied for {zip_code}</font>',
        styles['caption']
    ))
    story.append(Spacer(1, 10))

    # Build stat table (2 rows × 3 cols)
    stats_display = [
        {
            'label': 'Median Sale Price',
            'value': f"${market_data.get('median_price', 0):,.0f}",
            'yoy':   market_data.get('median_price_yoy'),
            'note':  f"National: ${market_data.get('national_median_price', 0):,.0f}",
        },
        {
            'label': 'Days on Market',
            'value': f"{market_data.get('days_on_market', 0)} days",
            'yoy':   None,
            'note':  'Median',
        },
        {
            'label': 'New Listings',
            'value': f"{market_data.get('new_listings', 0):,}",
            'yoy':   market_data.get('new_listings_yoy'),
            'note':  'This period',
        },
        {
            'label': 'Active Listings',
            'value': f"{market_data.get('active_listings', 0):,}",
            'yoy':   market_data.get('active_listings_yoy'),
            'note':  'Total available',
        },
        {
            'label': 'Homes Sold',
            'value': f"{market_data.get('homes_sold', 0):,}",
            'yoy':   market_data.get('homes_sold_yoy'),
            'note':  'Closed transactions',
        },
        {
            'label': 'Inventory (months)',
            'value': f"{market_data.get('inventory_months', 0):.1f} mo",
            'yoy':   None,
            'note':  'Supply indicator',
        },
    ]

    def _stat_cell(s):
        yoy = s['yoy']
        if yoy is not None:
            sign   = '+' if float(yoy) >= 0 else ''
            yoy_str = f"{'↑' if float(yoy) >= 0 else '↓'} {sign}{yoy:.2f}% YOY"
            yoy_color = '#16a34a' if float(yoy) >= 0 else '#dc2626'
        else:
            yoy_str   = s['note']
            yoy_color = '#64748b'

        return Paragraph(
            f'<font color="#64748b" size="7"><b>{s["label"].upper()}</b></font><br/>'
            f'<font size="14"><b>{s["value"]}</b></font><br/>'
            f'<font color="{yoy_color}" size="8">{yoy_str}</font>',
            styles['stat_cell']
        )

    stat_rows = [
        [_stat_cell(stats_display[0]), _stat_cell(stats_display[1]), _stat_cell(stats_display[2])],
        [_stat_cell(stats_display[3]), _stat_cell(stats_display[4]), _stat_cell(stats_display[5])],
    ]
    col_w = 2.43 * inch
    stat_table = Table(stat_rows, colWidths=[col_w, col_w, col_w])
    stat_table.setStyle(TableStyle([
        ('BOX',           (0, 0), (-1, -1), 0.5, BORDER),
        ('INNERGRID',     (0, 0), (-1, -1), 0.5, BORDER),
        ('BACKGROUND',    (0, 0), (-1, -1), WHITE),
        ('LEFTPADDING',   (0, 0), (-1, -1), 14),
        ('RIGHTPADDING',  (0, 0), (-1, -1), 14),
        ('TOPPADDING',    (0, 0), (-1, -1), 14),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 14),
        ('VALIGN',        (0, 0), (-1, -1), 'TOP'),
        # Alternate row background
        ('ROWBACKGROUNDS', (0, 0), (-1, -1), [colors.HexColor('#f8fafc'), WHITE]),
    ]))
    story.append(stat_table)
    story.append(Spacer(1, 24))

    # ── Additional Metrics Row ───────────────────────────────────────────────
    extra_rows = [[
        Paragraph(
            f'<font color="#64748b" size="8"><b>LIST-TO-SALE RATIO</b></font><br/>'
            f'<b>{market_data.get("list_to_sale_ratio", 0):.1f}%</b>',
            styles['extra_cell']
        ),
        Paragraph(
            f'<font color="#64748b" size="8"><b>PENDING SALES</b></font><br/>'
            f'<b>{market_data.get("pending_sales", 0):,}</b>',
            styles['extra_cell']
        ),
        Paragraph(
            f'<font color="#64748b" size="8"><b>PRICE GROWTH (YOY)</b></font><br/>'
            f'<b>+{market_data.get("price_growth", 0):.2f}%</b>',
            styles['extra_cell']
        ),
    ]]
    extra_table = Table(extra_rows, colWidths=[col_w, col_w, col_w])
    extra_table.setStyle(TableStyle([
        ('BOX',           (0, 0), (-1, -1), 0.5, BORDER),
        ('INNERGRID',     (0, 0), (-1, -1), 0.5, BORDER),
        ('BACKGROUND',    (0, 0), (-1, -1), colors.HexColor('#eff6ff')),
        ('LEFTPADDING',   (0, 0), (-1, -1), 14),
        ('RIGHTPADDING',  (0, 0), (-1, -1), 14),
        ('TOPPADDING',    (0, 0), (-1, -1), 12),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
        ('VALIGN',        (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    story.append(extra_table)
    story.append(Spacer(1, 28))

    # ── Section: AI Market Analysis ──────────────────────────────────────────
    story.append(Paragraph('🤖  AI Market Analysis', styles['section_header']))
    story.append(Spacer(1, 8))
    story.append(Paragraph(
        '<font color="#64748b" size="8">Generated by Groq · llama-3.3-70b-versatile</font>',
        styles['caption']
    ))
    story.append(Spacer(1, 10))

    # Format narrative paragraphs
    for para in summary.split('\n'):
        para = para.strip()
        if not para:
            story.append(Spacer(1, 6))
            continue
        if para[0].isdigit() and '.' in para[:3]:
            # Numbered section header
            story.append(Paragraph(f'<b>{para}</b>', styles['narrative_heading']))
        else:
            story.append(Paragraph(para, styles['narrative']))
        story.append(Spacer(1, 4))

    story.append(Spacer(1, 20))

    # ── Footer ───────────────────────────────────────────────────────────────
    story.append(HRFlowable(width="100%", thickness=0.5, color=BORDER))
    story.append(Spacer(1, 8))

    footer_data = [[
        Paragraph(
            f'<font color="#64748b" size="8">'
            f'SnapReport by Snaphomz · Generated {date_str} · '
            f'Data: Redfin Housing Market Data, National (Apr 2026)</font>',
            styles['footer_left']
        ),
        Paragraph(
            f'<font color="#2563EB" size="8"><b>snaphomz.com</b></font>',
            styles['footer_right']
        ),
    ]]
    footer_table = Table(footer_data, colWidths=[5.5 * inch, 1.8 * inch])
    footer_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('LEFTPADDING',  (0, 0), (-1, -1), 0),
        ('RIGHTPADDING', (0, 0), (-1, -1), 0),
    ]))
    story.append(footer_table)

    # Build PDF
    doc.build(story)
    return filename


def _build_styles() -> dict:
    """Create and return all custom paragraph styles."""
    base = getSampleStyleSheet()
    return {
        'brand_name': ParagraphStyle(
            'brand_name', fontName='Helvetica-Bold',
            fontSize=22, textColor=WHITE, alignment=TA_LEFT
        ),
        'header_sub': ParagraphStyle(
            'header_sub', fontName='Helvetica',
            fontSize=10, textColor=WHITE, alignment=TA_LEFT, leading=16
        ),
        'info_label': ParagraphStyle(
            'info_label', fontName='Helvetica-Bold',
            fontSize=7, textColor=colors.HexColor('#3b82f6'),
            letterSpacing=0.8, alignment=TA_LEFT
        ),
        'info_value': ParagraphStyle(
            'info_value', fontName='Helvetica',
            fontSize=10, textColor=TEXT, alignment=TA_LEFT, leading=15
        ),
        'section_header': ParagraphStyle(
            'section_header', fontName='Helvetica-Bold',
            fontSize=13, textColor=BRAND_DARK, spaceBefore=4, spaceAfter=2
        ),
        'caption': ParagraphStyle(
            'caption', fontName='Helvetica',
            fontSize=8, textColor=MUTED, alignment=TA_LEFT
        ),
        'stat_cell': ParagraphStyle(
            'stat_cell', fontName='Helvetica',
            fontSize=10, textColor=TEXT, leading=16
        ),
        'extra_cell': ParagraphStyle(
            'extra_cell', fontName='Helvetica',
            fontSize=10, textColor=TEXT, leading=16
        ),
        'narrative_heading': ParagraphStyle(
            'narrative_heading', fontName='Helvetica-Bold',
            fontSize=11, textColor=BRAND_DARK, spaceBefore=8, spaceAfter=2
        ),
        'narrative': ParagraphStyle(
            'narrative', fontName='Helvetica',
            fontSize=9.5, textColor=TEXT, leading=15, alignment=TA_LEFT
        ),
        'footer_left': ParagraphStyle(
            'footer_left', fontName='Helvetica',
            fontSize=8, textColor=MUTED, alignment=TA_LEFT
        ),
        'footer_right': ParagraphStyle(
            'footer_right', fontName='Helvetica-Bold',
            fontSize=8, textColor=BRAND_BLUE, alignment=TA_RIGHT
        ),
    }
