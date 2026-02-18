"""
Основной файл Flask приложения для ввода в оборот товаров из ЕАЭС
"""

import os
import logging
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from file_parser import parse_product_file, parse_codes_file, group_products_by_gtin, match_codes_to_products
from api_client import APIClient
from config import LOG_LEVEL, LOG_FILE
import traceback

# Настройка логирования
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE, encoding='utf-8'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# Инициализация API клиента
api_client = APIClient()


@app.route('/')
def index():
    """Главная страница"""
    return render_template('index.html')


@app.route('/api/process', methods=['POST'])
def process_files():
    """
    Основной эндпоинт для обработки файлов и выполнения процесса ввода в оборот
    
    Ожидает:
    - product_file: файл с описаниями товаров (GTIN; описание; количество)
    - codes_file: файл с неполными кодами маркировки
    
    Returns:
        JSON с результатами обработки
    """
    logger.info("Начало обработки файлов")
    try:
        # Проверка наличия файлов
        if 'product_file' not in request.files or 'codes_file' not in request.files:
            logger.warning("Не загружены оба файла")
            return jsonify({
                'success': False,
                'error': 'Необходимо загрузить оба файла'
            }), 400
        
        product_file = request.files['product_file']
        codes_file = request.files['codes_file']
        
        if product_file.filename == '' or codes_file.filename == '':
            logger.warning("Файлы не выбраны")
            return jsonify({
                'success': False,
                'error': 'Файлы не выбраны'
            }), 400
        
        logger.info(f"Загружены файлы: {product_file.filename}, {codes_file.filename}")
        
        # Чтение и парсинг файлов
        try:
            product_content = product_file.read().decode('utf-8')
            codes_content = codes_file.read().decode('utf-8')
        except UnicodeDecodeError as e:
            logger.error(f"Ошибка декодирования файлов: {e}")
            return jsonify({
                'success': False,
                'error': f'Ошибка чтения файлов: {str(e)}'
            }), 400
        
        try:
            products = parse_product_file(product_content)
            codes = parse_codes_file(codes_content)
            logger.info(f"Распарсено товаров: {len(products)}, кодов: {len(codes)}")
        except ValueError as e:
            logger.error(f"Ошибка парсинга файлов: {e}")
            return jsonify({
                'success': False,
                'error': f'Ошибка парсинга файлов: {str(e)}'
            }), 400
        
        # Группировка товаров по GTIN
        gtin_quantities = group_products_by_gtin(products)
        
        # Сопоставление кодов с товарами
        gtin_to_codes = match_codes_to_products(codes, products)
        
        # Определяем, сколько кодов нужно заказать для каждого GTIN
        codes_to_order = {}
        for gtin, quantity in gtin_quantities.items():
            existing_codes_count = len(gtin_to_codes.get(gtin, []))
            needed = quantity - existing_codes_count
            if needed > 0:
                codes_to_order[gtin] = needed
        
        result = {
            'success': True,
            'products_count': len(products),
            'codes_count': len(codes),
            'gtins': list(gtin_quantities.keys()),
            'codes_to_order': codes_to_order,
            'steps': []
        }
        
        # Шаг 1: Авторизация
        result['steps'].append({
            'step': 1,
            'name': 'Авторизация в API',
            'status': 'in_progress'
        })
        
        if not api_client.authenticate():
            logger.error("Ошибка авторизации в API")
            result['success'] = False
            result['steps'][-1]['status'] = 'failed'
            result['steps'][-1]['error'] = 'Ошибка авторизации. Проверьте учетные данные в .env файле'
            return jsonify(result), 500
        
        logger.info("Авторизация успешна")
        result['steps'][-1]['status'] = 'completed'
        
        # Шаг 2: Заказ недостающих кодов
        if codes_to_order:
            result['steps'].append({
                'step': 2,
                'name': 'Заказ недостающих кодов маркировки',
                'status': 'in_progress'
            })
            
            logger.info(f"Заказ кодов для GTIN: {list(codes_to_order.keys())}")
            order_id = api_client.order_codes(codes_to_order)
            
            if not order_id:
                logger.error("Не удалось создать заказ кодов")
                result['success'] = False
                result['steps'][-1]['status'] = 'failed'
                result['steps'][-1]['error'] = 'Ошибка заказа кодов'
                return jsonify(result), 500
            
            logger.info(f"Заказ создан: {order_id}")
            result['steps'][-1]['status'] = 'completed'
            result['steps'][-1]['order_id'] = order_id
            
            # Шаг 3: Ожидание выполнения заказа
            result['steps'].append({
                'step': 3,
                'name': 'Ожидание выполнения заказа',
                'status': 'in_progress',
                'order_id': order_id
            })
            
            logger.info(f"Ожидание выполнения заказа {order_id}")
            if not api_client.wait_for_order_completion(order_id):
                logger.error(f"Заказ {order_id} не выполнен в течение ожидаемого времени")
                result['success'] = False
                result['steps'][-1]['status'] = 'failed'
                result['steps'][-1]['error'] = 'Заказ не выполнен в течение ожидаемого времени'
                return jsonify(result), 500
            
            logger.info(f"Заказ {order_id} выполнен успешно")
            result['steps'][-1]['status'] = 'completed'
            
            # Шаг 4: Скачивание полных кодов
            result['steps'].append({
                'step': 4,
                'name': 'Скачивание полных кодов',
                'status': 'in_progress'
            })
            
            logger.info(f"Скачивание кодов для заказа {order_id}")
            new_codes = api_client.download_codes(order_id)
            
            if not new_codes:
                logger.error(f"Не удалось скачать коды для заказа {order_id}")
                result['success'] = False
                result['steps'][-1]['status'] = 'failed'
                result['steps'][-1]['error'] = 'Ошибка скачивания кодов'
                return jsonify(result), 500
            
            logger.info(f"Скачано кодов: {len(new_codes)}")
            result['steps'][-1]['status'] = 'completed'
            result['steps'][-1]['codes_count'] = len(new_codes)
            
            # Добавляем новые коды к существующим
            for gtin, needed in codes_to_order.items():
                if gtin not in gtin_to_codes:
                    gtin_to_codes[gtin] = []
                # Распределяем новые коды по GTIN (упрощенная логика)
                # В реальности нужно более точное сопоставление
                gtin_to_codes[gtin].extend(new_codes[:needed])
                new_codes = new_codes[needed:]
        
        # Шаг 5: Отправка отчетов о вводе в оборот
        result['steps'].append({
            'step': 5,
            'name': 'Отправка отчетов о вводе в оборот',
            'status': 'in_progress',
            'reports': []
        })
        
        report_ids = []
        for gtin, codes_list in gtin_to_codes.items():
            if codes_list:
                logger.info(f"Отправка отчета для GTIN {gtin} ({len(codes_list)} кодов)")
                report_id = api_client.submit_import_report(codes_list, gtin)
                if report_id:
                    logger.info(f"Отчет создан: {report_id} для GTIN {gtin}")
                    report_ids.append({
                        'gtin': gtin,
                        'report_id': report_id,
                        'codes_count': len(codes_list)
                    })
                else:
                    logger.warning(f"Не удалось создать отчет для GTIN {gtin}")
        
        if not report_ids:
            logger.error("Не удалось отправить ни одного отчета")
            result['success'] = False
            result['steps'][-1]['status'] = 'failed'
            result['steps'][-1]['error'] = 'Не удалось отправить отчеты'
            return jsonify(result), 500
        
        result['steps'][-1]['reports'] = report_ids
        result['steps'][-1]['status'] = 'completed'
        
        # Шаг 6: Отслеживание статуса отчетов
        result['steps'].append({
            'step': 6,
            'name': 'Отслеживание статуса отчетов',
            'status': 'in_progress'
        })
        
        logger.info("Ожидание завершения отчетов")
        all_reports_completed = True
        for report_info in report_ids:
            logger.info(f"Проверка статуса отчета {report_info['report_id']}")
            if not api_client.wait_for_report_completion(report_info['report_id']):
                logger.warning(f"Отчет {report_info['report_id']} не завершен")
                all_reports_completed = False
                break
        
        if all_reports_completed:
            logger.info("Все отчеты успешно завершены")
            result['steps'][-1]['status'] = 'completed'
        else:
            logger.warning("Некоторые отчеты не завершены")
            result['steps'][-1]['status'] = 'warning'
            result['steps'][-1]['message'] = 'Некоторые отчеты не завершены'
        
        result['final_status'] = 'completed' if all_reports_completed else 'partial'
        
        logger.info("Обработка завершена успешно")
        return jsonify(result), 200
        
    except Exception as e:
        error_trace = traceback.format_exc()
        logger.error(f"Критическая ошибка: {e}\n{error_trace}")
        return jsonify({
            'success': False,
            'error': str(e),
            'trace': error_trace
        }), 500


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
