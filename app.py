from flask import Flask, request, redirect, url_for, render_template, session
from mysql.connector import connect
import config

app = Flask(__name__)


@app.route('/', methods=['GET', 'POST'])
def index():
    try:
        if request.method == "POST":
            user_name = request.form['user-name']
            password = request.form['password']
            if user_name == "admin@thereporter" and password == "1234":
                return redirect(url_for('dashboard'))
            elif user_name == "user@thereporter" and password == "1234":
                return redirect(url_for('user'))
            else:
                return render_template('login.html')
        else:
            return render_template('login.html')
    except Exception as e:
        print(e)
        return redirect(url_for('error_log'))


@app.route('/user', methods=['GET', 'POST'])
def user():
    try:
        if request.method == "POST":
            description = request.form['description']
            possible_cause = request.form['possible-cause']
            vehicles_involved = request.form['vehicles-involved']
            contact_phone = request.form['contact-phone']
            location = request.form['location']
            accident_photo = request.form['accident-photo']
            db_parameter = config.db_parameters()
            db = connect(host=db_parameter[0], user=db_parameter[1], password=db_parameter[2],
                         database='TheReporter')
            c = db.cursor(buffered=True)
            cur_day = config.cur_day_generator()
            sql_stmt = "Insert into Accidents (description, possible_cause, vehicles_involved, contact_phone, location, accident_photo, date_taken)" " values (%s, %s, %s, %s, %s, %s, %s)"
            data = (description, possible_cause, vehicles_involved, contact_phone, location, accident_photo, cur_day)
            try:
                c.execute(sql_stmt, data)
            except Exception as e:
                if str(e)[:str(e).find(" ")] == "1146":
                    c.execute("Create table Accidents (accident_id int not null primary key auto_increment, description varchar(100) not null, possible_cause varchar(100) not null, vehicles_involved int not null, contact_phone varchar(20) not null, location varchar(100) not null, accident_photo varchar(100) not null, date_taken timestamp not null)")
                    c.execute(sql_stmt, data)
                else:
                    print(e)
                    db.close()
                    return redirect(url_for('error_log'))
            db.commit()
            db.close()
            return redirect(url_for('user'))
        else:
            return render_template('user-profile.html')
    except Exception as e:
        print(e)
        return redirect(url_for('error_log'))


@app.route('/admin/dashboard', methods=['GET', 'POST'])
def dashboard():
    try:
        db_parameter = config.db_parameters()
        db = connect(host=db_parameter[0], user=db_parameter[1], password=db_parameter[2],
                     database='TheReporter',  auth_plugin='mysql_native_password')
        c = db.cursor(buffered=True)
        if request.method == "POST":
            description = request.form['description']
            location = request.form['location']

            sql_stmt = "Insert into Accidents (description, possible_cause, vehicles_involved, contact_phone, location, accident_photo, date_taken)" " values(%s, %s, %s, %s, %s, %s, %s)"
            data = (description, '', 1, '+254710689178', location, '', config.cur_day_generator())
            try:
                c.execute(sql_stmt, data)
                db.commit()
            except Exception as e:
                if str(e)[:str(e).find(" ")] == "1146":
                    pass
                else:
                    print(e)
                    db.close()
                    return redirect(url_for('error_log'))
        # get today accidents
        try:
            c.execute("Select sum(vehicles_involved), count(accident_id) from Accidents")
            today_details = c.fetchone()
            total_cars = today_details[0]
            total_accidents = today_details[1]
        except TypeError:
            total_cars = 0
            total_accidents = 0
        except Exception as e:
            if str(e)[:str(e).find(" ")] == "1146":
                total_cars = 0
                total_accidents = 0
            else:
                print(e)
                db.close()
                return redirect(url_for('error_log'))

        # get the users count
        try:
            c.execute("Select count(user_id) from Users")
            total_users = 0
        except Exception as e:
            if str(e)[:str(e).find(" ")] == "1146":
                total_users = 0
            else:
                print(e)
                db.close()
                return redirect(url_for('error_log'))

        # get the accident details
        try:
            c.execute("Select * from Accidents")
            accident_details = c.fetchall()
            print(len(accident_details), 121)
        except Exception as e:
            if str(e)[:str(e).find(" ")] == "1146":
                accident_details = ()
            else:
                print(e)
                db.close()
                return redirect(url_for('error_log'))

        db.close()
        print(accident_details[::-1][:5], 131)
        return render_template('dashboard.html', total_cars=total_cars, total_accidents=total_accidents, total_users=total_users, accident_details=accident_details, todo=accident_details[::-1][:5])
    except Exception as e:
        print(e)
        return redirect(url_for('error_log'))


@app.route('/admin/accidents', methods=['GET'])
def accidents():
    try:
        db_parameter = config.db_parameters()
        db = connect(host=db_parameter[0], user=db_parameter[1], password=db_parameter[2],
                     database='TheReporter')
        c = db.cursor(buffered=True)
        try:
            c.execute("Select * from Accidents")
            accident_details = c.fetchall()
        except Exception as e:
            if str(e)[:str(e).find(" ")] == "1146":
                accident_details = ()
            else:
                print(e)
                db.close()
                return redirect(url_for('error_log'))
        db.close()
        return render_template('accidents.html', accident_details=accident_details)
    except Exception as e:
        print(e)
        return redirect(url_for('error_log'))


@app.route('/admin/profile', methods=['GET', 'POST'])
def admin_profile():
    try:
        if request.method == "POST":
            pass
        else:
            return render_template('admin-profile.html')
    except Exception as e:
        print(e)
        return redirect(url_for('error_log'))


@app.route('/error', methods=['GET'])
def error_log():
    try:
        return render_template('404.html')
    except Exception as e:
        print(e)
        return redirect(url_for(''))


@app.route('/logout', methods=['GET'])
def logout():
    for item in session:
        session.pop(item)
    return redirect(url_for('index'))


if __name__ == "__main__":
    app.run(debug=True, port=80)
