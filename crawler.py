from selenium import webdriver
from selenium.webdriver.common.by import By 
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
import time
import requests
from bs4 import BeautifulSoup
from openpyxl import Workbook
import json
import csv


# kakao api
# 참고 사이트
# https://john-analyst.medium.com/%ED%8C%8C%EC%9D%B4%EC%8D%AC%EC%9D%84-%ED%99%9C%EC%9A%A9%ED%95%9C-%EC%B9%B4%EC%B9%B4%EC%98%A4-api%EB%A1%9C-%EC%9C%84%EA%B2%BD%EB%8F%84-%EA%B5%AC%ED%95%98%EA%B8%B0-69bc51697753
# 여기서 아래의 Authoriztion 은 KakaoAK + REST API키를 사용


def getLatLng(addr):
    url = 'https://dapi.kakao.com/v2/local/search/address.json?query=' + addr
    headers = {
        "Authorization": "KakaoAK 794e600cd25dbe707dccdf154dde8021"}
    # get 방식으로 주소를 포함한 링크를 헤더와 넘기면 result에 json형식의 주소와 위도경도 내용들이 출력된다.
    result = json.loads(str(requests.get(url, headers=headers).text))
    # status_code = requests.get(url, headers=headers).status_code
    # if(status_code != 200):
    #     print(
    #         f"ERROR: Unable to call rest api, http_status_coe: {status_code}")
    #     return 0

    try:
        match_first = result['documents'][0]['address']
        lon = match_first['x']
        lat = match_first['y']

        return float(lat), float(lon)
    except IndexError:  # match값이 없을때
        return 0, 0
    except TypeError:  # match값이 2개이상일때
        return 2, 2


# 함수
def get_food_information(menu_url, addr_urls, SCROLL_PAUSE_TIME, FILE_NAME):
    BASE_URL = 'https://www.diningcode.com'
    restaurants_data = [['name', 'best_menu_list', 'rest_score', 'loc_address', 'lat', 'lon', 'img_url']]

    # 1. 각 지역별 링크로 들어가서 html 통째로 긁은 후 a 태그들 만 추출해서 모아놓은 배열을 전부 append한 배열 html_list 만들기
    #    dining code의 a 태그 클래스 명이 매일(?) 난수에 의해 변경되는것 같아서 일단 html을 먼저 모두 모음
    html_list = []
    for addr_url in addr_urls:
        url = menu_url+addr_url
        print("{} 크롤링 시작".format(url))

        # chrome_addr = './chromedriver.exe'
        options = webdriver.ChromeOptions()
        options.add_argument("--disable-gpu")
        # options.add_argument('window-size=1280, 720')
        # options.add_argument('--incognito')
        driver = webdriver.Chrome(options=options)
        try:
            driver.get(url)
            driver.implicitly_wait(15)
        except:
            continue
        
        while True:
            try:
                num = int(driver.find_element(By.CLASS_NAME,'Filter__Info__Cnt').text.replace(',', ''))
            except:
                print("No element:" + url)
                break
            if num > 20:
                try:
                    # 더보기 버튼 클릭
                    driver.find_element(By.XPATH,'/html/body/div/div/div[2]/div/div/button[2]').click()
                    # 몇 초간 기다린다.
                    time.sleep(SCROLL_PAUSE_TIME)               
                    
                except:
                    # 더보기 버튼이 없을 때 while문이 끝남.
                    break
            else:
                break
        
        # 음식점 리스트의 모든 칸 모으기
        try:
            html = driver.page_source
            driver.implicitly_wait(10)
            soup = BeautifulSoup(html, 'html.parser')
            a_list = soup.find_all("a", {"class": "sc-ilxdoh dCXsNO PoiBlock"})
            html_list.append(a_list)
        except:
            print("soup parser error.")
            continue
        driver.quit()
    print("html 모으기 완료")

    # 2. html_list에 모아둔 모든 링크에 대한 html에서 필요한 정보만 추출
    # 각 음식점에 대한 정보
    driver = webdriver.Chrome()
    try:
        driver.get(BASE_URL)
    except:
        print("driver get error.")
        raise

    # html이 a_list랑 같은거
    for html in html_list:
        for list_ in html:
            # 음식점 주소얻기 위한 사이트내 url
            try:       
                #print(list_)         
                loc_url = f'{BASE_URL}{list_['href']}'
            except:
                #print("자세히보기 링크 없음")
                continue
            #음식점 이름
            try:
                name = list_.find('div', class_="InfoHeader").h2.text.strip().split(". ")[1]
            except:
                continue
            #음식점 이미지 주소
            img_url = list_.find('img', class_='title')['src']
            if img_url == None:
                img_url = "No image"
            
            #대표 메뉴
            best_menu = list_.find('p', class_='Category').find_all(['strong', 'span'])
            best_menu_list = []
            for tag in best_menu:
                best_menu_list.append(tag.text.strip())
            if len(best_menu_list) == 0:
                best_menu_list.append("No menu")

            #음식점 평점
            rest_score = list_.find('p', class_='UserScore').text.strip()
            if rest_score == None:
                rest_score = "No score"

            # 가게 주소 정보 얻기위한 링크로 이동(새창열기)
            driver.execute_script("window.open('about:blank', '_blank');")
            driver.switch_to.window(driver.window_handles[-1])
            driver.get(loc_url)
            time.sleep(1)
            
            # 주소정보가 있는 새 창의 내용 가져옴
            # ['경기', '수원시','?구',"동",'번지']
            loc_list = []
            try:
                loc_element = driver.find_element(By.CLASS_NAME, 'locat')
            except:
                print("No detail" + loc_url)
                f.close()
                continue
            for element in loc_element.find_elements(By.TAG_NAME, 'a'):
                loc_list.append(element.text)
            for element in loc_element.find_elements(By.TAG_NAME,'span'):
                loc_list.append(element.text)
            time.sleep(0.5)
            driver.execute_script("window.close();")
            driver.switch_to.window(driver.window_handles[0])
            
            if loc_list == None: 
                print("주소없음")
                continue
            
            # 도로명주소
            if loc_list[1] != "수원시" and loc_list[1] != "수원":
                if loc_list[1] != "용인시" and loc_list[1] != "용인":
                    continue
            loc_address=' '.join(loc_list[:5])

            # 위도 경도
            lat, lon = getLatLng(loc_address) 
            time.sleep(1)
            if lat == 0 and lon == 0: 
                print('api가 응답하지 않습니다. timesleep 후 재시도 합니다.')
                time.sleep(2)
                lat, lon = getLatLng(loc_address) 

            
            if lat != 0 and lon != 0:
                restaurants_data.append([name, best_menu_list, rest_score, loc_address, lat, lon, img_url])
            f = open(FILE_NAME, "a", encoding='utf-8-sig', newline='')
            writer = csv.writer(f)
            writer.writerow([name, best_menu_list, rest_score, loc_address, lat, lon, img_url])
            f.close()


    # driver.quit()
# f = open(FILE_NAME, "w", encoding='utf-8-sig', newline='')
# writer = csv.writer(f)
# writer.writerows(restaurants_data)
# f.close()
        

#main
do = '경기'
sigungu = ['용인시 기흥구','수원시 영통구']
# sigungu = ['수원시 영통구']
# dong[n][m] : 경기 n시군구 m동
dong = [['하갈동','보정','동백','기흥역','기흥구청','흥덕','구성역','보정동','신갈','용인동백','고매동','공세동','구갈동','농서동','동백동','마북동','보라동','상갈동','상하동','서천동','언남동','영덕동','중동','지곡동','청덕동'],\
    ['광교','영통역','영통','망포역','망포','아주대','광교중앙역','영통구청','광교호수공원','곡선동','매탄동','신동','영통동','우만동','원천동','이의동','하동']]
# dong = [['신동','영통동','우만동','원천동','이의동','하동']]
#https://www.diningcode.com/list.dc?keyword={메뉴}&addr={경기}%20%{시군구}20%2B%{읍면동} 중에 &뒷부분 url 만들기
addr_urls = []
for i in range(len(sigungu)):
    for DONG in dong[i]:
        url = "&addr={}%20%{}%20%2B{}&order=l_count".format(do,sigungu[i],DONG)
        addr_urls.append(url)

FILE_PATH = './data/'

#한식
menu_URL = 'https://www.diningcode.com/list.dc?keyword='+ '한식'
get_food_information(menu_URL, addr_urls, 0.1, FILE_PATH+"restaurants_korean.csv")

#중식
menu_URL = 'https://www.diningcode.com/list.dc?keyword='+ '중식'
get_food_information(menu_URL, addr_urls, 0.1, FILE_PATH+"restaurants_chinese.csv")

# 일식
menu_URL = 'https://www.diningcode.com/list.dc?keyword='+ '일식'
get_food_information(menu_URL, addr_urls, 0.1, FILE_PATH+"restaurants_japanese.csv")

# 양식
menu_URL = 'https://www.diningcode.com/list.dc?keyword='+ '양식'
get_food_information(menu_URL, addr_urls, 0.1, FILE_PATH+"restaurants_american.csv")

# 이탈리안
menu_URL = 'https://www.diningcode.com/list.dc?keyword='+ '이탈리안'
get_food_information(menu_URL, addr_urls, 0.1, FILE_PATH+"restaurants_italian.csv")

# 멕시칸
menu_URL = 'https://www.diningcode.com/list.dc?keyword='+ '멕시칸'
get_food_information(menu_URL, addr_urls, 0.1, FILE_PATH+"restaurants_mexican.csv")

# 패스트푸드
menu_URL = 'https://www.diningcode.com/list.dc?keyword='+ '패스트푸드'
get_food_information(menu_URL, addr_urls, 0.1, FILE_PATH+"restaurants_fastfood.csv")
