# uvicorn main:app --reload
# http://127.0.0.1:8000/docs

from fastapi import FastAPI, File, UploadFile, HTTPException, Path
import pandas as pd
import io

app = FastAPI()
excel_df = None

@app.post("/upload-excel/")
async def upload_excel(file: UploadFile = File(...)):
    global excel_df
    
    if not (file.filename.endswith(".xlsx") or file.filename.endswith(".xls")):
        raise HTTPException(
            status_code=400,
            detail="無效的檔案類型，請上傳 .xlsx 檔案"
        )

    try:
        file_content = await file.read()
        excel_data = io.BytesIO(file_content)
        
        df = pd.read_excel(excel_data, sheet_name=0, header=0)
        df.dropna(how='all', inplace=True)
        df = df.where(pd.notna(df), None)
        data = df.to_dict(orient="records")
        excel_df = df

        return {
            "filename": file.filename,
            "data_count": len(data),
            "data": data,
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"處理檔案時發生錯誤: {e}"
        )
    
@app.get("/query/")
async def query_by_category(category: str):
    if excel_df is None:
        raise HTTPException(status_code=400, detail="請先上傳 Excel 檔案")

    col_name = excel_df.columns[0]

    result = excel_df[excel_df[col_name] == category]

    return {
        "category": category,
        "count": len(result),
        "data": result.to_dict(orient="records"),
    }

