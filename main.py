from reportlab.platypus.doctemplate import PageTemplate, BaseDocTemplate, Spacer
from reportlab.platypus.frames import Frame
from reportlab.platypus import Table, Paragraph, PageBreak, NextPageTemplate
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
from reportlab.lib.units import cm
from reportlab.platypus.flowables import BalancedColumns
import pathlib
import uuid
import hashlib
from custom import CustomTOC, CustomLink, CustomParagraph
from style import styles
import itertools

BASE_PATH = pathlib.Path(__file__).parent

for (name, filename) in (
    ('NotoSansTC-Light', 'NotoSansTC-Light.ttf'),
    ('NotoSansTC-Regular', 'NotoSansTC-Regular.ttf'),
    ('NotoSansTC-Bold', 'NotoSansTC-Bold.ttf'),
    ('AdobeSongStd-Light', 'adobesongstd-light.ttf'),
):
    pdfmetrics.registerFont(
        TTFont(name, pathlib.PurePath.joinpath(BASE_PATH, filename))
    )


class Report(BaseDocTemplate):

    def __init__(self, filename, *args, **kwargs):
        super().__init__(filename, *args, **kwargs)

        frame = Frame(
            self.leftMargin,
            self.bottomMargin,
            self.width,
            self.height,
            id='NormalPageFrame',
            leftPadding=self.width * 3.5 / 35,
            rightPadding=self.width * 3.5 / 35,
            topPadding=self.height * 3.5 / 35,
            bottomPadding=self.height * 3.5 / 35,
            showBoundary=1,
        )
        page_template = PageTemplate(
            id='NormalPage',
            frames=[frame],
            onPage=self.drawFooter
        )
        self.addPageTemplates([page_template])
        self.availableWidth = frame._width - frame._leftPadding - frame._rightPadding
        self.availableHeight = frame._height - frame._topPadding - frame._bottomPadding

    def drawFooter(self, canvas, doc):
        x = self.pagesize[0] / 2
        canvas.saveState()
        canvas.setFont('AdobeSongStd-Light', 12)
        canvas.drawCentredString(x, 2.3*cm, f"{doc.page}")
        canvas.restoreState()

    def main(self):
        story = [NextPageTemplate(['NormalPage'])]
        story.append(Paragraph(
            text="這是封面",
            style=styles.get("paragraphStyle"),
        ))
        story.append(PageBreak())
        story.append(Paragraph('目錄', styles.get("titleTOC")))
        story.append(CustomTOC())
        story.append(PageBreak())
        story.append(CustomLink(
            name="gene1",
            text="這是文字，"
        ))
        story.append(PageBreak())
        story.append(CustomLink(
            name="gene2",
            text="這是文字，"
        ))
        story.append(PageBreak())
        for i in range(3):
            story.append(self.create_bookmark_paragraph(
                text=f"標題{i}",
                pstyle='subHeaderStyle',
            ))
            story.append(Spacer(1,2*cm))
            story.append(
                Table(
                    data=[
                        ['00', '01', '02', '03', '04'],
                        ['10', '11', '12' if i != 0 else (
                            self.create_bookmark_paragraph(
                                text="drug1",
                                pstyle='subHeaderStyle',
                                name="gene1",
                            )
                        ), '13', '14'],
                        ['20', '21', '22', '23', '24'],
                        ['30', '31', '32', '33', '34']
                    ],
                    colWidths=self.availableWidth // 5,
                    style=styles.get("tableStyle"),
                )
            )
            story.append(PageBreak())
        
        for gene_name, drugs in {
            "gene1": ["drug2", "drug3"]
        }.items():
            for drug in drugs:
                story.append(self.create_bookmark_paragraph(
                    text=drug,
                    pstyle='subHeaderStyle',
                    name=gene_name,
                ))
                story.append(PageBreak())

        for gene_name, drugs in {
            "gene2": ["drug4", "drug5", "drug6"]
        }.items():
            for drug in drugs:
                story.append(self.create_bookmark_paragraph(
                    text=drug,
                    pstyle='subHeaderStyle',
                    name=gene_name,
                ))
                story.append(PageBreak())

        self.multiBuild(story)

    def create_bookmark_paragraph(self, text:str, pstyle: str, name: str = "bookMark", bookmarkName: str = None, **kwargs):

        style = styles.get(pstyle)

        for (k, v) in kwargs.items():
            setattr(style, k, v)

        if bookmarkName is None:
            bookmarkName=hashlib.sha1(f'{text}{uuid.uuid4()}'.encode('utf-8')).hexdigest() # create bookmarkname
        
        para=CustomParagraph(name=name, text=f'{text}<a name="{bookmarkName}"/>', style=style) # modify paragraph text to include an anchor point with name bn
        para._bookmarkName=bookmarkName # store the bookmark name on the flowable so afterFlowable can see this
        return para

    def afterFlowable(self, flowable):
        "Registers TOC entries."
        if isinstance(flowable, CustomParagraph):
            level = 0 # for H1 style
            text = flowable.getPlainText()
            pageNumber = self.canv.getPageNumber()
            toc_el = [ level, text, pageNumber ] # basic elements, using Heading1OfTOC style
            toc_bm = getattr(flowable, '_bookmarkName', None) # bookmark for links
            if toc_bm:
                toc_el.append( toc_bm )
            if flowable.name == "bookMark":
                self.notify('TOCEntry', tuple(toc_el))
            else:
                toc_el.append(flowable.name)
                self.notify('linkEntry', tuple(toc_el))

        elif isinstance(flowable, Table):  
            for el in list(itertools.chain(*flowable._cellvalues)):
                if el and isinstance(el[0], CustomParagraph): # contentTable flowable
                    paraElement = el[0]
                    level = 0 # for H1 style
                    text = paraElement.getPlainText()
                    pageNumber = self.canv.getPageNumber()
                    toc_el = [ level, text, pageNumber ] # basic elements, using Heading1OfTOC style
                    toc_bm = getattr(paraElement, '_bookmarkName', None) # bookmark for links
                    if toc_bm:
                        toc_el.append( toc_bm )
                    if paraElement.name == "bookMark":
                        self.notify('TOCEntry', tuple(toc_el))
                    else:
                        toc_el.append(paraElement.name)
                        self.notify('linkEntry', tuple(toc_el))

if __name__ == "__main__":
    report = Report("report.pdf")
    report.main()

