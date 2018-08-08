"""
get_visible_text.py
~~~
Returns all visible text from a url.
"""

import requests
import re
from bs4 import BeautifulSoup
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdfpage import PDFPage
from io import StringIO
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def get_visible_text(url: str, toc_type: str) -> str:
    """
    Returns all of the visible text in a web page. Gets rid of html tags and other unnecessary text.

    Args:
        url (str): The url of the web page.
        toc_type (str): The type of the TOC webpage. (can either be "pdf", "dynamic", or "regular")
    Returns:
        str: All of the visible text on the web page in one string block.
    """
    answer = ""  # variable to store all the visible text on url

    # (1) Figure out what kind of url it is and proceed accordingly
    if toc_type == "pdf":
        # pdf website (most likely Citi)
        print("Terms and conditions are pdf.")
        answer = scrape_from_pdf(url)

    elif toc_type == "dynamic":
        print("Terms and conditions are dynamic html.")
        # dynamic HTML content (most likely Capital One)
        answer = scrape_using_node(url)

    else:
        print("Terms and conditions are regular html.")
        # normal website with terms and conditions table in HTML as visual text (most websites--Amex, Chase, Discover)
        answer = scrape_visual_text_directly(url)

    # (2) Clean up visual text string a little before scraping and get rid of unicode garbage
    try:
        answer = answer.decode('utf-8').strip()
        answer = answer.encode('ascii', 'ignore')
    except:
        pass

    # (3) Gets rid of any lingering HTML syntax and extraneous spaces
    answer = re.sub(r"<", "", answer)
    answer = re.sub(r">", "", answer)
    answer = re.sub(r"\t", "", answer)
    answer = re.sub(r"\n", "", answer)

    print("This is the returned visible text")
    print(answer)

    return answer


def scrape_using_node(url: str) -> str:
    """
    Scrapes from dynamic HTML web pages. Primarily for Capital One websites. Uses selenium to load the JS first before
    trying to scrape the visible text.

    Args:
        url (str): The url to scrape.
    Returns:
        str: The visible text to return.
    """
    # (1) Use Selenium to get the visible text from webpages with elements dynamically loaded in with JS.
    # If scraping from another computer, make sure to change this path.
    browser = webdriver.Chrome(executable_path="/Users/user/chromedriver")
    # browser.implicitly_wait(10)
    browser.get(url)

    # we wait for the TOC table to appear in the webpage before trying getting the visible text
    try:
        element = WebDriverWait(browser, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "schumer"), )
        )
    except:
        try:
            element = WebDriverWait(browser, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "preamble"), )
            )
        except:
            try:
                element = WebDriverWait(browser, 10).until(
                    EC.presence_of_element_located((By.CLASS_NAME, "tncinner"), )
                )
            except:
                print("Terms and conditions table not found.")
                return

    answer = browser.page_source

    # (2) Gets rid of all of the text after the table. (We don't need the terms and conditions)
    # print(re.findall(r"</table.*?>", r_content))
    matched_indices = [m.start(0) for m in re.finditer(r"</table", answer)]
    if len(matched_indices) > 0:
        answer = answer[:matched_indices[-1]]

    # (3) Delete everything between <> (only want visual text)
    answer = re.sub(r"<.*?>", "", answer)  # Note: need non greedy (lazy) quantifier ?

    # (4) Get rid of all other text besides the table
    # makes assumption that all Capital One websites follow this format
    start_index = answer.find("Interest Rates and Interest Charges")
    if start_index >= 0:
        answer = answer[start_index:]
    end_index = answer.find("Apply Now")
    if end_index >= 0:
        answer = answer[:end_index]

    return answer


def scrape_visual_text_directly(url: str, add_new_lines: bool = False) -> str:
    """
    Returns all of the visible text directly from the url's html. Adapted from
    https://stackoverflow.com/questions/1936466/beautifulsoup-grab-visible-webpage-text.

    Args:
        url (str): The url to get the visible text from.
        add_new_lines (bool): Adds a new line (\n) in place of <li ...>. (For Nerdwallet scraping only)
    Returns:
        str: Returns all of the visible text (pre processed)
    """
    # ip_address = "97.105.19.61"
    # port = "53281"
    # proxy = 'https://{}:{}/'.format(ip_address, port)
    # print(proxy)
    r = requests.get(url)
    # r = requests.get(url, proxies={"https": proxy})

    # The response encoding should either be utf-8 or ISO-8859-1
    try:
        r_content = r.content.decode("utf-8")
    except:
        r_content = r.content.decode("ISO-8859-1")

    # gets rid of all text after the table (the terms and condition that we don't need)
    # print(re.findall(r"</table.*?>", r_content))
    matched_indices = [m.start(0) for m in re.finditer(r"</table", r_content)]
    if len(matched_indices) > 0:
        r_content = r_content[:matched_indices[-1]]

    # substitutions directed towards NerdWallet
    # make append a _ in front of all attribute headers as well as marking new lines with XYZABC123!!!
    if add_new_lines:
        r_content = re.sub(r"<h4.*?>", "_", r_content)
        r_content = re.sub(r"<h3.*?>", "_", r_content)
        r_content = re.sub(r"<li.*?>", "XYZABC123!!!", r_content)  # we use a dummy string to mark all new lines

    r_content = r_content.encode("utf-8")

    soup = BeautifulSoup(r_content, "lxml")
    # kill all script and style elements
    print(r.content)
    for script in soup.find_all(["script", "style"]):
        script.extract()  # rip it out
    # get text
    text = soup.get_text()
    # break into lines and remove leading and trailing space on each
    lines = (line.strip() for line in text.splitlines())
    # break multi-headlines into a line each
    chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
    # drop blank lines
    text = '\n'.join(chunk for chunk in chunks if chunk)

    return text


def scrape_from_pdf(url: str) -> str:
    """
    Scrapes visible text from a pdf.

    Args:
        url (str): The url to scrape from.
    Returns:
        str: The visible text scraped from the webpage.
    """
    # (1) Download PDF using requests
    # adapted from https://stackoverflow.com/questions/24844729/download-pdf-using-urllib
    response = requests.get(url)
    print("Writing to the pdf_processing_doc.")
    doc = open("pdf_processing_doc", 'wb')
    doc.write(response.content)
    doc.close()

    # # (2) Use pdfminer to scrape visual text from the pdf
    return convert_pdf_to_txt("pdf_processing_doc")


def convert_pdf_to_txt(document: str) -> str:
    """
    Converts a pdf document into a string text. Adapted from
    https://stackoverflow.com/questions/5725278/how-do-i-use-pdfminer-as-a-library.

    Args:
        document (str): The pdf document we want to convert.
    Returns:
        str: The string text.
    """
    print("Converting pdf to string.")
    rsrcmgr = PDFResourceManager()
    retstr = StringIO()
    codec = 'utf-8'
    laparams = LAParams()
    device = TextConverter(rsrcmgr, retstr, codec=codec, laparams=laparams)
    fp = open(document, 'rb')
    interpreter = PDFPageInterpreter(rsrcmgr, device)
    password = ""
    maxpages = 0
    caching = True
    pagenos = set()
    for page in PDFPage.get_pages(fp, pagenos, maxpages=maxpages, password=password, caching=caching,
                                  check_extractable=True):
        interpreter.process_page(page)
    fp.close()
    device.close()
    str = retstr.getvalue()
    retstr.close()
    return str


