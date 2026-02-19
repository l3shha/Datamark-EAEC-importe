from fastapi import FastAPI, HTTPException, Request, UploadFile, File
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from typing import List
import tempfile
import os
from file_parser import parse_product_file, parse_codes_file

app = FastAPI(title="RF to RB Code Converter", description="Преобразование российских кодов маркировки в белорусский стандарт")

# Монтирование статических файлов
app.mount("/static", StaticFiles(directory="static"), name="static")

# Шаблоны
templates = Jinja2Templates(directory="templates")

class ConvertRequest(BaseModel):
    codes: List[str]

def convert_rf_to_rb(code: str) -> str:
    """
    Преобразует российский код маркировки в белорусский стандарт.
    Заменяет первую цифру после '21' с 5 (РФ) на 2 (Беларусь).
    
    Args:
        code (str): Исходный код маркировки
        
    Returns:
        str: Преобразованный код
    """
    # Найти позицию '21'
    pos = code.find('21')
    if pos == -1:
        # Если '21' не найдено, вернуть без изменений
        return code
    
    # Проверить, что после '21' есть хотя бы один символ и он равен '5'
    if pos + 2 < len(code) and code[pos + 2] == '5':
        # Заменить '5' на '2'
        return code[:pos + 2] + '2' + code[pos + 3:]
    else:
        # Если не '5', вернуть без изменений
        return code

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    """Главная страница с формой загрузки файлов"""
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/process", response_class=HTMLResponse)
async def process_files(
    request: Request,
    product_file: UploadFile = File(...),
    codes_file: UploadFile = File(...)
):
    """
    Обрабатывает загруженные файлы и преобразует коды.
    Возвращает страницу с результатом и ссылкой на скачивание.
    """
    try:
        # Проверка файлов
        if not product_file.filename or not codes_file.filename:
            raise HTTPException(status_code=400, detail="Необходимо загрузить оба файла")
        
        # Чтение содержимого файлов
        product_content = await product_file.read()
        codes_content = await codes_file.read()
        
        # Декодирование
        product_text = product_content.decode('utf-8')
        codes_text = codes_content.decode('utf-8')
        
        # Парсинг файлов
        products = parse_product_file(product_text)
        codes = parse_codes_file(codes_text)
        
        # Преобразование кодов
        converted_codes = [convert_rf_to_rb(code) for code in codes]
        
        # Создание файла для скачивания в static
        file_path = "static/converted_codes.txt"
        with open(file_path, 'w', encoding='utf-8') as f:
            for code in converted_codes:
                f.write(code + '\n')
        
        download_url = "/static/converted_codes.txt"
        
        return templates.TemplateResponse("result.html", {
            "request": request,
            "products_count": len(products),
            "codes_count": len(codes),
            "converted_count": len(converted_codes),
            "download_url": download_url
        })
        
    except Exception as e:
        return templates.TemplateResponse("error.html", {
            "request": request,
            "error": str(e)
        })

# Старые endpoints для API (опционально)
@app.post("/convert")
async def convert_codes(request: ConvertRequest):
    """
    Преобразует список кодов из РФ в РБ стандарт.
    
    Принимает JSON: {"codes": ["code1", "code2", ...]}
    Возвращает JSON: {"converted_codes": ["new_code1", "new_code2", ...]}
    """
    if not request.codes:
        raise HTTPException(status_code=400, detail="Список кодов не может быть пустым")
    
    converted_codes = [convert_rf_to_rb(code) for code in request.codes]
    
    return {"converted_codes": converted_codes}

@app.post("/convert/download")
async def convert_and_download(request: ConvertRequest):
    """
    Преобразует список кодов и возвращает файл для скачивания.
    
    Принимает JSON: {"codes": ["code1", "code2", ...]}
    Возвращает файл converted_codes.txt
    """
    if not request.codes:
        raise HTTPException(status_code=400, detail="Список кодов не может быть пустым")
    
    converted_codes = [convert_rf_to_rb(code) for code in request.codes]
    
    # Создать временный файл
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as f:
        for code in converted_codes:
            f.write(code + '\n')
        temp_file_path = f.name
    
    # Вернуть файл для скачивания
    response = FileResponse(
        path=temp_file_path,
        filename="converted_codes.txt",
        media_type='text/plain'
    )
    
    response.headers["Content-Disposition"] = "attachment; filename=converted_codes.txt"
    
    return response

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)