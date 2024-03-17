# eXOtic

Крестики-нолики в терминале на Python 3.10+.  
Для серверной части был использован `FastAPI`.

## Установка зависимостей 
```
pip install -r requirements.txt
```

## Запуск сервера
```
uvicorn --host <host> --port <port> src.server.main:app
```
Или `./run_server.sh` для запуска с значениями `host` и `port` по умолчанию. 

## Запуск клиента
```
python src/client/main.py <server_address>
```
Например, `python src/client/main.py http://127.0.0.1:8080`
