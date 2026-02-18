"""
Модуль для парсинга файлов из РФ
- Файл 1: GTIN; описание; количество
- Файл 2: неполные коды маркировки
"""


def parse_product_file(file_content: str) -> list:
    """
    Парсит файл с описаниями товаров (Файл 1)
    Формат: GTIN; описание; количество
    
    Returns:
        list: Список словарей с ключами: gtin, description, quantity
    """
    products = []
    lines = file_content.strip().split('\n')
    
    for line_num, line in enumerate(lines, 1):
        line = line.strip()
        if not line:
            continue
            
        parts = line.split(';')
        if len(parts) < 3:
            raise ValueError(f"Неверный формат строки {line_num}: ожидается формат 'GTIN; описание; количество'")
        
        gtin = parts[0].strip()
        description = parts[1].strip()
        try:
            quantity = int(parts[2].strip())
        except ValueError:
            raise ValueError(f"Неверное количество в строке {line_num}: {parts[2]}")
        
        products.append({
            'gtin': gtin,
            'description': description,
            'quantity': quantity
        })
    
    return products


def parse_codes_file(file_content: str) -> list:
    """
    Парсит файл с кодами маркировки (Файл 2)
    Формат: одна строка = один неполный код
    
    Returns:
        list: Список неполных кодов маркировки
    """
    codes = []
    lines = file_content.strip().split('\n')
    
    for line in lines:
        code = line.strip()
        if code:
            codes.append(code)
    
    return codes


def group_products_by_gtin(products: list) -> dict:
    """
    Группирует товары по GTIN для заказа кодов
    
    Args:
        products: Список товаров из parse_product_file
        
    Returns:
        dict: {gtin: total_quantity}
    """
    grouped = {}
    for product in products:
        gtin = product['gtin']
        if gtin not in grouped:
            grouped[gtin] = 0
        grouped[gtin] += product['quantity']
    
    return grouped


def match_codes_to_products(codes: list, products: list) -> dict:
    """
    Сопоставляет коды маркировки с товарами по GTIN
    
    Args:
        codes: Список неполных кодов из parse_codes_file
        products: Список товаров из parse_product_file
        
    Returns:
        dict: {gtin: [список кодов для этого GTIN]}
    """
    # Извлекаем GTIN из кодов (первые 14 цифр после 01)
    gtin_to_codes = {}
    
    for code in codes:
        # Формат кода: 01<GTIN>21<serial>...
        # GTIN обычно начинается после "01" и имеет длину 14 символов
        if code.startswith('01'):
            gtin = code[2:16]  # Извлекаем GTIN (14 символов)
            if gtin not in gtin_to_codes:
                gtin_to_codes[gtin] = []
            gtin_to_codes[gtin].append(code)
    
    return gtin_to_codes
