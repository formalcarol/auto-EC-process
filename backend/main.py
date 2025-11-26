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
    if category == "" or category.lower() == "全部":
        result = excel_df
    else:
        result = excel_df[excel_df["產品種類"] == category]
    return {"category": category, "count": len(result), "data": result.to_dict(orient="records")}