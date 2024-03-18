import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
import env_secrets
import CongressIndex
import random
from polygon import RESTClient
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class Browser:
    browser, service = None, None

    def __init__(self, driver: str):
        self.options = webdriver.ChromeOptions()
        self.options.add_argument("ignore-certificate-errors") #needs this for chrome since certificate error
        self.options.add_argument("--window-size=1980,1080")

        self.service = Service(driver)
        self.browser = webdriver.Chrome(options=self.options, service=self.service)
    
    def open_page(self, url: str):
        self.browser.get(url)

    def close_browser(self):
        self.browser.close()

    def add_input(self, by: By, value: str, text: str): 
        field = self.browser.find_element(by=by, value=value)
        for character in text:
            field.send_keys(character)
            time.sleep(random.uniform(0, 1)) # pause for 0.3 seconds

        time.sleep(5)
    
    def click_button(self, by: By, value: str): #works for links too
        button = self.browser.find_element(by=by, value=value)
        button.click()
        time.sleep(5)

    def login_investopedia(self, username: str, password: str):
        self.add_input(by=By.ID, value='username', text=username) #by basically is an abbrev for by id, by class name (by what is the program identifying the element on the page)
        self.add_input(by=By.ID, value='password', text=password)
        self.click_button(by=By.XPATH, value='/html/body/div[1]/div[1]/form/div[3]/input') #need to copy full xpath

    def navigateToStockTab(self):
        self.click_button(by=By.XPATH, value='/html/body/div[1]/div[1]/div/div/main/div/div[1]/div/div[2]/div[1]/div/div[2]/div/a[2]')
    
    def returnHome(self):
        self.click_button(by=By.XPATH, value='/html/body/div[1]/div[1]/div/div[2]/main/div/div[1]/div/div[2]/div[1]/div/div[2]/div/a[1]')

    def actionOnStock(self, stockName: str): #do not pass quantity as parameter, that will be calculated
        time.sleep(10)
        numPurchases = 0
        proportion = self.getBuyingPower() * 0.15 #need to get buyingpower first, as u start on main page
        time.sleep(5)
        self.navigateToStockTab()

        self.add_input(by=By.XPATH, value='/html/body/div[1]/div[1]/div/div/main/div/div[2]/div[2]/div[2]/div[1]/div[1]/div/div/div/div/div/div/div/div[1]/input[1]', text=stockName)
        time.sleep(5)                    
        self.click_button(by=By.XPATH, value='/html/body/div[1]/div[1]/div/div[2]/div/div[1]') #need to copy full xpath
        time.sleep(10)

        if(proportion > 10000):
            numPurchases = 10000 // self.getStockPrice() #calculates the number of stocks to buy
        else:
            numPurchases = proportion // self.getStockPrice()
        
        time.sleep(5)  
        if(numPurchases != 0):        
            self.add_input(by=By.XPATH, value='/html/body/div[1]/div[1]/div/div[1]/main/div/div[2]/div[2]/div[2]/div[1]/div[2]/form/div[1]/div/div[2]/div/div/div/div/div/input', text=str(numPurchases))
            time.sleep(5) #enter the quantity
            self.click_button(by=By.XPATH, value='/html/body/div[1]/div[1]/div/div[1]/main/div/div[2]/div[2]/div[2]/div[1]/div[2]/form/div[3]/div/div[2]/button') #preview order
            time.sleep(5)
            elem = self.browser.find_element(By.CLASS_NAME, "semi-bold.v-btn.v-btn--has-bg.v-btn--tile.theme--light.elevation-0.v-size--default.primary")
            print(elem.get_attribute('outerHTML')) #trying to print the element to see if it is correct
            self.browser.execute_script("arguments[0].click();", elem)

            #WebDriverWait(self.browser, 20).until(EC.element_to_be_clickable((By.XPATH, "//input[@class='semi-bold v-btn v-btn--has-bg v-btn--tile theme--light elevation-0 v-size--default primary']"))).click()

            #self.click_button(by=By.CLASS_NAME, value='semi-bold.v-btn.v-btn--has-bg.v-btn--tile.theme--light.elevation-0.v-size--default.primary')
            time.sleep(10)#if it has multiple class names, need to connect with dots

        self.click_button(by=By.XPATH, value='/html/body/div[1]/div[1]/div/div[2]/main/div/div[1]/div/div[2]/div[1]/div/div[2]/div/a[1]') #go back to the home page after transaction
        time.sleep(5)
    
    def getBuyingPower(self): #assumes ur on the main page
        buyingPower = self.browser.find_element(By.XPATH, "/html/body/div[1]/div/div/div/main/div/div[2]/div[2]/div[2]/div[1]/div[1]/div[2]/div/div[3]/div[1]/div[2]")
        print(buyingPower)
        buyingPowerContent = buyingPower.get_attribute('innerHTML').strip() #remove all leading and trailing whitespaces
        
        return float(buyingPowerContent[1:].replace(",", ''))

    def getStockPrice(self):
        time.sleep(5)  

        stockPrice = self.browser.find_element(By.XPATH, '/html/body/div[1]/div/div/div[1]/main/div/div[2]/div[2]/div[2]/div[1]/div[1]/div/div/div[2]/div/div[1]/div[2]/div/div[2]/div/div/table/tbody/tr[2]/td[2]')
        stockPrice = stockPrice.text
        sep = '/'
        stripped = stockPrice.split(sep, 1)[0]

        # stockPriceFront = self.browser.find_element(By.CLASS_NAME, 'tv-symbol-price-quote__value js-symbol-last')
        # #WebDriverWait(self.browser,100).until(EC.presence_of_element_located((By.XPATH, '/html/body/div[1]/div[2]/div/div/div/div[1]/div/div/div/div[1]/div[1]')))
        # stockPriceFront = stockPriceFront.text.strip()
        # stockPriceBack = self.browser.find_element(By.XPATH, '/html/body/div[1]/div[2]/div/div/div/div[1]/div/div/div/div[1]/div[1]/span')
        # #WebDriverWait(self.browser,100).until(EC.presence_of_element_located((By.XPATH, '/html/body/div[1]/div[2]/div/div/div/div[1]/div/div/div/div[1]/div[1]/span')))
        # stockPriceBack = stockPriceBack.text.strip()

        return float(stripped)

if __name__ == '__main__': #make sure this file isnt an import, and is run as the main file
    with open("CongressIndex.py") as file: #running CongressIndex.py from this file
        exec(file.read())

    print(CongressIndex.newStockTickers)

    browser = Browser('chromedriver-win64\chromedriver.exe')
    browser.open_page('https://www.investopedia.com/auth/realms/investopedia/protocol/openid-connect/auth?client_id=finance-simulator&redirect_uri=https%3A%2F%2Fwww.investopedia.com%2Fsimulator%2Fportfolio&state=6e700a07-e882-4019-a9fe-78760b19d657&response_mode=fragment&response_type=code&scope=openid&nonce=7bc7a86b-696d-49e7-b4ac-90b0cb34fc2f')#https://www.investopedia.com/auth/realms/investopedia/protocol/openid-connect/auth?client_id=finance-simulator&redirect_uri=https%3A%2F%2Fwww.investopedia.com%2Fsimulator%2Fportfolio&state=6e700a07-e882-4019-a9fe-78760b19d657&response_mode=fragment&response_type=code&scope=openid&nonce=7bc7a86b-696d-49e7-b4ac-90b0cb34fc2f
    time.sleep(3)
    browser.login_investopedia(env_secrets.investopediaEmail, env_secrets.investopediaPassword)
    time.sleep(3)
    browser.actionOnStock('nflx')
    time.sleep(10)

    browser.close_browser()

    #*****IF YOU GET CAUGHT FOR BOTTING, JUST CHANGE UR IP: open cmd with administrator, do "netsh interface ipv4 set address name=Ethernet static 130.113.73.[---] 255.255.255.0 130.113.73.5"