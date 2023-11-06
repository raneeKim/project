from selenium import webdriver
from selenium.webdriver.common.by import By
import time
import re
from bs4 import BeautifulSoup
from selenium.webdriver.common.keys import Keys

driver = webdriver.Chrome(executable_path=r'C:\ITWILL\project\tools\chromedriver_win32\chromedriver.exe')
final_url = 'https://pcmap.place.naver.com/restaurant/1925445175/review/visitor#'

driver.get(final_url)
time.sleep(5)

html = driver.page_source 
soup = BeautifulSoup(html, 'lxml')
time.sleep(1)

cnt = soup.find_all('span', attrs = {'class':'PXMot'})
print(cnt)
review_counts = cnt[1]
review_count = review_counts.find('em').text


# 더보기 버튼 다 누를 것
# 더보기 버튼은 10개 마다 나옴

while True:
    try:
        time.sleep(1)
        driver.find_element(By.TAG_NAME,value='body').send_keys(Keys.END)
        time.sleep(3)
        driver.find_element(By.CSS_SELECTOR, ".lfH3O").click()
        time.sleep(3)
        driver.find_element(By.TAG_NAME,value='body').send_keys(Keys.END)
        time.sleep(1)
    except :
        print('-더보기 버튼 모두 클릭 완료-')
        break

time.sleep(10)

'''
<span class="PXMot"><a class="place_bluelink" 
href="/restaurant/1687420221/review/visitor" role="button">방문자리뷰<!-- --> <em>5,635</em></a></span>

'''



one_review = soup.find_all('div', attrs = {'class':'ZZ4OK'})
print(len(one_review))
review = []

for i in range(len(one_review)): 
            try: 
                review_content = one_review[i].find('span', attrs = {'class':'zPfVt'}).text
            except: # 리뷰가 없다면
                pass
            review.append(review_content)

print(review)