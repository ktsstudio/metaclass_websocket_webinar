# Пишем websocket-сервер для геолокации на python asyncio

[Ссылка на курс](https://slurm.io/asyncio-with-kts?utm_source=metaclass_github)

[Ссылка на запись вебинара](https://www.youtube.com/watch?v=Iwj8Kb7EItY)

[Ссылка на демонстрацию](https://lms.metaclass.kts.studio/websocket_webinar/)

## Как запустить локально?
1. Настроить окружение
```shell
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```
2. [Получить API токен](https://yandex.ru/dev/maps/jsapi/doc/2.1/quick-start/index.html#get-api-key)
3. Заменить API токен в index.html
   1. Найти в client/index.html текст `apikey=${CONNECT_TOKEN}`
   2. Вставить свой токен вместо `${CONNECT_TOKEN}`
4. Запустить `python main.py`
5. Открыть браузер на http://localhost:8000 


## Как тестировать?
Можно открыть два браузера Chrome: в обычном и приватном режиме. В одном из браузеров не разрешать 
доступ к геопозиции - это приведет к появлению кнопки "Установить случайную позицию". При нажатии на эту
кнопку изменения геопозиции должны появляться в обоих браузерах.  