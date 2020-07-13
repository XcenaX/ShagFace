@ECHO OFF
start cmd.exe /C "python manage.py runserver && cd D:\D1\ && D:"
start C:\"Program Files (x86)"\Google\Chrome\Application\chrome.exe "http://127.0.0.1:8000/"