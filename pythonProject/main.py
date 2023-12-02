
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
                          "Server=ALEKSANDRA;"
                          "Database=CRM1;"
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
        print(request.form['password'])
        #Функция передачи запроса в скл
        res_email = db_connect(f"SELECT * FROM Users WHERE [email_address] = '{request.form['email_address']}'")
        res_passw = db_connect(f"SELECT * FROM Users WHERE [passw] = '{request.form['password']}'")
        #Проверка, что пользователь существует
        if res_email and res_passw:
            current_user["is_authenticated"] = True
            current_user["id"] = res_email[0][0]
            #Пользователь найден и редиректом переходим в его профиль
            return redirect("/profile")
        else:
            error = "Пользователя с таким email'ом не существует"
        print(res_email)
        print(res_passw)
    return render_template('main_page.html', error = error)

@app.route('/profile', methods=['POST', 'GET'])
def profile():
    if current_user["id"] != 0:
        #Возвращаем авторизованного чела по айди
        user = db_connect(f"SELECT * FROM Users WHERE [Users_id] = '{current_user['id']}'")
        #documents = db_connect(f"SELECT * FROM Documents WHERE [id] = '{current_user['id']}'")
        department = db_connect(f"SELECT * FROM Department WHERE [id] = '{current_user['id']}'")
        #passport = db_connect(f"SELECT * FROM Passport WHERE [id] = '{current_user['id']}'")
        med_police = db_connect(f"SELECT * FROM medical_information WHERE [id] = '{current_user['id']}'")
        education = db_connect(f"SELECT * FROM Diploma WHERE [id] = '{current_user['id']}'")
        grade = db_connect(f"SELECT * FROM Grade WHERE [id] = '{current_user['id']}'")
        depart_position = db_connect(f"SELECT * FROM Position WHERE [Position_id] = '{current_user['id']}'")
        diploma = db_connect(f"SELECT * FROM Diploma WHERE [id] = '{current_user['id']}'")
        achievments = db_connect(f"SELECT * FROM Review WHERE [id] = '{current_user['id']}'")
        print(user)
        #print(documents)
        print(department)
        #print(passport)
        print(med_police)
        print(grade)
        #Передаем в хтмл найденного пользователя
        return render_template('profile.html', user = user[0], med_police = med_police[0],
                               department = department[0], education = education[0],
                               grade = grade[0], depart_position=depart_position[0], diploma = diploma[0], achievments = achievments[0])
    return redirect("/")


@app.route('/test', methods=['POST', 'GET'])
def test():
    # Передаем в хтмл найденного пользователя
    return render_template('test.html')

@app.route('/logout', methods=['POST', 'GET'])
def logout():
    current_user["is_authenticated"] = False
    current_user["id"] = 0
    return redirect("/")













current_user = {"is_authenticated": False, "id": 0}
app.run()
