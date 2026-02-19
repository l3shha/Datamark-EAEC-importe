import requests

# URL сервера
base_url = "http://localhost:8000"

# Тестовые коды из ваших файлов
test_codes = [
    "0104660575291478215GQNjOY>S3!sQ",
    "0104660575291485215&xE6jq>TVW<a",
    "0104811644010685215mpid7gn7wzu[GS]91FFD0[GS]92dGVzdDk5..."
]

# Тест POST /convert
print("Тестирование /convert endpoint:")
response = requests.post(f"{base_url}/convert", json={"codes": test_codes})
if response.status_code == 200:
    result = response.json()
    print("Успешно!")
    for original, converted in zip(test_codes, result["converted_codes"]):
        print(f"Original: {original}")
        print(f"Converted: {converted}")
        print("---")
else:
    print(f"Ошибка: {response.status_code} - {response.text}")

# Тест POST /convert/download
print("\nТестирование /convert/download endpoint:")
response = requests.post(f"{base_url}/convert/download", json={"codes": test_codes})
if response.status_code == 200:
    print("Успешно! Файл получен.")
    print("Содержимое файла:")
    print(response.text)
else:
    print(f"Ошибка: {response.status_code} - {response.text}")