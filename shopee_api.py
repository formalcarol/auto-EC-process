import pandas as pd
import time
import requests
import hashlib
import hmac

"""
title, description, price, stock, images
商品A, 這是商品A, 499, 100, https://example.com/a1.jpg;https://example.com/a2.jpg
商品B, 這是商品B, 299, 50, https://example.com/b1.jpg
"""

# ---- 蝦皮 API 認證 ----
partner_id = "你的partner_id"
shop_id = "你的shop_id"
api_key = "你的api_key"
api_url = "https://partner.shopeemobile.com/api/v2/product/add_item"

# ---- 計算簽名函數 ----
def generate_signature(api_path, payload, api_key):
    message = api_path + ''.join([f'{k}{v}' for k,v in sorted(payload.items())])
    return hmac.new(api_key.encode(), message.encode(), hashlib.sha256).hexdigest()

# ---- 讀 Excel ----
df = pd.read_excel("products.xlsx")

for _, row in df.iterrows():
    images = row["images"].split(";")  # 如果多圖用分號分隔
    payload = {
        "partner_id": partner_id,
        "shop_id": shop_id,
        "timestamp": int(time.time()),
        "name": row["title"],
        "description": row["description"],
        "price": row["price"],
        "stock": row["stock"],
        "images": images,
        # 可加其他選填參數
    }
    payload["sign"] = generate_signature("/api/v2/product/add_item", payload, api_key)
    
    response = requests.post(api_url, json=payload)
    
    if response.status_code == 200 and response.json().get("msg") == "success":
        print(row["title"], "上架成功")
    else:
        print(row["title"], "上架失敗", response.text)
    
    time.sleep(1)  # 避免頻繁呼叫 API


