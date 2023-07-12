from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_JUSTIFY, TA_LEFT, TA_CENTER, TA_RIGHT
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus.tables import TableStyle

class CustomTableStyle(TableStyle):
    def __init__(self, name=None, cmds=None, parent=None, **kw):
        super().__init__(cmds, parent, **kw)
        self.name=name

styles = getSampleStyleSheet()

# Table Of Contents
styles.add(ParagraphStyle(name = 'Heading1OfTOC',
    fontSize = 14,
    leading = 16,
    fontName='NotoSansTC-Light',
))

styles.add(ParagraphStyle(name = 'Heading2OfTOC',
    fontSize = 12,
    leading = 14,
    leftIndent = 5,
    fontName='NotoSansTC-Light',
))

styles.add(ParagraphStyle(name = 'customLinkStyle',
    fontSize = 10,
    fontName='NotoSansTC-Light',
    borderWidth=1,
    borderColor='#000000',
))

styles.add(ParagraphStyle(
    name="paragraphStyle",
    fontSize=30,
    fontName='NotoSansTC-Regular',
    alignment=TA_CENTER,
))

styles.add(ParagraphStyle(
    name='titleTOC',
    fontName='NotoSansTC-Light',
    fontSize=16,
    textColor= colors.toColor('rgba(44, 153, 132, 1.0)'),
    spaceAfter=15
))

styles.add(ParagraphStyle(
    name="subHeaderStyle",
    fontSize=18,
    fontName='NotoSansTC-Bold',
    alignment=TA_LEFT,
))

styles.add(CustomTableStyle(
    name="tableStyle",
    cmds=[
        # basic styles
        ("GRID", (0, 0), (-1, -1), 0.5, colors.red),
        ('LEFTPADDING', (0, 0), (-1, -1), 0),
        ('RIGHTPADDING', (0, 0), (-1, -1), 0),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
        ('TOPPADDING', (0, 0), (-1, -1), 0),
        ("ALIGN", (0, 0), (-1, -1), 'CENTER'),
        ("VALIGN", (0, 0), (-1, -1), 'MIDDLE'),
    ]
))