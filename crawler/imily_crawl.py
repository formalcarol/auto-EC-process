from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import NoSuchElementException
import openpyxl

PATH = r"D:\module\chromedriver-win32\chromedriver.exe"
header = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36"}
service = Service(PATH)
driver = webdriver.Chrome(service=service)
wait = WebDriverWait(driver, 10)

def crawl_imily():
    url = "https://www.imilyoutlet.com.tw/"
    driver.get(url)

    brands, products = [], []
    wait = WebDriverWait(driver, 10)
    try:
        telecom_link = wait.until(EC.presence_of_element_located((By.XPATH, "//span[text()='通訊商品']/parent::a")))
        ActionChains(driver).move_to_element(telecom_link).perform()

        brand_items = driver.find_elements(By.XPATH, "//div[@id='74925']/ul/li")
        for brand_item in brand_items:
            brand_link = brand_item.find_element(By.TAG_NAME, "a")
            brand_name = brand_link.text.strip()
    

            brand_sub_links = brand_item.find_elements(By.XPATH, ".//div[.//a]//a")
            if brand_sub_links:
                for sub_link in brand_sub_links:
                    sub_name = driver.execute_script("return arguments[0].textContent;", sub_link).strip()
                    sub_url = sub_link.get_attribute("href")
                    brands.append({"category": "通訊商品", "brand_name": brand_name, "brand_item_name": sub_name, "brand_item_url": sub_url})

        for brand in brands:
            driver.execute_script("window.location.href = arguments[0];", brand["brand_item_url"])
            products_data = get_imily_products(driver, wait, brand["brand_name"], brand["brand_item_name"])
            products.extend(products_data)
            #driver.back()

            telecom_link = wait.until(EC.presence_of_element_located((By.XPATH, "//span[text()='通訊商品']/parent::a")))
            ActionChains(driver).move_to_element(telecom_link).perform()
    except Exception as e:
        print(f"發生錯誤: {e}")
    
    driver.quit()
    return brands, products

def get_imily_products(driver, wait, brand_name, brand_item_name):
    product_data = []
    try:
        main_list_container = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".infinite-scroll-component")))
        products = main_list_container.find_elements(By.CSS_SELECTOR, ".storeProduct")
        for product in products:
            try:
                try:
                    product.find_element(By.XPATH, ".//p[contains(text(), '已售完')]")
                    continue
                except NoSuchElementException:
                    pass

                product_name = product.find_element(By.CSS_SELECTOR, "p.MuiTypography-body1")
                product_price = product.find_element(By.CSS_SELECTOR, "h6.MuiTypography-subtitle1")
                product_link = product.find_element(By.TAG_NAME, "a")
                product_url = product_link.get_attribute("href")
                
                product_data.append({
                    "brand_name": brand_name,
                    "brand_item_name": brand_item_name,
                    "product_name": product_name.text.strip(),
                    "product_price": product_price.text.strip(),
                    "product_url": product_url
                })
            except NoSuchElementException:
                continue
        return product_data
    except Exception as e:
        print(f"抓取 {brand_name} 商品列表時發生錯誤: {e}")
        return product_data
    
def write_imily_excel(products, output_path): 
    wb = openpyxl.Workbook() 
    ws = wb.active
    title = ["品牌名稱", "品牌項目", "產品名稱", "產品價格", "產品網址"]
    ws.append(title)

    for product in products:
        ws.append([
            product["brand_name"],
            product["brand_item_name"],
            product["product_name"],
            product["product_price"],
            product["product_url"]
        ])
    wb.save(output_path)

if __name__ == '__main__':
    brands, products = crawl_imily()
    write_imily_excel(products, "imily_products.xlsx")
