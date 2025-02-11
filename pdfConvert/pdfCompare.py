import PyPDF2
import os
from datetime import datetime
from PyPDF2 import PdfReader

import PyPDFCompare as pycompare

def arabic_to_roman(arabic):
    roman = ''
    while arabic >= 1000:
      roman += 'm'
      arabic -= 1000
    diffs = [900, 500, 400, 300, 200, 100, 90, 50, 40, 30, 20, 10, 9, 5, 4, 3, 2, 1]
    digits = ['cm', 'd', 'cd', 'ccc', 'cc', 'c', 'xc', 'l', 'xl', 'xxx', 'xx', 'x', 'ix', 'v', 'iv', 'iii', 'ii', 'i']
    for i in range(len(diffs)):
      if arabic >= diffs[i]:
        roman += digits[i]
        arabic -= diffs[i]
    return(roman)

def compare(fname, doc_old, doc_new):
    olddir = os.getcwd()
    os.chdir(fname)
    docA = aw.Document(doc_old)
    docB = aw.Document(doc_new)

    # There should be no revisions before comparison.
    docA.accept_all_revisions()
    docB.accept_all_revisions()

    docA.compare(docB, "Author Name", datetime.now())
    docA.save("Output.pdf")

def get_page_labels(pdf):
    try:
        page_label_type = pdf.trailer["/Root"]["/PageLabels"]["/Nums"][1].getObject()["/S"]
    except:
        page_label_type = "/D"
    try:
        page_start = pdf.trailer["/Root"]["/PageLabels"]["/Nums"][1].getObject()["/St"]
    except:
        page_start = 1
    page_count = pdf.getNumPages()
    ##or, if you feel fancy, do:
    #page_count = pdf.trailer["/Root"]["/Pages"]["/Count"]
    page_stop = page_start + page_count

    if page_label_type == "/D":
        page_numbers = list(range(page_start, page_stop))
        for i in range(len(page_numbers)):
            page_numbers[i] = str(page_numbers[i])
    elif page_label_type == '/r':
        page_numbers_arabic = range(page_start, page_stop)
        page_numbers = []
        for i in range(len(page_numbers_arabic)):
            page_numbers.append(arabic_to_roman(page_numbers_arabic[i]))

    print(page_label_type)
    print(page_start)
    print(page_count)
    print(page_numbers)
def extract_pdinfo(dir, fname):
    olddir = os.getcwd()
    os.chdir(dir)
    with open(fname, 'rb') as f:
        pdf = PdfReader(f)
        information = pdf.getDocumentInfo()
        number_of_pages = pdf.getNumPages()
        outline = pdf.getPageLayout()
        page_info = pdf.getPage(1)
        get_page_labels(pdf)

    txt = f
    """
    Information about {pdf_path}: 

    Author: {information.author}
    Creator: {information.creator}
    Producer: {information.producer}
    Subject: {information.subject}
    Title: {information.title}
    Number of pages: {number_of_pages}
    """

    print(txt)
    os.chdir(olddir)
    return information

dir = r'C:\Users\ginse\OneDrive\Documents\SG\Projects\Backbone - VEP\Engineering\Electrical-Engineering\Electrical-Design\compare_3'
pdf1 = r'2024-03-26_Backbone_-_90.pdf' #r'old_page3.pdf'
doc_new = r'new_page3.pdf'
extract_pdinfo(dir, pdf1)