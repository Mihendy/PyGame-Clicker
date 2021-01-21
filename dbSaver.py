import os.path
import sqlite3


def upload(file_path, values):
    if not os.path.exists(file_path):
        con = sqlite3.connect(file_path)
        cur = con.cursor()
        cur.execute('''CREATE TABLE Clicker (
                        is_paused   BOOLEAN,
                        score       STRING,
                        money       STRING,
                        click       STRING,
                        click_money STRING,
                        cps         STRING,
                        skin_path   STRING
                                            );''')
        con.commit()
    con = sqlite3.connect(file_path)
    is_paused, score, money, click, click_money, cps, skin_path = values
    cur = con.cursor()
    cur.execute("""INSERT INTO Clicker(is_paused, score, money, click, click_money, cps, skin_path)
                VALUES({}, '{}', '{}', '{}', '{}', '{}', '{}')"""
                .format(is_paused, score, money, click, click_money, cps, skin_path))
    con.commit()
    return None


def download(file_path):
    if not os.path.exists(file_path):
        raise FileNotFoundError
    else:
        con = sqlite3.connect(file_path)
        cur = con.cursor()
        result = cur.execute("""SELECT * FROM Clicker""").fetchall()
        con.commit()
        return result[-1]
