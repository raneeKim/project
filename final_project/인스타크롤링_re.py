'''
# 필요 패키지 호출
from selenium import webdriver
from bs4 import BeautifulSoup
import time
import re
import time

# 함수 정의: 검색어 조건에 따른 url 생성
def insta_searching(word):
    url = "https://www.instagram.com/explore/tags/" + str(word)
    return url


# 함수 정의: 본문 내용, 작성일자, 좋아요 수, 위치 정보, 해시태그 가져오기
## 2022/04/03 전체적으로 수정
import re
from bs4 import BeautifulSoup
def get_content(driver):
    html = driver.page_source
    soup = BeautifulSoup(html, 'lxml')
    # 본문 내용
    try:
        content = soup.select('div.MOdxS')[0].text
    except:
        content = ''
    # 해시태그
    tags = re.findall(r'#[^\s#,\\]+', content)
    # 작성일자
    date = soup.select('time._1o9PC')[0]['datetime'][:10]
    # 좋아요
    try:
        like = soup.select('section.EDfFK.ygqzn')[0].findAll('span')[-1].text
    except:
        like = 0
    # 위치
    try:
        place = soup.select('div.M30cS')[0].text
    except:
        place = ''
    data = [content, date, like, place, tags]
    return data

# 함수 정의: 첫 번째 게시물 클릭 후 다음 게시물 클릭
def move_next(driver):
    right = driver.find_element_by_css_selector("div.l8mY4.feth3") # 2022/01/11 수정
    right.click()
    time.sleep(3)

# 크롤링 시작
"""
driver.get(url)을 통해 검색 페이지 접속하고,
target 변수에 크롤링할 게시글의 수를 바인딩
"""

from selenium.webdriver.common.by import By

# 크롬 브라우저 열기
driver = webdriver.Chrome('chromedriver.exe')
driver.get('https://www.instagram.com')
time.sleep(3)
# 인스타그램 로그인을 위한 계정 정보
email = 'icex__o'
input_id = driver.find_element(By.XPATH,'/html/body/div[2]/div/div/div[1]/div/div/div/div[1]/section/main/div/div/div[1]/div[2]/form/div/div[1]/div/label/input')
input_id.click()
input_id.send_keys(email)
password = 'Ejqmf9866!'
input_pw = driver.find_element(By.XPATH,'/html/body/div[2]/div/div/div[1]/div/div/div/div[1]/section/main/div/div/div[1]/div[2]/form/div/div[2]/div/label/input')
input_pw.click()
input_pw.send_keys(password)
input_pw.submit()
time.sleep(5)
# 게시물을 조회할 검색 키워드 입력 요청
word = input("검색어를 입력하세요 : ")
word = str(word)
url = insta_searching(word)
# 검색 결과 페이지 열기
driver.get(url)
time.sleep(8) # 코드 수행 환경에 따라 페이지가 로드되는 데 시간이 더 걸릴 수 있어 8초로 변경(2022/01/11)
# 첫 번째 게시물 클릭
select_first(driver)
# 본격적으로 데이터 수집 시작
results = []
## 수집할 게시물의 수
target = 10000
for i in range(target):
    try:
        data = get_content(driver)
        results.append(data)
        move_next(driver)
    except:
        time.sleep(2)
        move_next(driver)
print(results[:2])
# 결과를 데이터프레임으로 저장
# 2022/04/03 수정
import pandas as pd
from datetime import datetime
date = datetime.today().strftime('%Y-%m-%d')
results_df = pd.DataFrame(results)
results_df.columns = ['content','date','like','place','tags']
results_df.to_excel(date + '_about '+word+' insta crawling.xlsx')

'''

# 2023/06/30
from selenium import webdriver
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
import time
import re
import time
# 함수 정의: 검색어 조건에 따른 url 생성
def insta_searching(word):
    url = "https://www.instagram.com/explore/tags/" + str(word)
    return url
# 함수 정의: 열린 페이지에서 첫 번째 게시물 클릭 + sleep 메소드 통하여 시차 두기
def select_first(driver):
    first = driver.find_element(By.CSS_SELECTOR, "._aagu")   
    first.click()
    time.sleep(3)

# 함수 정의: 본문 내용, 작성일자, 좋아요 수, 위치 정보, 해시태그 가져오기
import re
from bs4 import BeautifulSoup
def get_content(driver):
    html = driver.page_source
    soup = BeautifulSoup(html, 'lxml')
    # 본문 내용
    try:
        content = soup.select('div._a9zs')[0].text
    except:
        content = ''
    # 해시태그
    tags = re.findall(r'#[^\s#,\\]+', content)
    data = [content, tags]
    return data
# 함수 정의: 첫 번째 게시물 클릭 후 다음 게시물 클릭
def move_next(driver):
    right = driver.find_element(By.CSS_SELECTOR, "svg[aria-label='다음']") # 2023/07/03
    right.click()
    time.sleep(3)

    
# 크롤링 시작
"""
driver.get(url)을 통해 검색 페이지 접속하고,
target 변수에 크롤링할 게시글의 수를 바인딩
"""
# 크롬 브라우저 열기
driver = webdriver.Chrome('chromedriver.exe')
driver.get('https://www.instagram.com')
time.sleep(3)
# 인스타그램 로그인을 위한 계정 정보
email = 'icex__o'
input_id = driver.find_element(By.XPATH, '//*[@id="loginForm"]/div/div[1]/div/label/input')
input_id.clear()
input_id.send_keys(email)
password = 'Ejqmf9866!'
input_pw =driver.find_element(By.XPATH, '//*[@id="loginForm"]/div/div[2]/div/label/input')
input_pw.clear()
input_pw.send_keys(password)
input_pw.submit()
time.sleep(5)
# 게시물을 조회할 검색 키워드 입력 요청
word = input("검색어를 입력하세요 : ")
word = str(word)
url = insta_searching(word)
# 검색 결과 페이지 열기
driver.get(url)
time.sleep(8) # 코드 수행 환경에 따라 페이지가 로드되는 데 시간이 더 걸릴 수 있어 8초로 변경(2022/01/11)
# 첫 번째 게시물 클릭
select_first(driver)
# 본격적으로 데이터 수집 시작
results = []
## 수집할 게시물의 수
target = 500
i = 0
for i in range(target):
    try:
        data = get_content(driver)
        results.append(data)
        move_next(driver)
    except:
        time.sleep(2)
        move_next(driver)
    i += 1
    print(i)

#print(results[:2])
print(results)
# 결과를 데이터프레임으로 저장
# 2022/04/03 수정
import pandas as pd
results_df = pd.DataFrame(results)
results_df.columns = ['content','tags']
results_df.to_csv(r'C:\ITWILL\공모전\버거킹.csv', encoding='utf-8-sig')