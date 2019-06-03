
def set_up():
    try:
        from .db_config import FULL_PATH_DB
    except:
        from db_config import FULL_PATH_DB
    import sqlite3
    connection = sqlite3.connect(FULL_PATH_DB)
    cursor = connection.cursor()
    return connection, cursor


