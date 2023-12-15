from PyQt5.QtWidgets import QApplication, QDialog, QLineEdit, QVBoxLayout, QPushButton, QLabel
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon, QFont
from PyQt5 import QtCore
import pyperclip


def close_browser(browser):
    try:
        if browser is not None and browser.capabilities['browserVersion']:
            # Close all tabs
            browser.execute_script("window.open('', '_self').close();")
            browser.quit()
    except Exception as e:
        print(f"Error closing browser: {e}")


def get_price_mediagalaxy(browser, product_name, links):
    try:
        # Navigate to mediagalaxy.ro
        browser.get('https://mediagalaxy.ro/')

        # Find the search input and enter the user-inputted product name
        search_input_mediagalaxy = browser.find_element(
            By.XPATH, '//*[@id="__next"]/div[1]/div[1]/div/div/div[3]/div/form/div/div/input')
        search_input_mediagalaxy.send_keys(product_name)

        # Find the search button and click it
        search_button_mediagalaxy = browser.find_element(
            By.XPATH, '//*[@id="__next"]/div[1]/div[1]/div/div/div[3]/div/form/div/div/button[2]')
        search_button_mediagalaxy.click()

        # Wait for the first product to be present on the page
        wait_mediagalaxy = WebDriverWait(browser, 10)
        first_product_mediagalaxy = wait_mediagalaxy.until(EC.presence_of_element_located(
            (By.XPATH, '//*[@id="__next"]/div[2]/div[1]/main/div[2]/div[2]/div[2]/ul[2]/li[1]/div/a[2]')))

        # Capture the link
        links['mediagalaxy'] = first_product_mediagalaxy.get_attribute('href')

        first_product_mediagalaxy.click()

        # Wait for the price element to be present on the page
        price_element_mediagalaxy = wait_mediagalaxy.until(EC.presence_of_element_located(
            (By.XPATH, '//*[@id="__next"]/div[2]/div[1]/main/div[1]/div[4]/div[2]/div/div[1]/div[1]/div[1]/div/div[2]')))

        # Get the text of the price element
        mediagalaxy_price = price_element_mediagalaxy.text

        return mediagalaxy_price

    except NoSuchElementException as e:
        print(f"Error in MediaGalaxy: {e}")
        return "Not found"


class ProductInputDialog(QDialog):
    def __init__(self, parent=None):
        super(ProductInputDialog, self).__init__(parent)
        self.setWindowIcon(QIcon('protection.png'))
        self.setWindowTitle("Price Tracking App")
        font = QFont("Georgia", 12)
        self.setWindowFlags(self.windowFlags() & ~
                            Qt.WindowContextHelpButtonHint)
        self.setStyleSheet("QDialog {background-color: #7d8780;}")

        self.product_input = QLineEdit(self)
        self.ok_button = QPushButton("Search", self)
        layout = QVBoxLayout(self)
        layout.addWidget(self.product_input)
        layout.addWidget(self.ok_button)

        self.ok_button.clicked.connect(self.accept)

    def get_product_name(self):
        return self.product_input.text()


class PriceDialog(QDialog):
    def __init__(self, emag_price, evomag_price, mediagalaxy_price, links, parent=None):
        super(PriceDialog, self).__init__(parent)
        self.setWindowFlags(self.windowFlags() & ~
                            QtCore.Qt.WindowContextHelpButtonHint)
        self.setStyleSheet("background-color: #d1eddb;")
        self.setWindowIcon(QIcon('protection.png'))
        self.setWindowTitle("Price Tracking App")

        self.emag_price_label = QLabel(f"eMAG Price: {emag_price}", self)
        self.evomag_price_label = QLabel(f"EvoMag Price: {evomag_price}", self)
        self.mediagalaxy_price_label = QLabel(
            f"MediaGalaxy Price: {mediagalaxy_price}", self)
        self.emag_link_label = QLabel("eMAG Link: ", self)
        self.evomag_link_label = QLabel("EvoMag Link: ", self)
        self.mediagalaxy_link_label = QLabel("MediaGalaxy Link: ", self)

        # Set link labels
        if 'emag' in links:
            self.emag_link_label.setText(f"eMAG Link: {links['emag']}")
            self.emag_link_label.setTextInteractionFlags(
                Qt.TextSelectableByMouse)
        if 'evomag' in links:
            self.evomag_link_label.setText(f"EvoMag Link: {links['evomag']}")
            self.evomag_link_label.setTextInteractionFlags(
                Qt.TextSelectableByMouse)
        if 'mediagalaxy' in links:
            self.mediagalaxy_link_label.setText(
                f"MediaGalaxy Link: {links['mediagalaxy']}")
            self.mediagalaxy_link_label.setTextInteractionFlags(
                Qt.TextSelectableByMouse)

        layout = QVBoxLayout(self)
        layout.addWidget(self.emag_price_label)
        layout.addWidget(self.emag_link_label)
        layout.addWidget(self.evomag_price_label)
        layout.addWidget(self.evomag_link_label)
        layout.addWidget(self.mediagalaxy_price_label)
        layout.addWidget(self.mediagalaxy_link_label)

    def showEvent(self, event):
        super().showEvent(event)

        # Copy links to clipboard when the PriceDialog is shown
        emag_link = f"eMAG Link: {links.get('emag', 'Not found')}\n"
        evomag_link = f"EvoMag Link: {links.get('evomag', 'Not found')}\n"
        mediagalaxy_link = f"MediaGalaxy Link: {
            links.get('mediagalaxy', 'Not found')}\n"

        clipboard_text = emag_link + evomag_link + mediagalaxy_link
        pyperclip.copy(clipboard_text)

        # Notify the user
        print("Links have been copied to the clipboard.")


if __name__ == "__main__":
    app = QApplication([])

    # Create PyQt input dialog
    input_dialog = ProductInputDialog()
    input_result = input_dialog.exec_()
    product_name = input_dialog.get_product_name()

    # Initialize variables to store product prices and links
    emag_price = "Not found"
    evomag_price = "Not found"
    mediagalaxy_price = "Not found"

    # Capture links
    links = {}

    options = uc.ChromeOptions()
    # options.add_argument('--headless')

    # After entering the product name
    if input_result == QDialog.Accepted and product_name:
        # Interact with emag.ro
        browser_emag = uc.Chrome()
        try:
            browser_emag.get('https://www.emag.ro/')
            search_input_emag = browser_emag.find_element(
                By.XPATH, '//*[@id="searchboxTrigger"]')
            search_input_emag.send_keys(product_name)
            search_button_emag = browser_emag.find_element(
                By.XPATH, '//*[@id="masthead"]/div/div/div[2]/div/form/div[1]/div[2]')
            search_button_emag.click()
            wait_emag = WebDriverWait(browser_emag, 10)
            first_product_emag = wait_emag.until(EC.presence_of_element_located(
                (By.XPATH, '//*[@id="card_grid"]/div[1]/div/div/div[3]/a')))

            # Capture the link
            links['emag'] = first_product_emag.get_attribute('href')

            first_product_emag.click()
            price_element_emag = wait_emag.until(EC.presence_of_element_located(
                (By.XPATH, '//*[@id="main-container"]/section[3]/div/div[1]/div[2]/div/div[2]/div[2]/form[1]/div[1]/div[1]/div[1]/div/div/div[1]/p[2]')))
            emag_price = price_element_emag.text
        except NoSuchElementException as e:
            print(f"Error in eMAG: {e}")
        finally:
            close_browser(browser_emag)

        # Interact with evomag.ro
        browser_evomag = uc.Chrome()
        try:
            browser_evomag.get('https://www.evomag.ro/')
            search_input_evomag = browser_evomag.find_element(
                By.XPATH, '/html/body/div[4]/div[1]/div/div[1]/form/div/span/input[2]')
            browser_evomag.execute_script(
                "arguments[0].focus();", search_input_evomag)
            search_input_evomag.send_keys(product_name)
            search_button_evomag = browser_evomag.find_element(
                By.XPATH, '/html/body/div[4]/div[1]/div/div[1]/form/div/div[1]/input')
            search_button_evomag.click()
            wait_evomag = WebDriverWait(browser_evomag, 10)
            first_product_evomag = wait_evomag.until(EC.presence_of_element_located(
                (By.XPATH, '/html/body/div[5]/div[4]/div/div[2]/div[2]/div[5]/div[1]/div/div[3]/a')))

            # Capture the link
            links['evomag'] = first_product_evomag.get_attribute('href')

            first_product_evomag.click()
            price_element_evomag = wait_evomag.until(EC.element_to_be_clickable(
                (By.XPATH, '//*[@id="add-to-cart-detail"]/div/div[3]')))

            evomag_price = price_element_evomag.text
        except NoSuchElementException as e:
            print(f"Error in EvoMag: {e}")
        finally:
            close_browser(browser_evomag)

        # Interact with mediagalaxy.ro
        browser_mediagalaxy = uc.Chrome()
        try:
            mediagalaxy_price = get_price_mediagalaxy(
                browser_mediagalaxy, product_name, links)
        finally:
            close_browser(browser_mediagalaxy)

    # Show the PriceDialog with the obtained prices and links
    price_dialog = PriceDialog(emag_price, evomag_price.splitlines()[
                               0], mediagalaxy_price, links)
    price_dialog.exec_()
