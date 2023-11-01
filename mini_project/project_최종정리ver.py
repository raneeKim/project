# -*- coding: utf-8 -*-
"""
Created on Mon Mar 27 15:24:22 2023

@author: ITWILL
"""

import FinanceDataReader as fdr # 주식
import pandas as pd
import matplotlib.pyplot as plt # 그래프 그리기
import urllib.request as req  # url 가져오기 
from bs4 import BeautifulSoup
import re
import datetime # 전후 n일 뽑기위해
from wordcloud import WordCloud # class - 단어 구름 시각화 
from collections import Counter # 단어 카운트 

def stock7_func(stock_num):
    
    stock = fdr.DataReader(stock_num, start='2022-02-01', end='2023-03-22')
    len(stock) # 281
    big_change = stock[stock['Change']==max(stock.Change)]
    small_change = stock[stock['Change']==min(stock.Change)]
    
    # 변화량 max date
    big_change_index = big_change.index # date 뽑기
    Big = str(big_change_index[0]).split()[0]
    Bbefore = big_change_index - datetime.timedelta(days=14) # 변화량 크기 전 14일
    Bbefore = str(Bbefore[0]).split()[0] # 날짜만 뽑기 전 str형 변환    
    Before = Bbefore.split()[0] # 시간 제외, 날짜만 뽑기
    
    # 변화량 min date
    small_change_index = small_change.index # date 뽑기
    Small = str(small_change_index[0]).split()[0]
    Sbefore = small_change_index - datetime.timedelta(days=14) # 변화량 가장 작은 전 14일
    Sbefore = str(Sbefore[0]) # 날짜만 뽑기 전 str형 변환
    Sbefore = Sbefore.split()[0] # 시간 제외, 날짜만 뽑기
    
    
    return Bbefore,Big,Sbefore,Small




def crawler7_func(Bdate,Adate,stock_name,pages=200):  
    
    title =[]
    subnews = []
    
    for page in range(1, pages+1) : 
        
        # 1) url 구성 
        url = f"https://finance.naver.com/news/news_search.naver?rcdate=&q={stock_name}&x=0&y=0&sm=all.basic&pd=4&stDateStart={Bdate}&stDateEnd={Adate}&page={page}" 
        # 2) url 요청          
        res = req.urlopen(url)
        data = res.read()
        
        # 3) html 파싱
        src = data.decode('euc-kr') 
        html = BeautifulSoup(src, 'html.parser')
        
        # 4) a 태그 수집                  
        step1 = html.select('#contentarea_left > div > dl > dd > a') 
                         # //*[@id="contentarea_left"]/div[2]/dl/dd[1]/a
        
        
        title_list = []
        
        for t in step1 :
            title_step2 = str(t.text).strip()
            title_list.append(title_step2)
        title.extend(title_list)
        
        
        # 5) 보조기사 수집
        news_step1 = html.select('#contentarea_left > div > dl > dd')
        print(news_step1)
        
        subnews_list =[]
        
        for n in news_step1 :
            sub = str(n.text)
            sub = re.sub('[\t\n]','',sub)
            #sub = sub.split('...') # 보조기사에서 언론사,기사날짜 제거 : ...으로 구별 불가능
            #sub = sub[0] 
            #print(sub)
            subnews_list.append(sub)
        subnews.extend(subnews_list)
        #print(news_list)
    #news = pd.DataFrame({"Title": title, "SubNews": subnews}) : title,subnews 수 다름
        #print(url)
        
    
    return title,subnews

dates = ['2022-03-07','2022-04-13','2022-04-29','2022-06-13','2022-07-07',
         '2022-07-18','2022-09-13','2022-10-04','2022-10-24','2022-10-28',
         '2022-10-31','2022-11-08','2022-11-11','2022-11-30','2022-12-02']
B_dates = []

import datetime

# 날짜형
cur_datetime = datetime.datetime.strptime(dates, '%Y-%m-%d %H:%M:%S')
for date in dates :  
    before = date - datetime.timedelta(days=2) # 변화량 크기 전 14일
    before = str(before[0]).split()[0] # 날짜만 뽑기 전 str형 변환    
    before = before.split()[0] # 시간 제외, 날짜만 뽑기
    B_dates.append(before)

samsung = stock7_func('005930') # %BB%EF%BC%BA
sm # ('2022-09-02', '2022-09-16', '2023-02-27', '2023-03-13')

Bchange_sm = crawler7_func(sm[0],sm[1],'%BF%A1%BD%BA%BF%A5')
SM = Bchange_sm[0] + Bchange_sm[1]

def clean_text(texts) :
    from re import sub # 함수 임포트

    # 단계1 : 소문자 변경
    # texts_re = [t.lower() for t in texts]

    #단계2 : 숫자 제거 : 변수 = [실행문(method/func) for 변수 in 열거형객체]
    texts_re = [sub('[0-9]', '', t) for t in texts]

    # 단계3 : 문장부호 제거
    punc_str = '[\',.?!:;\"…]'
    texts_re2 = [sub(punc_str, '', t) for t in texts_re]

    # 단계4 : 특수문자 제거
    spec_str = '[@#$%^&◇△|*()-_\[\]]'
    texts_re3 = [sub(spec_str, '', t) for t in texts_re2]

    # 단계5 : 공백(white space) 제거
    texts_re4 = [' '.join(t.split()) for t in texts_re3]

    return texts_re4

#################################### 기사번역 -> 단어추출

clean_news_title = clean_text(SM) 
print(clean_news_title)


import googletrans # 기사번역을 위해
translator = googletrans.Translator() # 객체생성

news_title = []
for title in clean_news_title:
    try : 
        result =  translator.translate(title, dest='en')
    #print(result.text)
        news_title.append(result.text)
    except : 
        pass
news_title


clean_eng_news = clean_text(news_title) 


from konlpy.tag import Okt # class - 형태소 
okt = Okt()

import nltk # Natural Laguage Toolkit
nltk.download('punkt') # nltk data download
from nltk.tokenize import word_tokenize # 문장 -> 단어 token
nltk.download("stopwords") # 라이브러리 다운
from nltk.corpus import stopwords #  불용어제거

news_word = []
for title in clean_eng_news : 
    result = word_tokenize(title)
    news_word.extend(result)
print(news_word)
len(news_word) # 1324

stopwords.words('english')
 
news_stopwords = []   
for w in news_word :
    if w not in stopwords.words('english') :
            news_stopwords.append(w)
    else :
        pass
print(news_stopwords)

wcf = {}

for word in news_stopwords :
     wcf[word] = wcf.get(word, 0) + 1
    

print(wcf)

# top10 단어 선정

count = Counter(news_stopwords) 

top10_word = count.most_common(10)  
print(top10_word) # [('단어',빈도수)]

# 단어와 출현빈도수 추출 
words = []
cnt = []

for (w,c) in top10_word :
    words.append(w)
    cnt.append(c)

#print(words)
#print(cnt)


# word cloud

wc = WordCloud(font_path='C:/Windows/Fonts/malgun.ttf',
          width=500, height=400,
          max_words=100,max_font_size=150,
          background_color='white')

wc_result = wc.generate_from_frequencies(dict(wcf))

plt.imshow(wc_result)
plt.axis('off') # 축 눈금 감추기 
plt.show()


############################# 한글단어 추출 -> 번역


# title 단어
nouns_word = [] # 명사 저장 
for word in clean_news_title : 
    for noun in okt.nouns(word) : # 문장(1개) -> 명사, 서수 제외(okt)
        nouns_word.append(noun)

print(nouns_word)
words = []
for word in nouns_word :
    if len(word) > 1 :
        words.append(word)
print(words)


eng_word = []
for word in words:
    try : 
        result =  translator.translate(word, dest='en')
    #print(result.text)
        eng_word.append(result.text)
    except : 
        pass
print(eng_word)


del wcf['엠']

count = Counter(wcf) # Counter object 생성
''

# date,news 다 크롤링
    
samsung_news = []
samsung_date = []

for i in range(0,29) :
    samsung2 = crawler_func(B_dates[i],dates[i],'%BB%EF%BC%BA')
    samsung_date.extend(samsung2[0]) # 날짜부분
    samsung_news.extend(samsung2[1]) # title + sub news 부분

len(samsung_date) # 35395 
len(samsung_news) # 35395 

news = pd.DataFrame({"Date": samsung_date, "News": samsung_news})
news.to_csv(r'C:\ITWILL\3_TextMining\news.csv',index=None, encoding='utf-8') # csv파일 저장
print(news)
news[0]

# TEST용
article_dict = {}
for i in range(0,2) :
    key = samsung_date[i]
    value = samsung_news[i]
    article_dict[key] = value

print(article_list['2022-03-07'])

for s in samsung_news:
    for news in s:
        real_samsung.append(news)


#################################### 기사번역 -> 단어추출




import os
print('\n현재 경로 :', os.getcwd())  
os.chdir(r'C:\ITWILL\3_TextMining')
f = open('eng_news.txt', mode = 'w')
f.close() 

for news in news_title : 
    f2 = open('eng_news.txt', mode = 'a',encoding='utf-8') # 1. 생성
    f2.write(news)   # 2. 사용
    f2.write('\n')
    f2.close() 



clean_eng_news = clean_text(news_title) 


from konlpy.tag import Okt # class - 형태소 
okt = Okt()

import nltk # Natural Laguage Toolkit
nltk.download('punkt') # nltk data download
from nltk.tokenize import word_tokenize # 문장 -> 단어 token
nltk.download("stopwords") # 라이브러리 다운
from nltk.corpus import stopwords #  불용어제거

news_word = []
for title in clean_eng_news : 
    result = word_tokenize(title)
    news_word.extend(result)
print(news_word)
len(news_word) # 521655

stopwords.words('english')
 
news_stopwords = []   
for w in news_word :
    if w not in stopwords.words('english') :
            news_stopwords.append(w)
    else :
        pass
print(news_stopwords)
len(news_stopwords) # 369041 (불용어제거 후)

eng_clean_news_words = []
for i in news_stopwords:
    if len(i) > 1 :
        eng_clean_news_words.append(i)

wcf = {}

for word in eng_clean_news_words :
     wcf[word] = wcf.get(word, 0) + 1


print(wcf)

# top10 단어 선정

count = Counter(eng_clean_news_words) 

top10_word = count.most_common(10)  
print(top10_word) # [('단어',빈도수)]

# 단어와 출현빈도수 추출 
words = []
cnt = []

for (w,c) in top10_word :
    words.append(w)
    cnt.append(c)

#print(words)
#print(cnt)


# word cloud

wc = WordCloud(font_path='C:/Windows/Fonts/malgun.ttf',
          width=500, height=400,
          max_words=100,max_font_size=150,
          background_color='white')

wc_result = wc.generate_from_frequencies(dict(wcf))

plt.imshow(wc_result)
plt.axis('off') # 축 눈금 감추기 
plt.show()


# pip install afinn

##### 준호님 감성분석 코드

import statistics as stat
# pip install -U textblob nltk
import nltk
from textblob import TextBlob

result = TextBlob(news_stopwords[0])

positive_titles = []
negative_titles = []

for word in news_stopwords:
    sentiment = TextBlob(word).sentiment.polarity
    if sentiment > 0:
        positive_titles.append((word, sentiment))
    elif sentiment < 0:
        negative_titles.append((word, sentiment))

print("Positive titles:")
for ptitle, psentiment in positive_titles:
    print(f"{ptitle}: {psentiment}")

print("\nNegative titles:")
for ntitle, nsentiment in negative_titles:
    print(f"{ntitle}: {nsentiment}")


positive = pd.DataFrame(positive_titles)
positive[1]

stat.mean(positive[1]) # 긍정수치 평균

negative = pd.DataFrame(negative_titles)
negative

stat.mean(negative[1]) # 부정수치 평균 