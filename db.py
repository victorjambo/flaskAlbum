import sqlite3 as lite


class DBManager:
    """Create a new connection to the sqlite database"""
    def __init__(self):
        db_name = "room_alloc.db"
        self.connection = lite.connect(db_name)
        self.cursor = self.connection.cursor()
        self.migrations()

    def migrations(self):
        """
        Create the tables if they do not exist
        """
        with self.connection:
            self.cursor.executescript("""
                CREATE TABLE IF NOT EXISTS rooms (
                    id    INTEGER PRIMARY KEY AUTOINCREMENT,
                    name  INTEGER UNIQUE,
                    type  CHAR(1)
                );
                CREATE TABLE IF NOT EXISTS fellows (
                    id    INTEGER PRIMARY KEY AUTOINCREMENT,
                    name  TEXT,
                    accomodation  TEXT,
                    room_id   INTEGER
                );
                CREATE TABLE IF NOT EXISTS staff (
                    id    INTEGER PRIMARY KEY AUTOINCREMENT,
                    name  TEXT,
                    room_id   INTEGER
                );
                """)

    def run_many_queries(self, query_string, data):
        """
        Run the executemany command to query multiple statements
        """
        try:
            with self.connection:
                self.cursor.executemany(query_string, data)
                return True
        except lite.IntegrityError:
            return False

    def insert(self, query_string):
        """Run sqlite execute to query to insert a single record
        Args:
            query_string    The sql statement to run
        Returns: last inserted id or false in case of error
        """
        try:
            with self.connection:
                self.cursor.execute(query_string)
                return self.cursor.lastrowid
        except lite.IntegrityError:
            return False

    def update(self, query_string):
        """Run sqlite execute to query to update a record
        Args:
            query_string    The sql statement to run
        Returns:    True or False
        """
        try:
            with self.connection:
                self.cursor.execute(query_string)
                return True
        except lite.IntegrityError:
            return False

    def select(self, query_string):
        """Run sqlite execute to select data
        Args:
            query_string    The sql statement to run
        Returns: returned data or false in case of error
        """
        try:
            with self.connection:
                self.cursor.execute(query_string)
                return self.cursor.fetchall()
        except:
            return False

    def select_one(self, query_string):
        """Run sqlite execute to select one record of data
        Args:
            query_string    The sql statement to run
        Returns: returned data or false in case of error
        """
        try:
            with self.connection:
                self.cursor.execute(query_string)
                return self.cursor.fetchone()
        except:
            return False