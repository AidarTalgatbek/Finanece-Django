# Finance Django Project

Простой проект на Django для управления финансами.

## Установка

1. Клонируйте репозиторий:
   ```sh
   git clone https://github.com/AidarTalgatbek/Finanece-Django.git
   cd Finanece-Django
   ```

2. Создайте виртуальное окружение и активируйте его:
   ```sh
   python -m venv venv
   source venv/bin/activate  # Для Linux/macOS
   venv\Scripts\activate  # Для Windows
   ```

3. Установите зависимости:
   ```sh
   pip install -r requirements.txt
   ```

4. Примените миграции:
   ```sh
   python manage.py migrate
   ```

5. Создайте суперпользователя (по желанию):
   ```sh
   python manage.py createsuperuser
   ```

6. Запустите сервер:
   ```sh
   python manage.py runserver
   ```

## Использование

- Открыть в браузере: `http://127.0.0.1:8000/`
- Админ-панель: `http://127.0.0.1:8000/admin/`

## Контакты

Если есть вопросы или предложения, пишите в Issues или создавайте Pull Request.

