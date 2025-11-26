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

def crawl_findprice():
    target_products = ["Apple MacBook Pro M2", "Apple MacBook Air M2", "Apple 原廠 MagSafe 充電器", "OPPO Reno8 Pro 5G", "OPPO Reno8 5G", "OPPO A77 5G", "Lenovo IdeaPad Slim 3 14吋筆電", "HTC VIVE Flow 虛擬實境頭戴裝置", "Kieslect 藍牙通話智慧運動手錶 kr2"]
    product_list = []
    url = "https://www.findprice.com.tw/"
    driver.get(url)

    for target_product in target_products:
        search = wait.until(EC.presence_of_element_located((By.ID, "search")))
        search.clear()
        search.send_keys(target_product)
        search.send_keys(Keys.RETURN)

        try:
            wait.until(EC.presence_of_element_located((By.CLASS_NAME, "pagecontent-left")))
            products = driver.find_elements(By.XPATH, "//div[contains(@class, 'divGoods') or contains(@class, 'divPromoGoods')]")

            for product in products:
                try:
                    product_element = product.find_element(By.CLASS_NAME, "GoodsGname").find_element(By.TAG_NAME, "a")
                    product_name = product_element.text
                    product_url = product_element.get_attribute("href")

                    price_text = product.find_element(By.CLASS_NAME, "rec-price-20").text
                    product_price = price_text.split("商品選項")[0].strip()
                    
                    merchant_element = product.find_element(By.CLASS_NAME, "GoodsMname").find_element(By.CLASS_NAME, "mname")
                    merchant_text = merchant_element.text
                    merchant_name = merchant_text.split('&nbsp;')[0].strip()
                                            
                    product_list.append({
                        "target_item": target_product,
                        "product_name": product_name,
                        "product_price": product_price,
                        "product_url": product_url,
                        "merchant_name": merchant_name
                    })
                    
                except Exception as e:
                    continue
        except Exception as e:
            print(f"搜尋 {target_product} 時發生錯誤或超時: {e}")
    driver.quit()
    #print(product_list)

    seen_urls = set()
    findprice_products = []
    for product in product_list:
        if product["product_url"] not in seen_urls:
            findprice_products.append(product)
            seen_urls.add(product["product_url"])
    return findprice_products

def write_findprice_excel(products, output_path): 
    wb = openpyxl.Workbook() 
    ws = wb.active
    title = ["產品種類", "產品名稱", "產品價格", "產品網址", "售賣商城"]
    ws.append(title)

    for product in products:
        ws.append([
            product["target_item"],
            product["product_name"],
            product["product_price"],
            product["product_url"],
            product["merchant_name"]
        ])
    wb.save(output_path)

if __name__ == '__main__':
    findprice_products = crawl_findprice()
    write_findprice_excel(findprice_products, "findprice_products.xlsx")
