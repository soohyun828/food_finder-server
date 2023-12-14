import pymysql


mydb = pymysql.connect(
    host="localhost",
    user="server",
    password="serverpw",
    port=3306,
    db="foodfinderdb",
    charset='utf8'
)
"""
Table: bookmarks
Columns:
    id int AI PK 
    username varchar(255) 
    resnum int
"""


try:
        # Get Cursor
    dbcursor = mydb.cursor()

    # bookmarks 테이블 만들기
    sql = """CREATE TABLE IF NOT EXISTS bookmarks (
        id INT AUTO_INCREMENT PRIMARY KEY,
        username VARCHAR(255) NOT NULL,
        resnum INT NOT NULL,
        UNIQUE KEY unique_bookmark (username, resnum)
        )"""
    dbcursor.execute(sql)

    sql = """CREATE TABLE IF NOT EXISTS restaurants (
        resnum INT PRIMARY KEY AUTO_INCREMENT,
        resname VARCHAR(255), 
        menu VARCHAR(255),
        address VARCHAR(255),
        lat DECIMAL(10, 8), 
        lon DECIMAL(11, 8),
        imageURL VARCHAR(255),
        category VARCHAR(255)
        )"""

    # 테이블 전체 비우기 
    # dbcursor.execute("TRUNCATE restaurants")
    # mydb.commit()

except pymysql.Error as e:
    print(f"Error: {e}")

finally:
    dbcursor.close()