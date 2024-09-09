from sklearn.cluster import KMeans
import matplotlib.pyplot as plt
from sklearn.preprocessing import StandardScaler
import pandas as pd

# 국가를 cluster 하여 각 군집을 대표하는 나라 뽑기
df1= pd.read_csv(r'C:\ITWILL\trade_project\data\country_2022.csv' , encoding='utf-8')
df1.head()

df2 = pd.read_csv(r'C:\ITWILL\trade_project\GDP.csv', sep=',', encoding='utf-8')
df2.head()

df3 = pd.merge(df1, df2, on='국가명')
df3.head()
df3.to_csv(r'C:\ITWILL\trade_project\data\최종나라목록_2022.csv', encoding='ANSI', index=False)

# 군집분석용 변수 추가
df4 = pd.read_csv(r'C:\ITWILL\trade_project\data\환율.csv', encoding='ANSI')
df5 = pd.read_csv(r'C:\ITWILL\trade_project\data\국제금리.csv', encoding='ANSI')
df4.info()
df5.info()
country_name = []
for i in df4['국가(통화단위)별'] :
    a = i.split('(')
    country_name.append(a[0])

df4['국가명'] = country_name
df4['환율'] = df4['2021']
df4 = df4[['국가명','환율']]
df5['국가명'] = df5['국가별']
df5['대출금리'] = df5['2021.2']
df5 = df5[['대출금리','국가명']]


len(df3) # 144
merged = pd.merge(df3,df4, on='국가명')
len(merged) # 108
merged2 = pd.merge(merged,df5, on='국가명')
merged2 = merged2[['국가명','무역수지','국내총생산','1인당 총생산','환율','대출금리']] 
len(merged2) # 78, data개수손실이 커 대출금리는 사용X

# 결측치 처리
merged.isnull().sum()
merged = merged.dropna()

merged.info()

merged.corr(method='pearson')
merged.describe()

# 각 변수 float형으로 변환
def re_float(a) :
    a = a.str.replace(',', '').astype('float')
    return a

merged['수출건수'] = re_float(merged['수출건수'])
merged['수출금액'] = re_float(merged['수출금액'])
merged['수입건수'] = re_float(merged['수입건수'])
merged['수입금액'] = re_float(merged['수입금액'])
merged['무역수지'] = re_float(merged['무역수지'])

# 상관분석 시각화
import seaborn as sns

df_segmentation = merged.drop('cluster', axis = 1)
df_segmentation.info()
df_segmentation = df_segmentation.rename(columns={'국가명': 'Country Name', '수출건수': 'Export Weight', '수출금액': 'Export Value','수입건수': 'Import Weight','수입금액': 'Import Value', '무역수지' : 'Trade Balance', '국내총생산' : 'GDP', '1인당 총생산' : 'per capita GDP', '환율' : 'Exchange Rate'})
df_segmentation

plt.figure(figsize = (12, 9))
s = sns.heatmap(df_segmentation.corr(),
               annot = True, 
               cmap = 'RdBu',
               vmin = -1, 
               vmax = 1)

s.set_yticklabels(s.get_yticklabels(), rotation = 0, fontsize = 12)
s.set_xticklabels(s.get_xticklabels(), rotation = 90, fontsize = 12)
plt.title('Correlation Heatmap')
plt.show()



# 자료 표준화
merged2 = merged.drop(['국가명'], axis=1)
scaler = StandardScaler()
merged2 = scaler.fit_transform(merged2)


# best cluster 찾기
size = range(1, 11) # k값 범위
inertia = [] # 응집도 (중심점과 포인트 간 거리 제곱합)

for k in size : 
    obj = KMeans(n_clusters = k) 
    model = obj.fit(merged2)
    inertia.append(model.inertia_) 

print(inertia)

# 시각화
plt.plot(size, inertia, '-o')
plt.xticks(size)
plt.show()


# 클러스터링
kmeans = KMeans(n_clusters=3, random_state=10)
clusters = kmeans.fit(merged2)


# 클러스터 변수추가
merged['cluster'] = clusters.labels_
merged['cluster'].value_counts()

merged[merged['cluster']==0]
merged[merged['cluster']==1]

merged.groupby('cluster').mean()
merged.to_csv(r'C:\ITWILL\trade_project\data\merged(최종).csv', encoding='ANSI')


# 계층적군집분석
from scipy.cluster.hierarchy import linkage, dendrogram 

hier_clust = linkage(merged2, method = 'ward')
plt.figure(figsize = (12,9))
plt.title('Hierarchical Clustering Dendrogram')
plt.xlabel('Observations')
plt.ylabel('Distance')
dendrogram(hier_clust,
           truncate_mode = 'level',
           p = 5,
           show_leaf_counts = True,
           no_labels = False,
           )
plt.show()



# 각 클러스터 상위 25% 추출
cluster2 = merged[merged['cluster']==2]
cluster2 = cluster2[cluster2['무역수지'] >= cluster2['무역수지'].quantile(.75)]
cluster2.info()
cluster2.to_csv(r'C:\ITWILL\trade_project\data\cluster2.csv', encoding='ANSI')

cluster1 = merged[merged['cluster']==1]
cluster1.to_csv(r'C:\ITWILL\trade_project\data\cluster1.csv', encoding='ANSI')
cluster0 = merged[merged['cluster']==0]
cluster0.to_csv(r'C:\ITWILL\trade_project\data\cluster0.csv', encoding='ANSI')

