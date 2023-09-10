import time

from mysql.connector import connect, Error

from db_credentials import database_credentials


class DatabaseConnection:
    sql_connection, sql_conn_cursor = None, None

    def open_sql_connection(self):
        connection_tries = 0
        while connection_tries < 5:
            try:
                self.sql_connection = connect(**database_credentials)
                self.sql_conn_cursor = self.sql_connection.cursor()
                self.sql_conn_dict_cursor = self.sql_connection.cursor(dictionary=True)
                print("Database connected!")
                return 1
            except Error as err:
                print("Exception while making SQL Database Connection: {}".format(err))
                connection_tries += 1
                time.sleep(30)

        if connection_tries == 5:
            print("Failed 5 tries to establish connection")
            raise StopIteration()

    def update_mysql_connection(self):
        if self.sql_connection and self.sql_connection.is_connected():
            return
        self.open_sql_connection()
