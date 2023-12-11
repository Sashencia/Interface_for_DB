import pyodbc
import main
'''Библиотека FLASK'''

from flask import Flask, render_template, redirect, request, jsonify

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
    cursor.execute(request)  # Выполняет действие
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

# Функция для подключения к базе данных
# def db_connect(request):
#     cnxn = pyodbc.connect("Driver={SQL Server};"
#                           "Server=ALEKSANDRA;"
#                           "Database=CRM1;"
#                           "Trusted_Connection=yes;")
#
#     cursor = cnxn.cursor()
#     cursor.execute(request)
#     data = []
#     if 'SELECT' in request:
#         data = [row for row in cursor]
#         description = cursor.description
#         cursor.close()
#     else:
#         cnxn.commit()
#         cursor.close()
#
#     cnxn.close()  # Закрываем соединение с базой данных
#     return data, description if 'SELECT' in request else None





# Что происходит на пути "/", т.е. на главной странице
@app.route('/', methods=['POST', 'GET'])
def main_page():
    error = ""
    # Проверяем, что метод "пост", т.е. что пользователь ввел данные
    if request.method == 'POST':
        print(request.form['email_address'])
        print(request.form['password'])
        # Функция передачи запроса в скл
        res_email = db_connect(f"SELECT * FROM Users WHERE [email_address] = '{request.form['email_address']}' AND [passw] = '{request.form['password']}'")
        #res_passw = db_connect(f"SELECT * FROM Users WHERE '")
        print(res_email)
        # Проверка, что пользователь существует
        if res_email and len(res_email) > 0:
            current_user["is_authenticated"] = True
            current_user["id"] = res_email[0][0]
            if res_email[0][1] == 0:
                # Пользователь найден и редиректом переходим в его профиль
                return redirect("/profile_normal")
            else:
                return redirect("/profile_admin")
        else:
            error = "Пользователя с таким email'ом или паролем не существует"
        print(res_email)
        #print(res_passw)
    return render_template('main_page.html', error=error)


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
                db_connect(f"INSERT INTO Passport (series, number, surname, [name], patronymic, dob, city_of_birth, " +
                           f"issued_by, issue_date, department_number, registration) VALUES" +
                           f" ('{data['series']}', "
                           f"  '{data['number']}',"
                           f" '{data['lastName']}',"
                           f" '{data['firstName']}',"
                           f" '{data['patronymic']}',"
                           f"   '{data['dob']}',"
                           f"   '{data['city_of_birth']}',"
                           f"   '{data['issued_by']}',"
                           f"   '{data['issue_date']}',"
                           f"   '{data['department_number']}',"
                           f"   '{data['registration']}')")
                # db_connect(f"INSERT INTO Department (department_name, [address], phone_number, email," +
                #            f" header_of_depart_id, employees_list, department_budget, amount_of_projects, " +
                #            f"creating_date, activities_description, exact_grade_id) VALUES" +)
                # db_connect(f"INSERT INTO Education (series, number, surname, [name], patronymic, dob, city_of_birth, " +
                #            f"issued_by, issue_date, department_number, registration) VALUES" +)
                return redirect('/profile_admin')
    return redirect('/')


from flask import jsonify

def db_get_all_tables():
    request = 'SELECT * FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_TYPE = \'BASE TABLE\''
    tables = db_connect(request)
    return tables

@app.route('/get_all_tables', methods=['POST'])
def get_all_tables():
    all_tables = db_get_all_tables()  # Предположим, что у вас есть метод db_get_all_tables в классе, который обращается к базе данных и возвращает результат запроса

    serialized_tables = []

    for table in all_tables:
        # Преобразовать каждую строку в словарь
        serialized_row = {}
        for key, value in table.items():
            # Преобразовать Decimal в float (если это необходимо)
            if isinstance(value, Decimal):
                value = float(value)
            serialized_row[key] = value
        serialized_tables.append(serialized_row)

    return jsonify(all_tables=serialized_tables)


@app.route('/profile_normal', methods=['POST', 'GET'])
def profile():
    if current_user["id"] != 0:
        # Возвращаем авторизованного чела по айди
        user = db_connect(f"SELECT * FROM Users WHERE [Users_id] = '{current_user['id']}'")
        # # Возвращаем авторизованного человека по айди
        # user_data = db_connect(f"SELECT * FROM Users WHERE [Users_id] = '{current_user['id']}'")
        # if not user_data:
        #     # Пользователь с текущим id не найден
        #     return redirect("/")

        # user = user_data[0]
        department = db_connect(f"SELECT * FROM Department WHERE [id] = '{current_user['id']}'")
        education = db_connect(f"SELECT * FROM Diploma WHERE [id] = '{current_user['id']}'")
        grade = db_connect(f"SELECT * FROM Grade WHERE [id] = '{current_user['id']}'")
        depart_position = db_connect(f"SELECT * FROM Position WHERE [Position_id] = '{current_user['id']}'")
        diploma = db_connect(f"SELECT * FROM Diploma WHERE [id] = '{current_user['id']}'")
        achievments = db_connect(f"SELECT * FROM Review WHERE [id] = '{current_user['id']}'")
        # conn = db_connect()
        # cursor = conn.cursor()
        # cursor.execute('SELECT * FROM Passport')
        # # Получение заголовков столбцов
        # columns = [column[0] for column in cursor.description]
        # # Получение данных из таблицы
        # data = cursor.fetchall()
        # conn.close()
        #return render_template('profile_normal.html', columns=columns, data=data)
        print(user)
        if request.method == 'POST':
            data = request.form
            print(data)
            #return jsonify({"status": "success"})
            search_term = data['term']
            print("Zahodit")

            users = db_connect(f"SELECT * FROM Users WHERE [fio] LIKE '%{search_term}%'")

            # Здесь вы можете добавить код для получения всех таблиц из базы данных
            # Предположим, что у вас есть функция db_get_all_tables, которая возвращает список таблиц
            all_tables = db_get_all_tables()

            return render_template('profile_normal.html', user=user[0],
                                   department=department[0], education=education[0],
                                   grade=grade[0], depart_position=depart_position[0],
                                   diploma=diploma[0], achievments=achievments[0],
                                   users=users, all_tables=all_tables)
        # Передаем в хтмл найденного пользователя
        return render_template('profile_normal.html', user=user[0],
                               department=department[0], education=education[0],
                               grade=grade[0], depart_position=depart_position[0],
                               diploma=diploma[0], achievments=achievments[0], users = [])
        # request1 = 'SELECT * FROM Passport'
        # data1, description = db_connect(request1)
        # # Получение заголовков столбцов
        # columns1 = [column1[0] for column1 in description] if description else None
        # return render_template('profile_normal.html', columns=columns1, data=data1)
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
            return render_template('profile_normal.html', user=user_t[0],
                                   department=department[0], education=education[0],
                                   grade=grade[0], depart_position=depart_position[0], diploma=diploma[0],
                                   achievments=achievments[0])
    return redirect("/")


@app.route('/profile_admin', methods=['POST', 'GET'])
def profile_admin():
    if current_user["id"] != 0:
        # Возвращаем авторизованного чела по айди
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
            # Передаем в хтмл найденного пользователя
            return render_template('profile_admin.html', user=user[0], users=[])
        else:
            return redirect("/")
    return redirect("/")


@app.route('/test', methods=['POST', 'GET'])
def test():
    # Измените 'your_table_name' и SQL-запрос в соответствии с вашей таблицей и требованиями
    request = 'SELECT * FROM Passport'
    data, description = db_connect(request)
    # Получение заголовков столбцов
    columns = [column[0] for column in description] if description else None
    return render_template('test.html', columns=columns, data=data)
    # Для представлений
    # # Пример запроса к представлению или таблице в базе данных
    # request = "SELECT * FROM UpdatableView"  # Замените на свой запрос
    #
    # # Вызываем функцию db_connect для выполнения запроса
    # data, description = db_connect(request)
    # return render_template('test.html', data=data, description=description)



@app.route('/logout', methods=['POST', 'GET'])
def logout():
    current_user["is_authenticated"] = False
    current_user["id"] = 0
    return redirect("/")


current_user = {"is_authenticated": False, "id": 0}

app.run()
