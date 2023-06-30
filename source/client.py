import os
import logging
import time
import traceback

import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

file_log = logging.FileHandler('log_client.log', encoding='utf-8')
logging.basicConfig(handlers=(file_log,),
                    format='[%(asctime)s | %(levelname)s | %(name)s]: %(message)s',
                    datefmt='%m.%d.%Y %H:%M:%S',
                    level=logging.INFO)

log = logging.getLogger("parser")


class Client:
    categories = (("https://www.ozon.ru/category/protsessory-15726/", "Процессоры"),
                  ('https://www.ozon.ru/category/smartfony-15502/', 'Смартфоны'))

    def __init__(self):
        self.driver = uc.Chrome(service=Service(ChromeDriverManager().install()), headless=True,
                                user_data_dir=f"{os.getcwd()}/cookie")
        self.driver.implicitly_wait(5)
        self.driver.set_window_size(1920, 1080)

    def get_urls(self):
        try:
            result = []
            for category, name in self.categories:
                product_urls = []
                product_prices = []
                for i in range(5):
                    url = category
                    if i != 0:
                        url += f'?page={i + 1}'
                    self.driver.get(url)
                    time.sleep(1)
                    product_url = list(map(lambda x: x.get_attribute("href"),
                                           self.driver.find_elements(By.CLASS_NAME, 'tile-hover-target.i3l.il4')))
                    while len(product_url) < 20 and i != 4:
                        time.sleep(1)
                        product_url = list(map(lambda x: x.get_attribute("href"),
                                               self.driver.find_elements(By.CLASS_NAME, 'tile-hover-target.i3l.il4')))

                    product_price = list(map(lambda x: x.text.split("₽")[0].replace('\u2009', ''),
                                             self.driver.find_elements(By.CLASS_NAME, 'oi6')))
                    product_urls.extend(product_url)
                    product_prices.extend(product_price)
                result.append(((product_urls, product_prices), name))
            return result
        except Exception as ex:
            print('Произошла ошибка внутри селениума, необходимо посмотреть файл log_client.log')
            log.error({'error': ex, 'traceback': traceback.format_exc()})

    def get_data(self, url):
        try:
            self.driver.get(url)
            return self.driver.find_element(By.TAG_NAME, 'body').text
        except Exception as ex:
            print('Произошла ошибка внутри селениума, необходимо посмотреть файл log_client.log')
            log.error({'error': ex, 'traceback': traceback.format_exc()})

    def quit(self):
        self.driver.quit()
