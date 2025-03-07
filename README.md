# ЗАКОН ПЕРУНА
- НЕ ПУШИТЬ НЕПОТРЕБСТВО В main
- СПИСОК ЕРЕСИ (НЕ ПУШИТЬ НИКУДА):  
- - `.idea`
- - `venv`
- - `.venv`
- - `__pycache__`
- - `.pyc`

# План работ
- Страница профиля и взаимодейтсвия с ней
- БД
- Страница авторизации и регистрации
- welcome page
- Страница оплаты


# Инструкция по постройке Гипербореи:
- ВОЙТИ В ХРАМ ПЕРУНА:  
`git init`  
`git config --global user.email example@allah.com`  
`git config --local user.email example@allah.com`  

- ЗАМОЛИТЬ ИЗМЕНЕНИЯ ПЕРЕД ВЕЛЕСОМ:  
`git add --all`  
`git commit -m "Инша Аллах Сообщение коммита"`

- ПРИВЯЗАТЬ К origin ССЫЛКУ:  
`git remote add origin https://gitlab.informatics.ru/link-to-project.git`

- ЕСЛИ ПУШИШЬ 1-ЫЙ РАЗ:
`git push --set-upstream origin master:branch_name`

- ПОСЛЕДУЮЩИЕ РАЗЫ:
`git push origin master:branch_name`  
- ЕСЛИ ЗАПОР (ОШИБКА):
`git push --set-upstream --force origin master:branch_name`
<br>
- ЕСЛИ ПОНОС (ЛИШНЯЯ ВЕТКА):  
`git push --delete origin branch_name`  
`ИЛИ git push -d origin branch_name`  
`ИЛИ git push origin :branch_name`