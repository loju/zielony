#!/usr/bin/python3.4
# -*- coding: utf-8 -*-

from mysql.connector import (connection)
from mysql.connector import errorcode, Error
from settings import settings


def connect_db():
    try:
        cnx = connection.MySQLConnection(
            user=settings['user'],
            password=settings['password'],
            host=settings['host'],
            database=settings['database']
        )
        cursor = cnx.cursor()
        query = ("SELECT id, user_mail, license_end FROM serials WHERE user_mail LIKE %s ORDER BY id")

        mail_to_search = '%noga%'
        cursor.execute(query, (mail_to_search, ))
        for (id, user_mail, license_end) in cursor:
            print ("User id: %s, mail: %s, abonament do: %s" %
                   (id, user_mail, license_end)
                   )
        cursor.close()

    except Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            print("Something is wrong with your user name or password")
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            print("Database does not exist")
        else:
            print(err)
    finally:
        cnx.close()


if __name__ == "__main__":
    connect_db()
