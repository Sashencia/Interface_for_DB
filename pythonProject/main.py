
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
    cursor.execute(request) #Выполняет действие
    data = []
    if 'SELECT' in request:
    # Идем по массиву строчек селекта (первый элемент массива - первая строчка таблицы, и тд)
    # В общем, переводим результаты селекта в питон
        for row in cursor:
            data.append(row)

        cursor.close()
    else:
        # Просто выполняем запросы, такие как инсерт или делит
        cnxn.commit()  # Сохраняе результат ти отправляем его в базу данных
        cursor.close()  # Разрываем соединение с базой данных
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
            if res_email[0][1] == 0:
                #Пользователь найден и редиректом переходим в его профиль
                return redirect("/profile_normal")
            else:
                return redirect("/profile_admin")
        else:
            error = "Пользователя с таким email'ом не существует"
        print(res_email)
        print(res_passw)
    return render_template('main_page.html', error = error)

@app.route('/delete_user/<int:id_>', methods=['POST', 'GET'])
def delete_user(id_):
    if current_user["id"] != 0:
        user = db_connect(f"SELECT * FROM Users WHERE [Users_id] = '{current_user['id']}'")
        print(user)
        if user[0][1] == 1:
            db_connect(f"DELETE FROM Users WHERE [Users_id] = '{id_}'")
            return redirect('/profile_admin')
    return redirect('/')

@app.route('/add_user', methods=['POST', 'GET'])
def add_user():
    if current_user["id"] != 0:
        user = db_connect(f"SELECT * FROM Users WHERE [Users_id] = '{current_user['id']}'")
        print(user)
        if user[0][1] == 1:
            if request.method == 'POST':
                print(request.form)
                data = request.form
                print(data['lastName'])
                db_connect(f"INSERT INTO Users (admin_check, passw, surname, [name]," +
                           f" patronymic, sex, phone_number, email_address," +
                           f" snils, inn, medical_policy, fio) VALUES" +
                           f" ({0 if data['status'] == 'user' else 1},"
                           f"   '{data['passw']}',"
                           f" '{data['lastName']}',"
                           f" '{data['firstName']}',"
                           f" '{data['patronymic']}',"
                           f" {0 if data['gender'] == 'female' else 1},"
                           f" '{data['phone']}',"
                           f" '{data['email']}',"
                           f" '{data['snils']}', "
                           f" '{data['inn']}',"
                           f" '{data['medicalRecords']}',"
                           f" '{data['lastName'] + ' ' + data['firstName'] + ' ' + data['patronymic']}')")
                db_connect(f"INSERT INTO Passport () VALUES" +
                           f" ({})")
                return redirect('/profile_admin')
    return redirect('/')

@app.route('/profile_normal', methods=['POST', 'GET'])
def profile():
    if current_user["id"] != 0:
        #Возвращаем авторизованного чела по айди
        user = db_connect(f"SELECT * FROM Users WHERE [Users_id] = '{current_user['id']}'")
        #documents = db_connect(f"SELECT * FROM Documents WHERE [id] = '{current_user['id']}'")
        department = db_connect(f"SELECT * FROM Department WHERE [id] = '{current_user['id']}'")
        #passport = db_connect(f"SELECT * FROM Passport WHERE [id] = '{current_user['id']}'")
        # med_police = db_connect(f"SELECT * FROM medical_information WHERE [id] = '{current_user['id']}'")
        education = db_connect(f"SELECT * FROM Diploma WHERE [id] = '{current_user['id']}'")
        grade = db_connect(f"SELECT * FROM Grade WHERE [id] = '{current_user['id']}'")
        depart_position = db_connect(f"SELECT * FROM Position WHERE [Position_id] = '{current_user['id']}'")
        diploma = db_connect(f"SELECT * FROM Diploma WHERE [id] = '{current_user['id']}'")
        achievments = db_connect(f"SELECT * FROM Review WHERE [id] = '{current_user['id']}'")
        print(user)
        #print(documents)
        print(department)
        #print(passport)
        print(grade)
        #Передаем в хтмл найденного пользователя
        return render_template('profile_normal.html', user = user[0],
                               department = department[0], education = education[0],
                               grade = grade[0], depart_position=depart_position[0], diploma = diploma[0], achievments = achievments[0])
    return redirect("/")

@app.route('/profile_user/<int:id_>', methods=['POST', 'GET'])
def profile_user(id_):
    if current_user["id"] != 0:
        # Возвращаем авторизованного чела по айди
        user = db_connect(f"SELECT * FROM Users WHERE [Users_id] = '{current_user['id']}'")
        # Проверяем, что авторизованный пользователь - админ
        if user[0][1] == 1:
            # Подгружаем информацию о юзере, с переданным айдишником id_
            user_t = db_connect(f"SELECT * FROM Users WHERE [Users_id] = '{id_}'")
            # documents = db_connect(f"SELECT * FROM Documents WHERE [id] = '{id_}'")
            department = db_connect(f"SELECT * FROM Department WHERE [id] = '{id_}'")
            # passport = db_connect(f"SELECT * FROM Passport WHERE [id] = '{current_user['id']}'")
            # med_police = db_connect(f"SELECT * FROM medical_information WHERE [id] = '{id_}'")
            education = db_connect(f"SELECT * FROM Diploma WHERE [id] = '{id_}'")
            grade = db_connect(f"SELECT * FROM Grade WHERE [id] = '{id_}'")
            depart_position = db_connect(f"SELECT * FROM Position WHERE [Position_id] = '{id_}'")
            diploma = db_connect(f"SELECT * FROM Diploma WHERE [id] = '{id_}'")
            achievments = db_connect(f"SELECT * FROM Review WHERE [id] = '{id_}'")
            return render_template('profile_normal.html', user = user_t[0],
                               department = department[0], education = education[0],
                               grade = grade[0], depart_position=depart_position[0], diploma = diploma[0], achievments = achievments[0])
    return redirect("/")

@app.route('/profile_admin', methods=['POST', 'GET'])
def profile_admin():
    if current_user["id"] != 0:
        #Возвращаем авторизованного чела по айди
        user = db_connect(f"SELECT * FROM Users WHERE [Users_id] = '{current_user['id']}'")
        print(user)
        if user[0][1] == 1:
            if request.method == 'POST':
                data = request.json
                search_term = data['term']
                print(search_term)
                users = db_connect(f"SELECT * FROM Users WHERE [fio] LIKE '%{search_term}%'")
                print(users)
                return render_template('profile_admin.html', user=user[0], users=users)
            #Передаем в хтмл найденного пользователя
            return render_template('profile_admin.html', user = user[0], users=[])
        else:
            return redirect("/")
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













current_user = {"is_authenticated": True, "id": 2}

app.run()
