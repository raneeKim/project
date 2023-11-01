import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import statsmodels.api as sm
from statsmodels.tsa.stattools import adfuller
import itertools
import warnings
warnings.filterwarnings('ignore')
import os


pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)

# 디렉토리 세팅
# 국가별,HS코드별,무역정보 추출
path = ''# working 디렉토리
os.chdir(path)
csv_files = ['cluster2_1__201701_202102.csv','cluster2_1__202102_202306.csv','cluster2_2__201701_202101.csv', 'cluster2_2__202102_202305.csv','cluster2_3__201701_202101.csv','cluster2_3__202102_202305.csv']


# 데이터 전처리
merged_df = pd.DataFrame()
for file in csv_files:
    data = pd.read_csv(file,encoding='utf-8')
    data.columns = ['Order Date', 'Product Name', 'Product Code', 'Country Name', 'Export Weight',
                    'Import Weight', 'Export Value', 'Import Value', 'Trade Balance']
    
    data = data.drop(range(5)).reset_index(drop=True)
    data['Order Date'] = pd.to_datetime(data['Order Date'])
    
    data['Export Weight'] = data['Export Weight'].str.replace(',', '').astype(float)
    data['Import Weight'] = data['Import Weight'].str.replace(',', '').astype(float)
    data['Export Value'] = data['Export Value'].str.replace(',', '').astype(float)
    data['Import Value'] = data['Import Value'].str.replace(',', '').astype(float)
    data['Trade Balance'] = data['Trade Balance'].str.replace(',', '').astype(float)
    merged_df = merged_df.append(data, ignore_index=True)

merged_df.to_csv('merged_data_cluster2_new.csv', index=False)

################################################################################


os.getcwd()

file_names = ['merged_data_cluster0_new.csv', 'merged_data_cluster1_new.csv', 'merged_data_cluster2_new.csv']

for file_name in file_names:
    cluster_data = pd.read_csv(file_name)
    
    country_count = cluster_data.groupby('Country Name')['Product Code'].count()
    print(f"Country Count for {file_name}:")
    print(country_count)
    
    prod_df2 = cluster_data.groupby('Product Code').mean()
    print(f"Product Mean for {file_name}:")
    print(prod_df2)
    
    # Sort by Trade Balance
    sorted_prod_df = prod_df2.sort_values('Trade Balance')
    print(f"Sorted Product Mean by Trade Balance for {file_name}:")
    print(sorted_prod_df)
    
    print("----------------------------------------------")
################################################################################


cluster0 = pd.read_csv('merged_data_cluster0_new.csv')
cluster0.head()
cluster0.info()
cluster0.describe()

cluster1 = pd.read_csv('merged_data_cluster1_new.csv')
cluster1.describe()
cluster1.info()

cluster2 = pd.read_csv('merged_data_cluster2_new.csv')
cluster2.describe()

# hscodes 전처리
hscodes = pd.read_csv('merged_hscode.csv')
hscodes.info()
hscodes.head()
hscodes.drop('hsCode', axis = 1, inplace = True)
hscodes.columns = ['Order Date', 'Trade Balance', 'Export Value', 'Export Weight', 'Import Value', 'Import Weight', 'HS Code']
hscodes.info()

'''
# 워드 클라우드
from wordcloud import WordCloud
# Select the 'Product Code' column from the DataFrame
product_codes = cluster2['Product Code']
# Count the frequency of each product code
product_code_counts = product_codes.astype(str).value_counts().head(15)
# Convert the product code counts to a dictionary format
product_code_dict = product_code_counts.to_dict()
# Create the word cloud
wordcloud = WordCloud(width=800, height=400, background_color='white').generate_from_frequencies(product_code_dict)
# Plot the word cloud
plt.figure(figsize=(10, 5))
plt.imshow(wordcloud, interpolation='bilinear')
plt.axis('off')
plt.title('Cluster 2',fontsize = 20)
plt.show()
'''

#######################################################

# 클러스터 0,1,2 마다 SARIMA 모델 예측을 위한 데이터 전처리 작업
cluster0.groupby('Product Code')['Trade Balance'].count()

# 품목 마다 데이터 필터 후 전처리
df = cluster2[(cluster2['Product Code']== 39)].sort_values('Order Date')
df.head()
df.info()

# Date 와 trade balance 로 예측
df = df.loc[:, df.columns.isin(['Order Date','Trade Balance'])].reset_index(drop = True)
df.head(10)

# 'Order Date' 를 datetime 으로 포멧시키기
df['Order Date'] = pd.to_datetime(df['Order Date'])

# 'Order Date' 를 인덱스로 바꾸기
df.set_index('Order Date', inplace=True)

test = df['Trade Balance']
test.plot()

# 'MS' frequency 로 각 월별 평균값 매기기
y = df['Trade Balance'].resample('MS').mean()

y.plot()
len(y) #48

# 훈련, 테스트 세트로 스플릿
y_train = y[:len(y)-11]
y_train

y_test = y[(len(y)-11):]
y_test

y_train.plot()
y_test.plot()

y_train.plot(figsize = (20,10))
plt.show()

# AD Fullter test 를 통한 시계열 데이터 정상성 확인

result = adfuller(y_train)
print('ADF Statistic: %f' % result[0])
print('p-value : %f' % result[1])
print('Critival Values : ')

for key, value in result[4].items():
    print('\t%s: %.3f' %(key,value))
'''
데이터가 unstationary하다면 차분을 통해 stationary하게 바꿔준다.
df['Trade Balance Diff'] = df['Trade Balance'].diff()
df = df[1:]
'''
len(y_train) #37
#ACF and PACF

p = d = q = range(0,2)

pdq = list(itertools.product(p,d,q)) 
seasonal_pdq = [(x[0], x[1], x[2], 12) for x in pdq]
seasonal_pdq

# SARIMA 모델 변수 최적화
metric_aic_dict = dict()
for pm in pdq:
    for pm_seasonal in seasonal_pdq :
        try:
            model = sm.tsa.statespace.SARIMAX(y_train,
                                              order = pm,
                                              seasonal_order = pm_seasonal,
                                              enforce_stationarity=False,
                                              enforce_invertibility=False
                                              )
            model_aic = model.fit()
            print("ARIMA{}xSEASONAL{}12 - AIC: {}".format(pm,pm_seasonal, model_aic.aic))
            metric_aic_dict.update({(pm,pm_seasonal): model_aic.aic})
        except:
            continue

dir(model_aic)
model_aic.aic

metric_aic_dict.items()

min_aic = min(metric_aic_dict.items(), key=lambda x: x[1])
print(min_aic)
# 최적화 모델

#(((0, 1, 1), (0, 1, 1, 12)), 1031.8627749588624)

{k: v for k,v in sorted(metric_aic_dict.items(), key = lambda x: x[1])}

# 최적화 모델 변수 선정후 모델 생성
model = sm.tsa.statespace.SARIMAX(y_train,
                                  order = (0,1,1),
                                  seasonal_order = (0,1,1,12)
                                  )

# 모델과 잔차 확인
model_aic = model.fit()
print(model_aic.summary().tables[1])

model_aic.plot_diagnostics(figsize=(16,8))
plt.show()

# 모델로 무역수지 예측
forecast = model_aic.get_prediction(start = pd.to_datetime('2022-07-01'), end = pd.to_datetime('2023-08-01'),dynamic = False)
prediction = forecast.predicted_mean
prediction

actual = y_test['2021-07-01':]
actual

forecast = model_aic.get_forecast(steps=12)

# 예측 신뢰구간
predictions = forecast.predicted_mean
predictions
ci = forecast.conf_int()

# 예측 vs 실제 데이터 그래프 시각화 + 미래 무역수지 예측
fig = y.plot(label='observed', figsize=(15,7))
fig.set_xlabel('Date')
fig.set_ylabel('Trade Balance')
predictions.plot(ax=fig, label='predicted', color='r')
fig.fill_between(ci.index,
                 ci.iloc[:,0],
                 ci.iloc[:,1], color = 'k', alpha = .2)
