# FastAPI app for DocuStruct
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
from typing import Dict, Any
from . import parser
import asyncio

app = FastAPI(title='DocuStruct API')

# simple health
@app.get('/health')
async def health():
    return {'status': 'ok'}

@app.post('/analyze')
async def analyze(file: UploadFile = File(...)):
    if file.content_type != 'application/pdf':
        raise HTTPException(status_code=400, detail='Only application/pdf supported')
    contents = await file.read()
    # enforce size limit (50 MB)
    if len(contents) > 50 * 1024 * 1024:
        raise HTTPException(status_code=413, detail='File too large (max 50 MB)')
    try:
        # call parser - this is synchronous and may block; for heavier loads, run in threadpool
        loop = asyncio.get_running_loop()
        result = await loop.run_in_executor(None, parser.analyze_pdf_bytes, contents)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    return JSONResponse(content=result)
