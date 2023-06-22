import pdfminer
from pdfminer.high_level import extract_pages
from pdfminer.layout import LTTextContainer

import re

from PyPDF2 import PdfWriter, PdfReader

import fitz
import os


def extract_text_content(path):
    """_summary_

    :param path: _description_
    :type path: _type_
    :return: _description_
    :rtype: _type_
    """
    content = []

    for page_layout in extract_pages(path):
        for element in page_layout:
            if isinstance(element, LTTextContainer):
                # removes line breaks
                # removes leading and trailing whitespace
                # replaces multiple spaces with a single space
                # converts text to lowercase
                content.append((re.sub(' +', ' ', ((element.get_text()).replace('\n', ' ').strip()).lower()), 
                                element.bbox, page_layout.pageid))

    return [tup for tup in content if tup[0]] # to remove empty strings


def find_indicator(text_content, regex):
    """_summary_

    :param text_content: _description_
    :type text_content: _type_
    :param regex: _description_
    :type regex: _type_
    :return: _description_
    :rtype: _type_
    """
    all_tup = []
    i = 0

    for tup in text_content:
        
        match = re.search(regex, tup[0]) # search is enough to identify an occurrence for every tuple (we don't need to use findall())

        if match:
            all_tup.append((i, tup[0], tup[1], tup[2]))
            i += 1

    return all_tup


def crop_pdf(path, pad_x, pad_y, all_tup, list_idx, indicator_name):
    """_summary_

    :param path: _description_
    :type path: _type_
    :param pad_x: _description_
    :type pad_x: _type_
    :param pad_y: _description_
    :type pad_y: _type_
    :param all_tup: _description_
    :type all_tup: _type_
    :param list_idx: _description_
    :type list_idx: _type_
    :param indicator_name: _description_
    :type indicator_name: _type_
    """
    print("Processing...")
    # page coordinates (assuming that all pages are identical)
    for page_layout in extract_pages(path):
        page_coo = page_layout.bbox
        break

    x0, y0, x1, y1 = all_tup[list_idx][2]

    crop_coo = [int(x0 - pad_x), int(y0 - pad_y), 
                int(x1 + pad_x), int(y1 + pad_y)] # add padding to each coordinate

    # to make sure we do not go over the page limits
    for i in range(2):
        if crop_coo[i] < page_coo[i]:
            crop_coo[i] = int(page_coo[i])
            
    for i in range(2, 4):
        if crop_coo[i] > page_coo[i]:
            crop_coo[i] = int(page_coo[i])

    reader = PdfReader(path)

    writer = PdfWriter()

    page = reader.pages[all_tup[list_idx][3]-1] # starts in 0

    page.mediabox.lower_left = crop_coo[0:2] # (x0, y0)
    page.mediabox.upper_right = crop_coo[2:4] # (x1, y1)

    writer.add_page(page)

    if list_idx < 10:
        filename = path.split('/')[-1][:-4] + '-crop_' + indicator_name + str(0) + str(list_idx) + '.pdf'
    else:
        filename = path.split('/')[-1][:-4] + '-crop_' + indicator_name + str(list_idx) + '.pdf'

    print(os.getcwd())
    with open("./output_data/crops/" + filename, "wb") as f:
        writer.write(f)

    print("Done!")


def crop_to_image():
    """_summary_
    """
    print("Processing...")
    crops_path = "./output_data/crops/"

    for filename in os.listdir(crops_path):
        if filename.endswith('.pdf'):
            with fitz.open(crops_path + filename) as crop_pdf:

                zoom_x = 2
                zoom_y = 2
                mat = fitz.Matrix(zoom_x, zoom_y)

                page = crop_pdf.load_page(0)

                pix = page.get_pixmap(matrix=mat)
                pix.save(crops_path + filename.split('.')[0] + '.jpg') 
            os.remove(crops_path + filename)
    print("Done!")


if __name__ == '__main__':

    #path = "./tutorials/sustainability_reports/Electrolux_2021.pdf"
    
    #content = extract_text_content(path)
    #print(content[0])
    #print(content[1])
    #print(content[2])

    #regex = 'sustainability report.{1,10}\d{4}'

    #print(find_indicator(content, regex))

    #all_tup = find_indicator(path, regex)
    #crop_pdf(path, all_tup, 0, "report_year")
    #crop_pdf(path, all_tup, 1, "report_year")

    crop_to_image()

    print("Success!")