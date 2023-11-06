
from selenium import webdriver
from bs4 import BeautifulSoup
import pandas as pd
from selenium.webdriver.chrome.options import Options



path = r'C:\ITWILL\공모전\data'
data = pd.read_csv(path+'\표준품명(2023).csv', encoding='cp949')
hscode = data['HS부호']
hscode2 = hscode[768:]

balpayments2 = []
expDlr2 = []
expWgt2 = []
hsCode2 = []
impDlr2 = []
impWgt2 = []
name2 = []
date2 = []
cnt = 0

for hs in hscode2 :

    chrome_options = Options()
    chrome_options.add_argument("--headless")

    if len(str(hs))==9 :
        driver = webdriver.Chrome()
        driver.get(f'https://apis.data.go.kr/1220000/Itemtrade/getItemtradeList?serviceKey=4zvIP%2BsjQwMdl1yNBQ3J7lWEUZ9LELXYe9lqSwA%2Fp%2FnO8YILy68BJO6vaSASPmZ6fd85YN9pj%2FLRPxZ5vdPbIg%3D%3D&strtYymm=201701&endYymm=201712&hsSgn=0{hs}')
    else :
        driver = webdriver.Chrome()
        driver.get(f'https://apis.data.go.kr/1220000/Itemtrade/getItemtradeList?serviceKey=4zvIP%2BsjQwMdl1yNBQ3J7lWEUZ9LELXYe9lqSwA%2Fp%2FnO8YILy68BJO6vaSASPmZ6fd85YN9pj%2FLRPxZ5vdPbIg%3D%3D&strtYymm=201701&endYymm=201712&hsSgn={hs}')

    src = driver.page_source
    soup = BeautifulSoup(src, 'lxml') # xml파일 파싱 방법
   
    balpayments = []
    expDlr = []
    expWgt = []
    hsCode = []
    impDlr = []
    impWgt = []
    name = []
    date = []

    for i in soup.find_all('item') :
        bal = i.find('balpayments').text
        balpayments.append(bal)
            
        ed = i.find('expdlr').text
        expDlr.append(ed)
            
        ew = i.find('expwgt').text
        expWgt.append(ew)
            
        Hs = i.find('hscode').text
        hsCode.append(Hs)
            
        idr = i.find('impdlr').text
        impDlr.append(idr)
            
        iw = i.find('impwgt').text
        impWgt.append(iw)
            
        sk = i.find('statkor').text
        name.append(sk)
            
        year = i.find('year').text
        date.append(year)
            
    balpayments2.extend(balpayments)
    expDlr2.extend(expDlr)
    expWgt2.extend(expWgt)
    hsCode2.extend(hsCode)
    impDlr2.extend(impDlr)
    impWgt2.extend(impWgt)
    name2.extend(name)
    date2.extend(date)

    cnt += 1
    print(cnt)

    driver.quit()

len(name2)
        
df = pd.DataFrame( {'무역수지': balpayments2, '수출금액' : expDlr2, '수출중량' : expWgt2, 'hsCode' : hsCode2, 
                    '수입금액' : impDlr2, '수입중량':impWgt2, '한국품목명':name2, '날짜':date2})

index1 = df[df['날짜']=='총계'].index
df2 = df.drop(index1)


HS = [str[0:2] for str in df2['hsCode']]
df2['HS'] = HS
df2['무역수지'] = df2['무역수지'].astype('float32')

df2.to_csv(r'C:\ITWILL\공모전\data\품목별수출입실적2017.csv', index=False, sep='\t', encoding='utf-16')

df3 = pd.read_csv(r'C:\ITWILL\공모전\data\품목별수출입실적2017.csv',sep='\t', encoding='utf-16')

