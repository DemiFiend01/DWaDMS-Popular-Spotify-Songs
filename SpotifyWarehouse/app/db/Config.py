class Config:
    DBNAME = "test_db"
    USER = "postgres"
    PASSWORD = "C3zwer45"

    def __init__(self, dbname="test_db",
                 user="postgres",
                 password="C3zwer45"):
        self.USER = user
        self.PASSWORD = password
        self.DBNAME = dbname