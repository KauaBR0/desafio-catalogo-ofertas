from django.core.management.base import BaseCommand
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from catalog.models import Product
from decimal import Decimal
import os
import time
import random
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Scrape Mercado Livre products'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.driver = None  

    def init_driver(self):
        chrome_options = Options()

        #evitar detecção
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation", "enable-logging"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--disable-infobars")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--lang=pt-BR")

        user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36" # Atualize se necessário
        chrome_options.add_argument(f"user-agent={user_agent}")

        chrome_options.add_argument("--headless=new")


        driver = webdriver.Chrome(options=chrome_options)

        driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
            "source": """
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined
                });
                window.chrome = {
                    runtime: {},
                };
            """
        })

        return driver

    def handle(self, *args, **kwargs):
        self.driver = self.init_driver()

        try:
            self.stdout.write("Acessando página inicial para cookies...")
            self.driver.get("https://www.mercadolivre.com.br")
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, 'body'))
            )
            time.sleep(random.uniform(2, 4))

            search_term = "computador-gamer-i7-16gb-ssd-1tb"
            search_url = f"https://lista.mercadolivre.com.br/informatica/{search_term}_NoIndex_True"

            self.stdout.write(f"Acessando URL de pesquisa: {search_url}")
            self.driver.get(search_url)

            self.rotate_user_agent(self.driver)

            if "Parece que esta página no existe" in self.driver.page_source:
                self.stdout.write(self.style.ERROR("Bloqueio detectado! Tentando contornar..."))
                self.rotate_user_agent(self.driver)
                self.driver.get(search_url)

            try:
                WebDriverWait(self.driver, 15).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, 'li.ui-search-layout__item'))
                )
            except TimeoutException:
                self.stdout.write(self.style.ERROR("Timeout - Resultados não carregados"))
                return

            self.save_debug_page(self.driver.page_source)

            products = self.driver.find_elements(By.CSS_SELECTOR, 'li.ui-search-layout__item')
            self.stdout.write(f"Encontrados {len(products)} produtos")

            for index, product in enumerate(products, 1):
                try:
                    self.process_product(product, index)
                    time.sleep(random.uniform(2, 5))
                except Exception as e:
                    logger.error(f"Erro no produto {index}: {str(e)}")
                    continue

            self.stdout.write(self.style.SUCCESS("Scraping concluído com sucesso!"))

        except Exception as e:
            logger.error(f"Erro fatal: {str(e)}")
            self.save_debug_page(self.driver.page_source)

        finally:
            if self.driver:
                self.driver.quit()

    def process_product(self, product, index):
        wait = WebDriverWait(self.driver, 10)

        try:
            product = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, f'li.ui-search-layout__item:nth-child({index})')))
        except TimeoutException:
            logger.error(f"Erro no produto {index}: Elemento do produto não encontrado.")
            return

        try:
            name_element = product.find_element(By.CSS_SELECTOR, 'h3.poly-component__title-wrapper a.poly-component__title')
            name = name_element.text.strip()
            product_url = name_element.get_attribute('href')
        except NoSuchElementException:
            logger.error(f"Erro no produto {index}: Nome ou URL do produto não encontrado.")
            return

        try:
            price_str = product.find_element(By.CSS_SELECTOR, 'span.andes-money-amount__fraction').text.replace('.', '').replace(',', '.')
            price = Decimal(price_str)
        except NoSuchElementException:
            logger.error(f"Erro no produto {index}: Preço não encontrado.")
            price = None

        original_price = None
        discount_percentage = None
        try:
            original_price_element = product.find_element(By.CSS_SELECTOR, 's.andes-money-amount--previous span.andes-money-amount__fraction')
            original_price_str = original_price_element.text.replace('.', '').replace(',', '.')
            original_price = Decimal(original_price_str)
            
            discount_element = product.find_element(By.CSS_SELECTOR, 'span.andes-money-amount__discount')
            discount_percentage = int(discount_element.text.replace('% OFF', '').strip())
        except NoSuchElementException:
            pass
        
        installment = None
        try:
            installment_element = product.find_element(By.CSS_SELECTOR, 'span.poly-price__installments')
            installment = installment_element.text.strip()
        except NoSuchElementException:
            pass
        
        image_url = None
        try:
            image_element = product.find_element(By.CSS_SELECTOR, 'img.poly-component__picture')
            image_url = image_element.get_attribute('data-src') or image_element.get_attribute('src')
            if image_url and 'data:' in image_url:
                image_url = None
            
        except NoSuchElementException:
            pass

        delivery_type = 'Full' if product.find_elements(By.CSS_SELECTOR, '.ui-search-item__shipping--full') else 'Normal'
        free_shipping = bool(product.find_elements(By.CSS_SELECTOR, '.poly-component__shipping'))

        Product.objects.update_or_create(
            product_url=product_url,
            defaults={
                'name': name,
                'price': price,
                'original_price': original_price,
                'discount_percentage': discount_percentage,
                'installment': installment,
                'image_url': image_url,
                'delivery_type': delivery_type,
                'free_shipping': free_shipping,
            }
        )

        self.stdout.write(f"[{index}] {name[:50]}... - R$ {price}")

    def rotate_user_agent(self, driver):
        new_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36" 
        driver.execute_cdp_cmd('Network.setUserAgentOverride', {"userAgent": new_agent})

    def save_debug_page(self, content):
        debug_dir = os.path.join(os.getcwd(), 'debug')
        os.makedirs(debug_dir, exist_ok=True)

        debug_file = os.path.join(debug_dir, f'debug_{int(time.time())}.html')
        with open(debug_file, 'w', encoding='utf-8') as f:
            f.write(content)

        self.stdout.write(self.style.WARNING(f"Debug salvo em: {debug_file}"))