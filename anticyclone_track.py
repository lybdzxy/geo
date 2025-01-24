import xarray as xr
import numpy as np
import math

data_path = 'E:/GEO/test/test.nc'
data = xr.open_dataset(data_path)
lons = np.arange(0.25, 360, 0.25)
lats = np.arange(-89.75, 90, 0.25)
valid_times = data['valid_time'].values  # 获取时间序列的值

scale_factor = 310
max_distance = 1200

# 初始化结果列表
results = []

# 主循环
for time_index in range(len(valid_times)):
    current_time = valid_times[time_index]  # 当前时间
    list_data = []  # 每次time循环开始时清空列表

    for lon in lons:
        for lat in lats:
            # 获取当前经纬度的数据
            test = data.sel(valid_time=current_time, longitude=lon, latitude=lat)['sp'].values
            n = 1
            for la in (0.25, 0, -0.25):
                for lo in (0.25, 0, -0.25):
                    if la == 0 and lo == 0:
                        continue
                    new_lon = lon + lo
                    new_lat = lat + la
                    beside = data.sel(valid_time=current_time, longitude=new_lon, latitude=new_lat)['sp'].values
                    if la == 0 or lo == 0:
                        distance = 31
                    else:
                        distance = 31 * math.sqrt(2)
                    gradient = (test - beside) / distance

                    if gradient <= 0.15:
                        n = 0  # 直接赋值为0，避免乘法

            if n == 1:  # 如果n仍然是1，说明符合条件
                coor = [lon, lat, test]
                print(coor)
                list_data.append(coor)

    # 处理相近点合并
    while len(list_data) > 1:
        distances = []
        for i in range(len(list_data)):
            for j in range(i + 1, len(list_data)):
                x1, y1 = list_data[i][0], list_data[i][1]
                x2, y2 = list_data[j][0], list_data[j][1]
                distance = math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2) * scale_factor
                distances.append((distance, i, j))

        if not distances:
            break

        distances.sort(key=lambda x: x[0])
        closest_distance, i, j = distances[0]

        if closest_distance > max_distance:
            break

        # 合并两个点
        new_point = [
            (list_data[i][0] + list_data[j][0]) / 2,
            (list_data[i][1] + list_data[j][1]) / 2,
            list_data[i][2]  # 选择其中一个数据值
        ]
        list_data[i] = new_point
        del list_data[j]

    # 保存结果
    file_name = f'E:/GEO/test/anticyclone/time_{time_index}.txt'
    with open(file_name, 'w') as f:
        for item in list_data:
            f.write(f"{item[0]}, {item[1]}, {item[2]}\n")
