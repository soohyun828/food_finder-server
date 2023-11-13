import pymysql
import csv
import os
import pandas as pd


mydb = pymysql.connect(
    host="localhost",
    user="server",
    password="serverpw",
    port=3306,
    db="foodfinderdb",
    charset='utf8'
)

def remove_duplicates_and_zeros(input_csv, output_csv):
    # Load the CSV file into a pandas DataFrame
    df = pd.read_csv(input_csv, header=None, encoding='utf-8-sig')

    # Remove duplicate rows, keeping the first occurrence
    df_no_duplicates = df.drop_duplicates()

    # Remove rows where the 3rd and 4th columns (index 3(lat) and 4(lon) in zero-based indexing) have values equal to 0
    df_no_zeros = df_no_duplicates.loc[~((df_no_duplicates.iloc[:, 3] == 0) & (df_no_duplicates.iloc[:, 4] == 0))]

    # Save the DataFrame to a new CSV file
    df_no_zeros.to_csv(output_csv, index=False, header=None, encoding='utf-8-sig')


def csv2db(csv_filename):
    try:
        # Get Cursor
        dbcursor = mydb.cursor()

        # 테이블 만들기
        # sql = """CREATE TABLE restaurants (
        #     resname VARCHAR(100), 
        #     menu VARCHAR(100),
        #     address VARCHAR(200),
        #     lat VARCHAR(20), 
        #     lon VARCHAR(20),
        #     imageURL VARCHAR(150),
        #     category VARCHAR(10)
        #     )"""
        # dbcursor.execute(sql)

        # 테이블 전체 비우기 
        # dbcursor.execute("TRUNCATE restaurants")
        # mydb.commit()

###################################
        # insert 쿼리문
        sql = "INSERT INTO restaurants (resname, menu, address, lat, lon, imageURL, category) VALUES (%s, %s, %s, %s, %s, %s, %s)"

        # 파일 읽기
        with open(csv_filename, 'r', encoding='UTF-8', newline='') as f:
            rd = csv.reader(f)
            for row in rd:
                dbcursor.execute(sql, (row[0], row[1], row[2], row[3], row[4], row[5], row[6]))

        mydb.commit()
        print("OK")

    except pymysql.Error as e:
        print(f"Error: {e}")

    finally:
        dbcursor.close()
####################################


# Main
if __name__ == "__main__":
    root_directory = './data/'
    input_dir = root_directory + 'crawling_data/'
    output_dir = root_directory + 'processed_data/'
    for input_filename in os.listdir(input_dir):
        remove_duplicates_and_zeros(os.path.join(input_dir, input_filename), os.path.join(output_dir, input_filename))
        csv2db(os.path.join(output_dir, input_filename))

# Close the database connection outside the loop
mydb.close()