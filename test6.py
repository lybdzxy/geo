import numpy as np
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
from sklearn.preprocessing import StandardScaler
import pandas as pd
# 读取Excel文件
data_path = f'E:/GEO/result/pca.xlsx'
data = pd.read_excel(data_path)
data = data.to_numpy()

# 选取后三列进行聚类
data_for_clustering = data

# 标准化数据
scaler = StandardScaler()
data_for_clustering_scaled = scaler.fit_transform(data_for_clustering)
# 定义聚类数量的范围
min_clusters = 2
max_clusters = 12

# 初始化最优轮廓系数和对应的聚类数量
best_score = -1
best_n_clusters = min_clusters

# 循环尝试不同的聚类数量
for n_clusters in range(min_clusters, max_clusters + 1):
    # 使用KMeans算法进行聚类
    kmeans = KMeans(n_clusters=n_clusters)
    kmeans.fit(data_for_clustering_scaled)

    # 获取聚类结果的轮廓系数
    silhouette_avg = silhouette_score(data_for_clustering_scaled, kmeans.labels_)
    print(silhouette_avg)
    # 如果当前轮廓系数更高，则更新最优值
    if silhouette_avg > best_score:
        best_score = silhouette_avg
        best_n_clusters = n_clusters

# 使用最优的聚类数量进行聚类
best_kmeans = KMeans(n_clusters=best_n_clusters)
best_kmeans.fit(data_for_clustering_scaled)

# 获取聚类标签
labels = best_kmeans.labels_

# 将聚类标签添加到原数据中
data_with_labels = np.column_stack((data, labels))
# 转换为 DataFrame
result_xl = pd.DataFrame(data_with_labels)

# 重新命名列
result_xl.columns = ['m','n','lon','lat', 'cluster']

# 将结果保存为Excel文件
result_xl.to_excel('E:/GEO/result/pca_km.xlsx', index=False)
result = {}
for i in data_with_labels:
    m,n,lon,lat, cluster = i
    result[(lon, lat)] = (m, n, cluster)
result_df = pd.DataFrame(result).T  # 转置数据

# 重新命名列
result_df.columns = ['m', 'n', 'cluster']

# 将结果保存为NetCDF文件
result_df.to_xarray().to_netcdf(f'E:/GEO/result/pca_km.nc')
