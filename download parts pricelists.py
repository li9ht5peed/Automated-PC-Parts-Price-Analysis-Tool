import glob
import os
import time
from urllib.parse import urljoin
from functools import partial

import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

# Get the current working directory at the start
cwd = os.getcwd()


def handle_pdf_link(soup, link_string, filename, base_url=''):
    """Handles the pdf link in the soup.
    :param soup: BeautifulSoup object containing the HTML content.
    :param link_string: Specific string in the href attribute of the link.
    :param filename: Name of the file to be downloaded.
    :param base_url: Base url for the website, if needed.
    """
    print("Checking for PDF links...")
    # Loop through all 'a' tags in the soup
    for link in soup.find_all('a'):
        href = link.get('href')
        print(href)
        # If the href attribute exists and contains the specified string and '.pdf'
        if href and '.pdf' and link_string in href:
            print(f'Found PDF link: {href}')
            # Download and save the pdf file
            download_and_save_pdf(urljoin(base_url, href), filename)
            break
        print(soup)
        print(link)
    else:
        print("No matching PDF link found.")


def download_and_save_pdf(url, filename):
    """Downloads and saves the PDF file from the given URL.
    :param url: URL of the PDF file.
    :param filename: Name of the file to be saved.
    """
    # Send a GET request to the url
    response = requests.get(url)
    filename = os.path.join(cwd, filename)
    # Write the content of the response to a pdf file
    with open(filename, 'wb') as f:
        f.write(response.content)
    print(f"Downloaded and saved PDF as {filename}")


def handle_selenium_download(shop, file_xpath, download_xpath, filename, popup_close_xpath=None):
    """Handles file download using Selenium.
    :param shop: URL of the shop.
    :param file_xpath: XPath of the file link.
    :param download_xpath: XPath of the download button.
    :param filename: Name of the file to be downloaded.
    :param popup_close_xpath: XPath of the popup close button, if exists.
    """
    # Set up Chrome options
    options = Options()
    options.add_experimental_option('prefs', {
        "download.default_directory": cwd,  # Set default directory for downloads
        "download.prompt_for_download": False,  # To auto download the file
        "download.directory_upgrade": True,
        "plugins.always_open_pdf_externally": True  # To download PDF files
    })

    # Set up WebDriver with the options
    webdriver_service = Service('./chromedriver')
    driver = webdriver.Chrome(service=webdriver_service, options=options)
    driver.get(shop)

    # Wait for up to 10 seconds for the element to be present
    wait = WebDriverWait(driver, 10)
    file_link = wait.until(EC.presence_of_element_located((By.XPATH, file_xpath)))
    print(f'PDF link href: {file_link.get_attribute("href")}')
    file_link.click()

    # If there is a popup, close it
    if popup_close_xpath:
        popup_close_button = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, popup_close_xpath)))
        popup_close_button.click()

    download_button = wait.until(EC.presence_of_element_located((By.XPATH, download_xpath)))
    download_button.click()

    # Add a delay to give the file time to download
    time.sleep(5)
    print(f"Downloaded and saved PDF as {filename}")

    # Close the driver
    driver.quit()

    # Rename the downloaded file
    rename_downloaded_file(filename)


def rename_downloaded_file(new_file_name):
    """Renames the most recently downloaded PDF file.
    :param new_file_name: New name for the downloaded file.
    """
    # Get list of all PDF files in the current working directory
    list_of_files = glob.glob(cwd + '/*.pdf')
    # Get the most recently created file
    latest_file = max(list_of_files, key=os.path.getctime)

    # If a file with the new filename already exists, delete it
    if os.path.exists(cwd + '/' + new_file_name):
        os.remove(new_file_name)

    # Rename the most recent file
    os.rename(latest_file, cwd + '/' + new_file_name)


# Dictionary of handlers for each site
handlers = {
    'https://www.bizgram.com/pricelist-download/': partial(handle_pdf_link, link_string='/?eflws_download=001',
                                                           filename='bizgram.pdf'),
    # 'https://dynacoretech.com/pricelist': partial(handle_pdf_link, link_string='Price list folder/Dynacore PL',
    #                                               filename='dynacore.pdf', base_url='https://dynacoretech.com'),
    # 'http://www.fuwell.com.sg/': partial(handle_pdf_link, link_string='uploads/misc/Fuwell', filename='fuwell.pdf',
    #                                      base_url='http://www.fuwell.com.sg'),
    # 'http://infinitycomputer.com.sg/': partial(handle_pdf_link, link_string='assets/files/Infinity',
    #                                           filename='infinity.pdf'),
}

# Dictionary of dropbox links for each site
dropbox = {
    'https://www.dropbox.com/sh/95ps5ktas6y3iwl/AAB_4uLreCCoRfi-Q_5DDyuka?dl=0': partial(handle_selenium_download,
                                                                                         file_xpath='//a[contains(@aria-label, "PC Themes Price List")]',
                                                                                         download_xpath='//span[text()="Download"]',
                                                                                         filename='pc_themes.pdf'),
    'https://tradepac.com.sg/index.php?route=product/product&path=289&product_id=2663': partial(
        handle_selenium_download,
        file_xpath='//a[contains(@href, "/TRADEPACPRICELIST")]',
        download_xpath='//span[text()="Download"]',
        filename='tradepac.pdf',
        popup_close_xpath='//button[@class="dig-IconButton dig-IconButton--transparent dig-IconButton--standard dig-Modal-close-btn"]')
}


def main():
    """Main function that handles the download and renaming of files.
    """
    # For each shop in the handlers dictionary, download and save the pdf file
    for shop, handler in handlers.items():
        response = requests.get(shop)
        soup = BeautifulSoup(response.text, 'html.parser')
        handler(soup)

    # For each shop in the dropbox dictionary, download and save the pdf file using Selenium
    # for shop, handler in dropbox.items():
    #     handler(shop)


if __name__ == "__main__":
    main()
