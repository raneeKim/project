import pandas as pd


m1 = pd.read_excel(r'C:\ITWILL\공모전\라벨링데이터\롯데리아(통합).xlsx')
m1.info()
content = []


for i in m1['content'] :
    if type(i) is str :
        i = i.replace('롯데리아','롯데리아자')
        i = i.replace('롯리','롯리자')
        i = i.replace('버거킹','버거킹타')
        i = i.replace('버거왕','버거왕타')
        i = i.replace('맥도날드','맥도날드타')
        i = i.replace('맥날','맥날타')
        content.append(i)
    else :
        content.append(i)

m1['content']= content

m1.to_excel(r'C:\ITWILL\공모전\라벨링데이터\롯데리아(통합)_자.xlsx', index=False)


m2 = pd.read_excel(r'C:\ITWILL\공모전\라벨링데이터\맥도날드(통합).xlsx')

content = []

for i in m2['content'] :
    if type(i) is str :
        i = i.replace('롯데리아','롯데리아타')
        i = i.replace('롯리','롯리타')
        i = i.replace('버거킹','버거킹타')
        i = i.replace('버거왕','버거왕타')
        i = i.replace('맥도날드','맥도날드자')
        i = i.replace('맥날','맥날자')
        content.append(i)
    else :
        content.append(i)

m2['content']= content

m2.to_excel(r'C:\ITWILL\공모전\라벨링데이터\맥도날드(통합)_자.xlsx', index=False)


m3 = pd.read_excel(r'C:\ITWILL\공모전\라벨링데이터\버거킹(통합).xlsx')
content = []

for i in m3['content'] :
    if type(i) is str :
        i = i.replace('롯데리아','롯데리아타')
        i = i.replace('롯리','롯리타')
        i = i.replace('버거킹','버거킹자')
        i = i.replace('버거왕','버거왕자')
        i = i.replace('맥도날드','맥도날드타')
        i = i.replace('맥날','맥날타')
        content.append(i)
    else :
        content.append(i)

m3['content']= content
m3.to_excel(r'C:\ITWILL\공모전\라벨링데이터\버거킹(통합)_자.xlsx', index=False)

m1 = m1.loc[(m1['target']==1) | (m1['target']==0) , 'content' :'target']
m2 = m2.loc[(m2['target']==1) | (m2['target']==0) , 'content' :'target']
m3 = m3.loc[(m3['target']==1) | (m3['target']==0) , 'content' :'target']

m1.info()
m2.info()
m3.info()
m4 = pd.concat([m1,m2,m3])
m4.info()
m4.to_excel(r'C:\ITWILL\공모전\라벨링데이터\통합_자.xlsx', index=False)