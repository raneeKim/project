import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
import time
import re
from bs4 import BeautifulSoup



'''
['버거킹 장안SK점','버거킹 위례신도시GS점',
 '버거킹 평촌금성GS점','버거킹 구리SK점','버거킹 녹번대성GS점','버거킹 광명소하DT점','버거킹 쌍문SK점','버거킹 박석고개SK점','버거킹 수지대경GS점',
 '버거킹 죽전DT점',]
'''

place = ['버거킹 울산구영DT점','버거킹 아산배방DT점','버거킹 포항대도DT점','버거킹 제주함덕DT점','버거킹 전주인후DT점','버거킹 김해구산DT점','버거킹 평택죽백DT점','버거킹 세종조치원','버거킹 부산신평DT점','버거킹 부산명지점','버거킹 포항두호점','버거킹 진해자은점','버거킹 평택안중DT점','버거킹 진해신항DT점','버거킹 서김해DT점','버거킹 부산영도DT점','버거킹 울산호계DT점','버거킹 천안원성DT점','버거킹 경주용강점','버거킹 울산북구청DT점','버거킹 동김해DT점','버거킹 진해충무점','버거킹 안성공도DT점','버거킹 송죽DT점','버거킹 속초점','버거킹 의정부용현 DT','버거킹 인천송도 DT','버거킹 영종하늘도시DT점','버거킹 대구평리점','버거킹 대구죽전네거리 DT','버거킹 대전터미널 DT','버거킹 분당상록점','버거킹 연세로점','버거킹 길동사거리점','버거킹 평촌금성GS점','버거킹 사당역점','버거킹 청담점','버거킹 구리SK점','버거킹 공릉역점','버거킹 개봉점','버거킹 부평시장역점','버거킹 전남대후문점','버거킹 상록수역점','버거킹 하남미사점','버거킹 인천주안점','버거킹 건대입구역점','버거킹 신논현역점','버거킹 대전둔산1점','버거킹 시흥정왕점','버거킹 불광점']


results = []

for i in place :
    driver = webdriver.Chrome(executable_path=r'C:\ITWILL\project\tools\chromedriver_win32\chromedriver.exe') # 웹드라이버가 설치된 경로를 지정해주시면 됩니다.

    naver_map_search_url = f'https://map.naver.com/v5/search/{i}/place' # 검색 url 만들기
    driver.get(naver_map_search_url) # 검색 url 접속 = 검색하기
    time.sleep(17)

    cu = driver.current_url
    res_code = re.findall(r"place/(\d+)", cu)
    final_url = f'https://pcmap.place.naver.com/restaurant/{res_code[0]}/review/visitor/#'
    driver.get(final_url)
    time.sleep(5)
    for j in range(19) :
        next = driver.find_element(By.CSS_SELECTOR, ".lfH3O")
        next.click()
        time.sleep(3)
        html = driver.page_source
        soup = BeautifulSoup(html, 'lxml')
        time.sleep(1)
    
    one_review = soup.find_all('div', attrs = {'class':'ZZ4OK'})
    for k in range(len(one_review)):
        try:
            review_content = one_review[k].find('span', attrs = {'class':'zPfVt'}).text
        except: # 리뷰가 없다면
            pass
        results.append(review_content)


a= pd.DataFrame(results)
a.to_csv(r'C:\ITWILL\공모전\버거킹.csv', encoding='utf-8-sig')


'''
df = pd.read_csv('원하는 플레이스 정보가 담긴 파일.csv') 
df['naver_map_url'] = '' # 미리 url을 담을 column을 만들어줌 
'''

'''
while True: 
    try:
        time.sleep(1) 
        driver.find_element_by_tag_name('body').send_keys(Keys.END) 
        time.sleep(3) 
        
        driver.find_element_by_css_selector('#app-root > div > div.place_detail_wrapper > div:nth-child(5) > div:nth-child(4) > div:nth-child(4) > div._2kAri > a').click() 
        time.sleep(3) 
        driver.find_element_by_tag_name('body').send_keys(Keys.END) 
        time.sleep(1) 
        
    except NoSuchElementException: 
        print('-더보기 버튼 모두 클릭 완료-') 
        break 
'''

 # 검색이 성공된 플레이스에 대한 개별 페이지
  
'''
review = driver.find_elements(By.CSS_SELECTOR, "PXMot") # 2023/07/03
print(review)

right.click()

final_url = driver.current_url
req = urlopen(final_url)  # ulr 요청 
byte_data = req.read() # data 읽기   
text_data = byte_data.decode("utf-8")
html = BeautifulSoup(text_data, 'html.parser')



print(final_url)
'''