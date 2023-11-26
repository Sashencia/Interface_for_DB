
import pyodbc

'''Библиотека FLASK'''


from flask import Flask, render_template, redirect, request
import requests

'''Запуск приложения FLASK'''


app = Flask(__name__)

'''Настройка приложения для того, чтобы можно было сохранять русские символы в json'''


app.config.update(
    JSON_AS_ASCII=False
)

'''Эта настройка защитит наше приложение от межсайтовой подделки запросов'''


app.config['SECRET_KEY'] = 'secret_key'


def db_connect(request):
    cnxn = pyodbc.connect("Driver={SQL Server};"
                          "Server=DESKTOP-NP32SPK;"
                          "Database=CRM2;"
                          "Trusted_Connection=yes;")

    cursor = cnxn.cursor()
    cursor.execute(request)

    data = []
    for row in cursor:
        data.append(row)
    cursor.close()
    return data

#Что происходит на пути "/", т.е. на главной странице
@app.route('/', methods=['POST', 'GET'])
def main_page():
    error = ""
    #Проверяем, что метод "пост", т.е. что пользователь ввел данные
    if request.method == 'POST':
        print(request.form['email_address'])
        #Функция передачи запроса в скл
        res = db_connect(f"SELECT * FROM Users WHERE [email_address] = '{request.form['email_address']}'")
        #Проверка, что пользователь существует
        if res:
            current_user["is_authenticated"] = True
            current_user["id"] = res[0][0]
            #Пользователь найден и редиректом переходим в его профиль
            return redirect("/profile")
        else:
            error = "Пользователя с таким email'ом не существует"
        print(res)
    return render_template('main_page.html', error = error)

@app.route('/profile', methods=['POST', 'GET'])

def profile():
    if current_user["id"] != 0:
        #Возвращаем авторизованного чела по айди
        user = db_connect(f"SELECT * FROM Users WHERE [Users_id] = '{current_user['id']}'")
        print(user)
        #Передаем в хтмл найденного пользователя
        return render_template('profile.html', user = user[0])
    return redirect("/")

current_user = {"is_authenticated": False, "id": 0}




app.run()
