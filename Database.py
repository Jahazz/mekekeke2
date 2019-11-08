import mysql.connector



class Database:
    connection = None

    def connect(self,host, port, username, password, database):
        self.connection = mysql.connector.connect(
            host=host,
            port=port,
            user=username,
            password=password,
            database=database
        )
        pass

    def execute_query(self,query):
        cursor = self.connection.cursor(named_tuple=True)
        cursor.execute(query)
        self.connection.commit()
        return cursor.fetchall()

    def insert_multiple_query(self, insert, values):
        cursor = self.connection.cursor()
        cursor.executemany(insert, values)
        self.connection.commit()
        return cursor

    def insert_query(self, query):
        cursor = self.connection.cursor()
        cursor.execute(query)
        self.connection.commit()
        return cursor