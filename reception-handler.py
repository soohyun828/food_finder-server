from flask import Flask, request, jsonify
from geopy.distance import geodesic
from pymysql.cursors import DictCursor
import pymysql
import hashlib


app = Flask(__name__)

# MySQL 설정
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'server'
app.config['MYSQL_PASSWORD'] = 'serverpw'
app.config['MYSQL_DB'] = 'foodfinderdb'
mysql = pymysql.connect(
    host=app.config['MYSQL_HOST'],
    user=app.config['MYSQL_USER'],
    password=app.config['MYSQL_PASSWORD'],
    db=app.config['MYSQL_DB'],
    charset='utf8mb4',
    cursorclass=pymysql.cursors.DictCursor
)

"""
Table: users
Columns:
    username varchar(255) PK 
    password varchar(255) 
    phoneNumber varchar(45) 
"""
"""
Table: bookmarks
Columns:
    id int AI PK => 순차적으로 넘버 매겨지는거(걍 인덱스용)
    username varchar(255) 
    resnum int
"""
"""
Table: restaurants
Columns:
    resnum int AI PK 
    resname varchar(255) 
    menu varchar(255) 
    address varchar(255) 
    lat decimal(10,8) 
    lon decimal(11,8) 
    imageURL varchar(255) 
    category varchar(255)
"""

with mysql.cursor() as cur:
    # encoding 방식 변경
    cur.execute('SET NAMES utf8mb4;')
    cur.execute('SET CHARACTER SET utf8mb4;')
    cur.execute('SET character_set_connection=utf8mb4;')



#### 회원가입

# 아이디 존재 여부 확인 함수
def check_username_availability(username):
    #username이 DB에 있으면 true, 없거나 테이블이 빈상태면 false 반환
    with mysql.cursor() as cur:
        cur.execute("SELECT COUNT(*) as count FROM users WHERE username=%s", (username,))
        result = cur.fetchone()
    if result:
        if result['count'] == 0:
            return False
        else:
            return True
    else:
        return False


# 아이디 체크
@app.route('/home/check_username/<username>', methods=['GET'])
def check_username(username):



    if check_username_availability(username):
        return jsonify(success=False, message='이미 사용 중인 ID 입니다. 다른 ID를 입력해주세요.')
    else:
        return jsonify(success=True, message='사용 가능한 ID 입니다.')




@app.route('/home/signup', methods=['POST'])
def signup():
    # 중복 아이디 확인
    data = request.get_json()
    username = data['username']



    # 아이디가 중복되지 않으면 회원가입 진행
    phone_number = data['phoneNumber']
    password = data['password']

    pw_hash = hashlib.sha256(password.encode('utf-8')).hexdigest()
    print(password, pw_hash)
    with mysql.cursor() as cur:
        cur.execute("INSERT INTO users (username, phoneNumber, password) VALUES (%s, %s, %s)",
                    (username, phone_number, pw_hash))
        mysql.commit()

    return jsonify(success=True, message='회원가입이 완료되었습니다.')




# 로그인 기능
@app.route('/home/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data['username']
    password = data['password']
    input_pw_hash = hashlib.sha256(password.encode('utf-8')).hexdigest()

    try:
        if check_username_availability(username):
            with mysql.cursor() as cur:
                cur.execute("SELECT * FROM users WHERE username=%s", (username,))
                user_data = cur.fetchone()
                # print(f'유저 정보 : {user_data}')
                # print(f'입력 정보 : {data, input_pw_hash}')

            if user_data['password'] == input_pw_hash:
                return jsonify(success=True, username=user_data['username'], message = '로그인 성공!')
            else:
                return jsonify(success=False, message = '비밀번호가 틀렸습니다.')
        else:
            return jsonify(success=False, message = '존재하지 않는 ID입니다.')



    except pymysql.Error as e:
        print(f"Error during login: {e}")
        return jsonify(success=False, message='An error occurred during login')




# 음식점 리스트업 기능
@app.route('/home/<category>/<menu>/<username>/<lat>/<lon>', methods=['GET'])
def restaurant_list(category, menu, username, lat, lon):
    try:
        user_location = (lat, lon)
        result = []
        print(f'lat : {lat}, lon : {lon}')

        # Use context manager for cursor
        with mysql.cursor() as cur:
            cur.execute("SELECT * FROM restaurants WHERE category=%s AND menu LIKE %s", (category, f"%{menu}%"))
            restaurants = cur.fetchall()

            for restaurant in restaurants:
                res_location = (restaurant['lat'], restaurant['lon'])
                distance = geodesic(user_location, res_location).meters # meter 단위

                if distance <= 5000:  # 거리가 5km 이내인 경우만 추가
                    resnum = restaurant['resnum']
                    bookmarked = is_bookmarked(username, resnum)
                    result.append({
                        'resnum': restaurant['resnum'],
                        'resname': restaurant['resname'],
                        'address': restaurant['address'],
                        'imageURL': restaurant['imageURL'],
                        'lat' : restaurant['lat'],
                        'lon' : restaurant['lon'],
                        'distance': distance,  
                        'bookmarked': bookmarked
                    })

        # 거리에 따라 오름차순으로 정렬
        result.sort(key=lambda x: x['distance'])

        # print(result)
        return jsonify(result)

    except Exception as e:
        print(f"Error during restaurant list: {e}")
        return jsonify(error=True, message='An error occurred during restaurant list')



# 북마크 여부 확인 함수
def is_bookmarked(username, resnum):
    try:
        with mysql.cursor() as cur:
            # 해당 username과 resnum에 대한 북마크 레코드 조회
            cur.execute("SELECT * FROM bookmarks WHERE username=%s AND resnum=%s", (username, resnum))
            result = cur.fetchone()

            # 북마크 레코드가 존재하면 True 반환, 그렇지 않으면 False 반환
            return result is not None

    except pymysql.Error as e:
        print(f"Error during is_bookmarked: {e}")
        return False



# 북마크 토글 기능
@app.route('/bookmark/<username>/<resnum>', methods=['POST'])
def toggle_bookmark(username, resnum):
    try:
        with mysql.cursor() as cur:
            # 해당 username과 resnum에 대한 북마크 레코드 조회
            cur.execute("SELECT * FROM bookmarks WHERE username=%s AND resnum=%s", (username, resnum))
            result = cur.fetchone()

            if result:
                # 북마크 레코드가 이미 존재하면 삭제
                cur.execute("DELETE FROM bookmarks WHERE username=%s AND resnum=%s", (username, resnum))
            else:
                # 북마크 레코드가 존재하지 않으면 추가
                cur.execute("INSERT INTO bookmarks (username, resnum) VALUES (%s, %s)", (username, resnum))

            mysql.commit()

        return jsonify(success=True)

    except pymysql.Error as e:
        print(f"Error during toggle_bookmark: {e}")
        return jsonify(error=True, message='An error occurred during bookmark toggle')


####### 여기부터 Navigation에 있는 기능

# 북마크 기능
@app.route('/bookmark/<username>', methods=['GET'])
def bookmark(username):

    result = []

    try:
        with mysql.cursor() as cur:
            cur.execute("SELECT resnum FROM bookmarks WHERE username=%s", (username,))
            bookmarked_resnum = cur.fetchall()
    
        if bookmarked_resnum and len(bookmarked_resnum) > 0:
            
            for num in bookmarked_resnum:

                with mysql.cursor() as cur:
                    cur.execute("SELECT * FROM restaurants WHERE resnum=%s", (num['resnum'],))
                    restaurant = cur.fetchone()

                    if restaurant:
                        result.append({
                            'resnum': restaurant['resnum'],
                            'resname': restaurant['resname'],
                            'address': restaurant['address'],
                            'lat': restaurant['lat'],
                            'lon': restaurant['lon'],
                            'imageURL': restaurant['imageURL'],
                            'category': restaurant['category']
                        })
            
            return jsonify({'success': True, 'result': result})

        else:
            return jsonify({'success': False, 'result': '북마크 된 음식점이 없습니다.'})
    
    except pymysql.Error as e:
        print(f"Error during get_bookmark: {e}")
        return jsonify(error=True, message='An error occurred during getting bookmark')

    


# 검색 기능
@app.route('/home/search/<menu>/<username>/<lat>/<lon>', methods=['GET'])
def search(menu, username, lat, lon):

    user_location = (lat, lon)
    result = []


    with mysql.cursor() as cur:
        cur.execute("SELECT * FROM restaurants WHERE menu LIKE %s", (f"%{menu}%",))
        restaurants = cur.fetchall()

        # 음식점 이름 같은거 중복 제거
        for restaurant in restaurants:

            if len(result) > 0:
                if any(restaurant['resname'] == item['resname'] for item in result):
                    pass

                else:
                    res_location = (restaurant['lat'], restaurant['lon'])
                    distance = geodesic(user_location, res_location).meters # meter 단위

                    if distance <= 5000:  # 거리가 5km 이내인 경우만 추가
                        resnum = restaurant['resnum']
                        bookmarked = is_bookmarked(username, resnum)
                        result.append({
                            'resnum': restaurant['resnum'],
                            'resname': restaurant['resname'],
                            'address': restaurant['address'],
                            'lat' : restaurant['lat'],
                            'lon' : restaurant['lon'],
                            'imageURL': restaurant['imageURL'],
                            'distance': distance,  
                            'bookmarked': bookmarked
                        })

            else:
                res_location = (restaurant['lat'], restaurant['lon'])
                distance = geodesic(user_location, res_location).meters # meter 단위

                if distance <= 5000:  # 거리가 5km 이내인 경우만 추가
                    resnum = restaurant['resnum']
                    bookmarked = is_bookmarked(username, resnum)
                    result.append({
                        'resnum': restaurant['resnum'],
                        'resname': restaurant['resname'],
                        'address': restaurant['address'],
                        'imageURL': restaurant['imageURL'],
                        'lat' : restaurant['lat'],
                        'lon' : restaurant['lon'],
                        'distance': distance,  
                        'bookmarked': bookmarked
                    })
                    
    
    # 거리에 따라 오름차순으로 정렬
    result.sort(key=lambda x: x['distance'])

    # print(result)
    return jsonify(result)



if __name__ == '__main__':
    # app.run(debug=True)
    app.run(host='0.0.0.0', port=5000, debug=True)