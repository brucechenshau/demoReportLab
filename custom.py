from reportlab.platypus import Table, Paragraph
from ast import literal_eval
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.lib.utils import strTypes
from reportlab.platypus.flowables import Spacer
from reportlab.platypus.tableofcontents import TableOfContents

from style import styles

def drawPageNumbers(canvas, style, pages, availWidth, availHeight, dot=' . ', formatter=None):
    '''
    Draws pagestr on the canvas using the given style.
    If dot is None, pagestr is drawn at the current position in the canvas.
    If dot is a string, pagestr is drawn right-aligned. If the string is not empty,
    the gap is filled with it.
    '''
    pagestr = ', '.join([str(p) for p, _ in pages])
    x, y = canvas._curr_tx_info['cur_x'], canvas._curr_tx_info['cur_y']

    fontSize = style.fontSize
    pagestrw = stringWidth(pagestr, style.fontName, fontSize)

    #if it's too long to fit, we need to shrink to fit in 10% increments.
    #it would be very hard to output multiline entries.
    #however, we impose a minimum size of 1 point as we don't want an
    #infinite loop.   Ultimately we should allow a TOC entry to spill
    #over onto a second line if needed.
    freeWidth = availWidth-x
    while pagestrw > freeWidth and fontSize >= 1.0:
        fontSize = 0.9 * fontSize
        pagestrw = stringWidth(pagestr, style.fontName, fontSize)


    if isinstance(dot, strTypes):
        if dot:
            dotw = stringWidth(dot, style.fontName, fontSize)
            dotsn = int((availWidth-x-pagestrw)/dotw)
        else:
            dotsn = dotw = 0
        text = '%s %s' % (dotsn * dot, pagestr) # adding a space between dot and pagenumber
        newx = availWidth - dotsn*dotw - pagestrw
        pagex = availWidth - pagestrw
    elif dot is None:
        text = ',  ' + pagestr
        newx = x
        pagex = newx
    else:
        raise TypeError('Argument dot should either be None or an instance of basestring.')

    tx = canvas.beginText(newx, y)
    tx.setFont(style.fontName, fontSize)
    tx.setFillColor(style.textColor)
    tx.textLine(text)
    canvas.drawText(tx)

    commaw = stringWidth(', ', style.fontName, fontSize)
    for p, key in pages:
        if not key:
            continue
        w = stringWidth(str(p), style.fontName, fontSize)
        canvas.linkRect('', key, (pagex, y, pagex+w, y+style.leading), relative=1)
        pagex += w + commaw


class CustomParagraph(Paragraph):
    def __init__(self, name=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.name=name

class CustomTOC(TableOfContents):
    '''
    for custom the dots purpose.
    '''
    def __init__(self, **kwds):
        super().__init__(**kwds)
        self.dotsMinLevel = 0
        self.levelStyles = [styles.get(level) for level in ('Heading1OfTOC', 'Heading2OfTOC')]

    def notify(self, kind, stuff):
        """The notification hook called to register all kinds of events.

        Here we are interested in 'TOCEntry' events only.
        """
        if kind == 'TOCEntry':
            self.addEntry(*stuff)

    def wrap(self, availWidth, availHeight):
        "All table properties should be known by now."

        # makes an internal table which does all the work.
        # we draw the LAST RUN's entries!  If there are
        # none, we make some dummy data to keep the table
        # from complaining
        if len(self._lastEntries) == 0:
            _tempEntries = [(0,'Placeholder for table of contents',0,None)]
        else:
            _tempEntries = self._lastEntries        
        def drawTOCEntryEnd(canvas, kind, label):
            '''Callback to draw dots and page numbers after each entry.'''
            label = label.split(',')
            page, level, key = int(label[0]), int(label[1]), literal_eval(label[2])
            style = self.getLevelStyle(level)
            if self.dotsMinLevel >= 0 and level >= self.dotsMinLevel:
                dot = '.'
            else:
                dot = ''
            if self.formatter: page = self.formatter(page)
            drawPageNumbers(canvas, style, [(page, key)], availWidth, availHeight, dot)
        self.canv.drawTOCEntryEnd = drawTOCEntryEnd

        tableData = []
        for (level, text, pageNum, key) in _tempEntries:
            style = self.getLevelStyle(level)
            if key:
                text = '<a href="#%s">%s</a>' % (key, text)
                keyVal = repr(key).replace(',','\\x2c').replace('"','\\x2c')
            else:
                keyVal = None
            para = Paragraph('%s<onDraw name="drawTOCEntryEnd" label="%d,%d,%s"/>' % (text, pageNum, level, keyVal), style)
            if style.spaceBefore:
                tableData.append([Spacer(1, style.spaceBefore),])
            tableData.append([para,])

        self._table = Table(tableData, colWidths=(availWidth,), style=self.tableStyle)

        self.width, self.height = self._table.wrapOn(self.canv,availWidth, availHeight)
        return (self.width, self.height)
    
class CustomLink(TableOfContents):
    '''
    for custom the dots purpose.
    '''
    def __init__(self, name: str, text: str, **kwds):
        self._name=name
        self._text=text
        super().__init__(**kwds)

    def notify(self, kind, stuff):
        """The notification hook called to register all kinds of events.

        Here we are interested in 'TOCEntry' events only.
        """
        if kind == 'linkEntry' and self._name == stuff[-1]:
            self.addEntry(*stuff)

    def addEntry(self, level, text, pageNum, key=None, name=None):
        """Adds one entry to the table of contents.

        This allows incremental buildup by a doctemplate.
        Requires that enough styles are defined."""

        assert type(level) == type(1), "Level must be an integer"
        self._entries.append((level, text, pageNum, key, name ))

    def wrap(self, availWidth, availHeight):
        "All table properties should be known by now."

        # makes an internal table which does all the work.
        # we draw the LAST RUN's entries!  If there are
        # none, we make some dummy data to keep the table
        # from complaining
        if len(self._lastEntries) == 0:
            _tempEntries = [(0,'Placeholder for table of contents',0,None)]
        else:
            _tempEntries = self._lastEntries

        def drawTOCEntryEnd(canvas, kind, label):
            '''Callback to draw dots and page numbers after each entry.'''
            # label = label.split(',')
            # page, level, key = int(label[0]), int(label[1]), literal_eval(label[2])
            # style = self.getLevelStyle(level)
            # if self.dotsMinLevel >= 0 and level >= self.dotsMinLevel:
            #     dot = '.'
            # else:
            #     dot = ''
            # if self.formatter: page = self.formatter(page)
            # drawPageNumbers(canvas, style, [(page, key)], availWidth, availHeight, dot)
            pass

        self.canv.drawTOCEntryEnd = drawTOCEntryEnd

        
        if _tempEntries[0][1] == "Placeholder for table of contents":
            tableData = []
            for (level, text, pageNum, key) in _tempEntries:
                # print(level, text, pageNum, key, name)
                style = self.getLevelStyle(level)
                if key:
                    text = '<a href="#%s">%s_page %s</a>' % (key, self._text, pageNum)
                    keyVal = repr(key).replace(',','\\x2c').replace('"','\\x2c')
                else:
                    keyVal = None
                para = Paragraph('%s<onDraw name="drawTOCEntryEnd" label="%d,%d,%s"/>' % (text, pageNum, level, keyVal), style)
                if style.spaceBefore:
                    tableData.append([Spacer(1, style.spaceBefore),])
                tableData.append([para,])
        else:
            l = []
            for (level, text, pageNum, key, name) in _tempEntries:
                style = styles.get("customLinkStyle")
                if key:
                    l.append(f"{text}: <a href=#{key} color='blue'><u>{pageNum}</u></a>")
                    keyVal = repr(key).replace(',','\\x2c').replace('"','\\x2c')
                else:
                    keyVal = None
            text=f"{self._text} For {name}, please refer to page: " + ', '.join(l)
            para = Paragraph('%s<onDraw name="drawTOCEntryEnd" label="%d,%d,%s"/>' % (text, pageNum, level, keyVal), style)    

        # self._table = Table(tableData, colWidths=(availWidth,), style=self.tableStyle)
        self._table = Paragraph(text, style)

        # self.width, self.height = self._table.wrapOn(self.canv,availWidth, availHeight)
        self.width, self.height = self._table.wrapOn(self.canv,availWidth, availHeight)
        return (self.width, self.height)
