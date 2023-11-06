from selenium import webdriver
from selenium.webdriver.common.by import By
import re
import time
from bs4 import BeautifulSoup
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException
from tqdm import tqdm

driver = webdriver.Chrome(executable_path=r'C:\ITWILL\project\tools\chromedriver_win32\chromedriver.exe')
 # 웹드라이버가 설치된 경로를 지정해주시면 됩니다.
keyword = input("검색어를 입력하세요 : ")
naver_map_search_url = f'https://map.naver.com/v5/search/{keyword}/place' # 검색 url 만들기
driver.get(naver_map_search_url) # 검색 url 접속 = 검색하기
time.sleep(17) # 중요

b = driver.find_element(By.CSS_SELECTOR, ".place_on_pcamp")
b.click()
cu = driver.current_url
print(cu)
res_code = re.findall(r"place/(\d+)", cu)
print(res_code)
final_url = f'https://pcmap.place.naver.com/restaurant/{res_code[0]}/review/visitor#'
print(final_url)
driver.get(final_url)
time.sleep(5)
for i in range(2):
    next = driver.find_element(By.CSS_SELECTOR, ".lfH3O")
    next.click()
    time.sleep(3)
html = driver.page_source
soup = BeautifulSoup(html, 'lxml')
time.sleep(1)
result =[]
one_review = soup.find_all('div', attrs = {'class':'ZZ4OK'})
print(len(one_review))
for i in range(len(one_review)):
            try:
                review_content = one_review[i].find('span', attrs = {'class':'zPfVt'}).text
            except: # 리뷰가 없다면
                pass
            print('리뷰 내용 : '+review_content)
            result.append(review_content)
print(result)
import pandas as pd
a= pd.DataFrame(result)
a.to_excel(keyword+'.xlsx',index=False,encoding='cp949')