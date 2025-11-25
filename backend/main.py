from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
import io

app = FastAPI()
excel_df = None
listed_products = []

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/upload-excel/")
async def upload_excel(file: UploadFile = File(...)):
    global excel_df
    if not (file.filename.endswith(".xlsx") or file.filename.endswith(".xls")):
        raise HTTPException(status_code=400, detail="無效的檔案類型，請上傳 .xlsx 檔案")
    try:
        file_content = await file.read()
        excel_data = io.BytesIO(file_content)
        df = pd.read_excel(excel_data, sheet_name=0, header=0)
        df.dropna(how='all', inplace=True)
        df = df.where(pd.notna(df), None)
        excel_df = df
        return {"filename": file.filename, "data_count": len(df), "data": df.to_dict(orient="records")}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"處理檔案時發生錯誤: {e}")

@app.get("/query/")
async def query_by_category(category: str):
    if excel_df is None:
        raise HTTPException(status_code=400, detail="請先上傳 Excel 檔案")
    col_name = excel_df.columns[0]
    result = excel_df[excel_df[col_name] == category]
    return {"category": category, "count": len(result), "data": result.to_dict(orient="records")}

@app.post("/mock-upload/")
async def mock_upload():
    global listed_products
    if excel_df is None:
        raise HTTPException(status_code=400, detail="請先上傳 Excel 檔案")
    
    for _, row in excel_df.iterrows():
        # listed_products.append({
        #     "product_name": row["產品名稱"],
        #     "product_category": row["產品種類"],
        #     "product_price": row["產品價格"],
        #     "product_url": row["產品網址"],
        #     "merchant_name": row["售賣商城"]
        # })
        listed_products.append({
            "name": row["產品名稱"],
            "category": row["產品種類"],
            "price": row["產品價格"],
            "profit_margin": 0  # 先給預設
        })

    return {"message": f"{len(listed_products)} products now listed", "listed_products": listed_products}

@app.get("/get-listed-products/")
async def get_listed_products():
    return {"listed_products": listed_products}
