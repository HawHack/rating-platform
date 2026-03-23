веб-платформа для учета активности участников молодежного парламента и кадрового резерва.

## Возможности проекта

- Регистрация и авторизация пользователей
- Роли: участник, организатор, наблюдатель (кадровая служба)
- Создание мероприятий организаторами
- Запись участников на мероприятия
- Подтверждение участия организатором
- Начисление баллов
- Глобальный рейтинг участников
- Профиль участника с портфолио и уровнями
- Профиль организатора с отзывами и рейтингом доверия
- Дашборд активности
- Страница кадрового инспектора с фильтрами
- Отчет по кандидату
- Простая QR-ready check-in логика
- Django Admin для управления

Технологии

- Python 3.11+
- Django 6.0.3
- SQLite
- Bootstrap 5
- Chart.js

 Установка и запуск

 1. Клонировать репозиторий

```bash
git clone  https://github.com/HawHack/rating-platform.git
cd rating-platform
```
2. Создать виртуальное окружение
Windows (PowerShell)
PowerShell

python -m venv venv
.\venv\Scripts\Activate.ps1
Если PowerShell блокирует активацию, выполни:
PowerShell
Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned
Windows (Command Prompt)
cmd
python -m venv venv
venv\Scripts\activate.bat

3. Установить зависимости
Bash
pip install -r requirements.txt

4. Применить миграции
Bash
python manage.py makemigrations
python manage.py migrate
5. Создать суперпользователя (админ)
Bash
python manage.py createsuperuser
6. (Опционально) Загрузить тестовые данные
Bash
python manage.py seed_data
7. Запустить сервер разработки
Bash
python manage.py runserver

Открой в браузере:

Сайт: http://127.0.0.1:8000/
Админка: http://127.0.0.1:8000/admin/
Тестовые аккаунты (после команды seed_data)
Роль	Логин	Пароль
Организатор	organizer1	12345678Qq
Участник	participant1	12345678Qq
Наблюдатель	observer1	12345678Qq
Основные страницы
Главная: /
Мероприятия: /events/
Рейтинг: /ratings/
Профиль: /users/profile/
Инспектор кадрового резерва: /inspector/
