import xarray as xr
import matplotlib.pyplot as plt
import numpy as np
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import warnings
from matplotlib.path import Path
import math
# 读取上传的 netCDF 文件
file_path = 'E:/GEO/test/test_slp.nc'
data = xr.open_dataset(file_path)

# 获取经度、纬度和地表气压数据
lon = data['longitude'].values
lat = data['latitude'].values
pressure = data['msl'].values.squeeze() / 100  # 转换为百帕 (hPa)

# 只选择气压值大于等于1010 hPa的区域
pressure_above_1010 = np.where(pressure >= 1010, pressure, np.nan)

# 设置绘图区域
interval = 1
proj = ccrs.LambertAzimuthalEqualArea(central_longitude=0, central_latitude=90)
leftlon, rightlon, lowerlat, upperlat = (-180, 180, 20, 90)
img_extent = [leftlon, rightlon, lowerlat, upperlat]

# 绘制等压线图
fig1 = plt.figure(figsize=(20, 20))
f1_ax1 = fig1.add_axes([0.1, 0.1, 0.8, 0.8], projection=ccrs.NorthPolarStereo(central_longitude=0))
f1_ax1.gridlines(crs=ccrs.PlateCarree(), draw_labels=True, linewidth=1, color='k', linestyle='--')
f1_ax1.add_feature(cfeature.COASTLINE)
f1_ax1.set_extent(img_extent, ccrs.PlateCarree())

# 绘制等压线
contours = plt.contour(lon, lat, pressure_above_1010, levels=np.arange(1010, pressure.max(), interval),
                       transform=ccrs.PlateCarree(), colors='black')

# 查找闭合等压线
closed_contours = []
tolerance = 0.001
for c in contours.collections:
    for path in c.get_paths():
        # 提取路径的顶点和代码
        vertices = path.vertices  # 顶点数组
        codes = path.codes  # 操作代码 (MOVETO, LINETO, CLOSEPOLY)

        if codes is None:
            # 如果没有 codes，无法区分子路径，跳过
            continue

        # 初始化子路径的顶点收集器
        sub_path_vertices = []

        # 遍历路径中的每个点和操作代码
        for i, code in enumerate(codes):
            if code == Path.MOVETO:
                # 遇到新的子路径，清空当前的顶点收集器
                if sub_path_vertices:  # 如果之前的子路径未清空，检查是否闭合
                    if np.allclose(sub_path_vertices[0], sub_path_vertices[-1], atol=tolerance):
                        closed_contours.append(np.array(sub_path_vertices))  # 存储闭合子路径
                sub_path_vertices = [vertices[i]]  # 初始化新的子路径

            elif code == Path.LINETO:
                # 添加到当前子路径
                sub_path_vertices.append(vertices[i])

            elif code == Path.CLOSEPOLY:
                # 闭合子路径：直接检查起点和终点是否相等
                sub_path_vertices.append(vertices[i])
                if np.allclose(sub_path_vertices[0], sub_path_vertices[-1], atol=tolerance):
                    closed_contours.append(np.array(sub_path_vertices))
                sub_path_vertices = []  # 清空子路径

        # 检查最后一个子路径是否闭合
        if sub_path_vertices and np.allclose(sub_path_vertices[0], sub_path_vertices[-1], atol=tolerance):
            closed_contours.append(np.array(sub_path_vertices))


# 输出过滤结果
if not closed_contours:
    print("未找到符合半径要求的闭合等压线")
else:
    print(f"找到 {len(closed_contours)} 条符合半径要求的闭合等压线")

# 可视化符合要求的闭合等压线
for contour in closed_contours:
    f1_ax1.plot(contour[:, 0], contour[:, 1], transform=ccrs.PlateCarree(), color='red', linewidth=2)

plt.show()


# 构建包含关系字典
containment_dict = {}  # {outer_index: [inner_indices]}
for i, outer_path in enumerate(closed_contours):
    outer_polygon = Path(outer_path)
    containment_dict[i] = []  # 初始化列表
    for j, inner_path in enumerate(closed_contours):
        if i != j:
            if np.all(outer_polygon.contains_points(inner_path)):
                containment_dict[i].append(j)

# 清理包含关系
def simplify_containment(containment_dict):
    simplified_dict = containment_dict.copy()
    for parent, children in list(containment_dict.items()):
        if len(children) > 1:
            # 多子节点情况：移除当前节点，保留子节点
            del simplified_dict[parent]
            for child in children:
                if child in simplified_dict:
                    simplified_dict[child] = simplified_dict.get(child, [])
    return simplified_dict

# 提取最外层和最内层等压线
def find_outer_and_inner_after_simplification(simplified_dict):
    # 所有等压线索引
    all_contours = set(simplified_dict.keys())
    # 子节点集合
    inner_contours = {idx for inner_list in simplified_dict.values() for idx in inner_list}
    # 最外层：未被其他等压线包含
    outer_contours = list(all_contours - inner_contours)
    # 最内层：没有子节点
    inner_most_contours = [idx for idx, inner_list in simplified_dict.items() if not inner_list]
    return outer_contours, inner_most_contours

# 简化包含关系
simplified_dict = simplify_containment(containment_dict)

# 提取最外层和最内层
outer_contours, inner_most_contours = find_outer_and_inner_after_simplification(simplified_dict)

# 绘图展示
fig2 = plt.figure(figsize=(20, 20))
ax2 = fig2.add_subplot(1, 1, 1, projection=ccrs.NorthPolarStereo(central_longitude=0))
ax2.add_feature(cfeature.COASTLINE)
ax2.set_extent(img_extent, ccrs.PlateCarree())
ax2.gridlines(crs=ccrs.PlateCarree(), draw_labels=True, linewidth=1, color='gray', linestyle='--')

# 绘制最外层等压线（红色）
for outer_idx in outer_contours:
    outer_path = closed_contours[outer_idx]
    ax2.plot(outer_path[:, 0], outer_path[:, 1], transform=ccrs.PlateCarree(),
             color='red', linewidth=2, label=f'Outer {outer_idx}')

# 绘制最内层等压线（绿色）
for inner_idx in inner_most_contours:
    inner_path = closed_contours[inner_idx]
    ax2.plot(inner_path[:, 0], inner_path[:, 1], transform=ccrs.PlateCarree(),
             color='green', linewidth=2, linestyle='--', label=f'Inner {inner_idx}')

plt.show()

