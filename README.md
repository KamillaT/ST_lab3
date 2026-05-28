# ST_lab3: Selenium tests for Tutu.ru

Автотесты для лабораторной работы 3, вариант 1230.

## Запуск

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pytest -v --browser chrome --headless
pytest -v --browser firefox --headless
```

Позитивная авторизация читает логин и пароль из локального `.env`, который игнорируется git:

```env
email="email@example.com"
password="password"
```

Также можно переопределить значения переменными окружения:

```bash
TUTU_LOGIN="email@example.com" TUTU_PASSWORD="password" pytest -v --browser chrome --headless -k successful_authorization
```

Вход по почте и коду из письма запускается интерактивно. Тест отправит код и попросит ввести его в терминале:

```bash
TUTU_LOGIN="email@example.com" TUTU_INTERACTIVE_AUTH=1 pytest -s -v --browser chrome -k email_code
```

Авиа-поиск можно прогнать отдельно. Без `--headless` будет видно, как Selenium заполняет маршрут, даты туда/обратно, пассажиров и проверяет неполные формы:

```bash
pytest -s -v --browser chrome -k avia
```

Ж/Д позитивные и негативные сценарии поиска:

```bash
pytest -s -q --browser chrome -k "tc02 or tc03"
```

Новые проверки выдачи, фильтров, подробностей и перехода к оформлению по разделам можно запустить видимо, с пошаговыми логами:

```bash
pytest -s -q --browser chrome -k "tc24 or tc25 or tc26 or tc27 or tc28 or tc29 or tc30 or tc31 or tc32 or tc33"
```

Ключевой проверенный набор для авиа и Ж/Д:

```bash
pytest -s -q --browser chrome --headless -k "tc02 or tc03 or tc24 or tc25"
```

В логах печатаются бизнес-шаги вида `[STEP 19:22:51] AviaPage: открываю раздел авиабилетов`. Перед кликами добавлена пауза 1 секунда, чтобы действия были читаемее и стабильнее на динамических страницах.

Отчёт: `REPORT.md`.
