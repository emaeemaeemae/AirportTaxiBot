import database as db


def check_available_cars(lst, tourists):
    return [x for x in lst if x['users_count'] + tourists <=
            x['max_users_count']]


def get_drives_list(context):
    connect = db.ConnectionFactory(db.PyMySQLWrapper,
                                   db.database.mysql_credentials)

    with connect() as c:
        c.execute(
            'SELECT * '
            'FROM main '
            'WHERE district=%s '
            'AND class_auto=%s '
            'AND max_users_count<=%s '
            'AND create_date >= '
            'DATE_SUB(NOW(), INTERVAL 1 MINUTE);',
            (context.user_data['district'],
             context.user_data['class_auto'],
             context.user_data['max_users_count']))

        tours_list = check_available_cars(c.fetchall(),
                                          context.user_data['users_count'])

        return tours_list


def add_new_drive(context):
    connect = db.ConnectionFactory(db.PyMySQLWrapper,
                                   db.database.mysql_credentials)
    with connect() as c:
        c.execute(
            'INSERT into main ('
            'admin_username, district, class_auto, users_count, '
            'max_users_count) values (%s, %s, %s, %s, %s);',
            (context.user_data['admin_username'],
             context.user_data['district'],
             context.user_data['class_auto'],
             context.user_data['users_count'],
             context.user_data['max_users_count']))


def add_users_to_drive(tour, context):
    connect = db.ConnectionFactory(db.PyMySQLWrapper,
                                   db.database.mysql_credentials)
    with connect() as c:
        c.execute(
            'SELECT * '
            'FROM main '
            'WHERE id=%s;',
            (tour['id']))

        tour['users_count'] = c.fetchone()['id']

        new_count = tour['users_count'] + context.user_data['users_count']
        if new_count <= tour['max_users_count']:
            c.execute(
                'UPDATE main '
                'SET users_count=%s '
                'WHERE id=%s;',
                (new_count, tour['id']))
        else:
            raise db.exceptions_.MySQLWrapperTransactionError
