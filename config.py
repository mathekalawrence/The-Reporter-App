#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
from datetime import datetime
import pytz
import pickle
from collections import abc
from mysql.connector import connect


def db_parameters():
    result_set = []
    file_name = open('config', 'rb')
    st = pickle.load(file_name)
    file_name.close()

    result_set.append(st['host'])
    result_set.append(st['user'])
    result_set.append(st['password'])
    return result_set


# update and keep the previous dict values.
def update_dict_section(orig_dict, new_dict):
    for key, val in new_dict.items():
        if isinstance(val, abc.Mapping):
            tmp = update_dict_section(orig_dict.get(key, {}), val)
            orig_dict[key] = tmp
        elif isinstance(val, list):
            orig_dict[key] = (orig_dict.get(key, []) + val)
        else:
            orig_dict[key] = new_dict[key]
    else:
        return orig_dict


def cur_date_generator():
    cur_date = str(datetime.now(pytz.timezone('Africa/Nairobi')))
    return cur_date[:cur_date.find(" ")]


def cur_day_generator():
    cur_date = str(datetime.now(pytz.timezone('Africa/Nairobi')))
    return cur_date[:cur_date.find(".")]


def session_details_section(session_id):
    db_parameter = db_parameters()
    db = connect(host=db_parameter[0], user=db_parameter[1], password=db_parameter[2], database='onespace_OneSpaceMall')
    c = db.cursor(buffered=True)
    c.execute("Select address from OneSpaceMall_Sessions where session_code = '" + session_id + "'")
    address = c.fetchone()[0]
    # return True/False/None (Flag to check on the password expiration, none is to do nothing), address, name, account_type(user/ administrator)
    return True, "", address,


def session_update_section(session_id, address, user_type):
    db_parameter = db_parameters()
    db = connect(host=db_parameter[0], user=db_parameter[1], password=db_parameter[2], database='onespace_OneSpaceMall')
    c = db.cursor(buffered=True)
    cur_date = cur_day_generator()
    sql_stmt = "Insert into OneSpaceMall_Sessions (session_code, address, user_type, date_created, last_update)" " values(%s, %s, %s, %s, %s)"
    data = (session_id, address, user_type, cur_date, cur_date)
    try:
        c.execute(sql_stmt, data)
    except Exception as e:
        if str(e)[:str(e).find(" ")] == "1146":
            c.execute(
                "Create table OneSpaceMall_Sessions(session_id int not null primary key auto_increment, session_code varchar(20) not null, address varchar(50) not null, user_type tinyint not null, date_created timestamp not null, last_update timestamp not null, unique key codes (session_code))")
            c.execute(sql_stmt, data)
        elif str(e)[:str(e).find(" ")] == "1062":
            # checking if 15 minutes has elapsed
            c.execute("Select last_update from OneSpaceMall_Sessions where session_code = '" + session_id + "'")
            last_update = c.fetchone()[0]
            c.execute("Select date_add('" + str(last_update) + "', interval 15 minute)")
            new_date = c.fetchone()[0]
            db.close()
            return True
            # if new_date >= datetime.now(pytz.timezone('Africa/Nairobi')):
            #     db.close()
            #     return False
            # c.execute("Update sessions set last_update = '" + cur_date + "' where session_id = '" + session_id + "'")
        else:
            print(e)
            db.close()
            return None
    db.commit()
    db.close()
    return True


def user_details_section(session_id):
    db_parameter = db_parameters()
    db = connect(host=db_parameter[0], user=db_parameter[1], password=db_parameter[2], database='onespace_OneSpaceMall')
    c = db.cursor(buffered=True)
    cur_day = cur_day_generator()
    sql_stmt = "Insert into OneSpaceMall_Sessions (session_code, date_created, last_update)" " values (%s, %s, %s)"
    data = (session_id, cur_day, cur_day)
    try:
        c.execute("Select address, user_type from OneSpaceMall_Sessions where session_code = '" + session_id + "'")
    except Exception as e:
        if str(e)[:str(e).find(" ")] == "1146":
            c.execute(
                "Create table OneSpaceMall_Sessions(session_id int not null primary key auto_increment, session_code varchar(20) not null, address varchar(50) not null default '', user_type tinyint not null default 100, date_created timestamp not null, last_update timestamp not null, unique key codes (session_code))")
            c.execute(sql_stmt, data)
            result_set = ('', 100)
        else:
            print(e)
            db.close()
            return None,

    result_set = c.fetchone()
    try:
        if result_set[1] == 0:
            # customer
            c.execute("Select user_id from OneSpaceMall_Users where address = '" + result_set[0] + "'")
            user_type = 0
            sub_set = c.fetchone()[0]
        elif result_set[1] == 1:
            # affiliate
            c.execute("Select affiliate_id from OneSpaceMall_Affiliates where email = '" + result_set[0] + "'")
            user_type = 1
            sub_set = c.fetchone()[0]
        elif result_set[1] == 2:
            # store owner
            c.execute("Select store_id from OneSpaceMall_Stores where address = '" + result_set[0] + "'")
            user_type = 2
            sub_set = c.fetchone()[0]
        elif result_set[1] == 3:
            # administrator
            c.execute("Select admin_id from OneSpaceMall_Administrators where address = '" + result_set[0] + "'")
            user_type = 3
            sub_set = c.fetchone()[0]
        else:
            user_type = 0
            sub_set = ''
        c.execute("Update OneSpaceMall_Sessions set last_update = '" + cur_day + "' where session_code = '" + session_id + "'")
    except TypeError:
        try:
            c.execute(sql_stmt, data)
            db.commit()
        except Exception as e:
            db.close()
            if str(e)[:str(e).find(" ")] == "1062":
                return None,
            else:
                print(e)
        db.close()
        return None,
    except Exception as e:
        db.close()
        if str(e)[:str(e).find(" ")] == "1146":
            pass
        else:
            print(e)
        return None,
    db.commit()
    db.close()
    return user_type, sub_set, result_set[0]
