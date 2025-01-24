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

# 定义一个函数来计算闭合等压线的近似半径
def calculate_radius(contour):
    # 计算闭合路径的质心
    center_x = np.mean(contour[:, 0])
    center_y = np.mean(contour[:, 1])

    # 计算每个顶点到质心的距离，并返回平均距离作为近似半径
    distances = np.sqrt((contour[:, 0] - center_x)**2 + (contour[:, 1] - center_y)**2)
    mean_distance = np.mean(distances)
    return mean_distance

# 设置最小半径阈值（单位：纬度/经度角度差，约等于 1° ~= 111 公里）
min_radius_threshold = 0.5  # 可调整阈值

# 筛选半径大于阈值的闭合等压线
filtered_contours = [contour for contour in closed_contours if calculate_radius(contour) >= min_radius_threshold]

# 输出过滤结果
if not filtered_contours:
    print("未找到符合半径要求的闭合等压线")
else:
    print(f"找到 {len(filtered_contours)} 条符合半径要求的闭合等压线")

# 可视化符合要求的闭合等压线
for contour in filtered_contours:
    f1_ax1.plot(contour[:, 0], contour[:, 1], transform=ccrs.PlateCarree(), color='red', linewidth=2)

plt.show()


# 构建包含关系字典
containment_dict = {}  # {outer_index: [inner_indices]}
for i, outer_path in enumerate(filtered_contours):
    outer_polygon = Path(outer_path)
    containment_dict[i] = []  # 初始化列表
    for j, inner_path in enumerate(filtered_contours):
        if i != j:
            if np.all(outer_polygon.contains_points(inner_path)):
                containment_dict[i].append(j)

# 清理包含关系
def simplify_containment(containment_dict, min_radius_threshold=1):
    simplified_dict = containment_dict.copy()

    for parent, children in list(containment_dict.items()):
        # 检查子节点的半径
        child_radii = [calculate_radius(filtered_contours[child]) for child in children]

        # 筛选半径显著的子节点
        significant_children = [
            child for child, radius in zip(children, child_radii) if radius >= min_radius_threshold
        ]

        if len(significant_children) == 1:
            # 只有一个显著子节点：保留该子节点，移除其他子节点
            simplified_dict[parent] = significant_children
        elif len(significant_children) > 1:
            # 多个显著子节点：移除当前`parent`，保留所有显著子节点作为新`parent`
            del simplified_dict[parent]
            for child in significant_children:
                if child not in simplified_dict:
                    simplified_dict[child] = []  # 添加显著子节点为新的`parent`

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
    outer_path = filtered_contours[outer_idx]
    ax2.plot(outer_path[:, 0], outer_path[:, 1], transform=ccrs.PlateCarree(),
             color='red', linewidth=2, label=f'Outer {outer_idx}')

# 绘制最内层等压线（绿色）
for inner_idx in inner_most_contours:
    inner_path = filtered_contours[inner_idx]
    ax2.plot(inner_path[:, 0], inner_path[:, 1], transform=ccrs.PlateCarree(),
             color='green', linewidth=2, linestyle='--', label=f'Inner {inner_idx}')


'''# 绘制闭合等压线
for contour_vertices in closed_contours:
    f1_ax1.plot(contour_vertices[:, 0], contour_vertices[:, 1], transform=ccrs.PlateCarree(), color='red', linewidth=1)
'''
# 添加标签并显示等压线图
plt.clabel(contours, inline=True, fontsize=8, fmt='%1.0f hPa')
plt.title(f'Surface Pressure Contour Lines (Above 1010 hPa, Interval: {interval} hPa)')

plt.show()
'''
# 等压线长度换算函数
def calculate_contour_length_km(contour):
    """将等压线长度换算为公里单位"""
    distances = np.sqrt(np.sum(np.diff(contour, axis=0) ** 2, axis=1))  # 邻点之间的距离 (经纬度)
    length_km = np.sum(distances) * 124  # 换算为公里，1度=124公里
    return length_km

# 等压线等级字典
contour_levels = {i: level for i, level in enumerate(contours.levels)}

# 按气压梯度过滤等压线
def filter_by_pressure_gradient_with_levels(
    outer_contours, inner_contours, filtered_contours, contour_levels, threshold_gradient=0.15
):
    """根据气压梯度剔除不满足条件的等压线"""
    to_remove = []  # 需要移除的等压线对


    # 确保 contoured_levels 是一个有效的列表或字典
    contour_keys = list(contour_levels.keys())

    for outer_idx in outer_contours:
        for inner_idx in inner_contours:
            # 确保索引在 contour_levels 的范围内
            if outer_idx >= len(contour_levels) or inner_idx >= len(contour_levels):
                continue  # 跳过无效的索引

            # 获取外层和内层等压线的气压值
            outer_pressure = contour_levels[outer_idx]
            inner_pressure = contour_levels[inner_idx]

            # 计算气压差值 (hPa)
            pressure_diff = abs(outer_pressure - inner_pressure) * 100
            # 计算等压线长度差值 (km)
            outer_length = calculate_contour_length_km(filtered_contours[outer_idx])
            inner_length = calculate_contour_length_km(filtered_contours[inner_idx])
            length_diff = np.abs(outer_length - inner_length)  # 长度差值 (km)

            # 计算气压梯度
            if length_diff == 0:  # 避免除以零
                continue
            gradient = pressure_diff / length_diff * 2 * math.pi # 气压梯度 (Pa/km)

            # 检查是否满足阈值条件
            if gradient < threshold_gradient:
                to_remove.append((outer_idx, inner_idx))  # 记录需要剔除的等压线对

    # 移除不满足条件的等压线索引
    updated_outer = [idx for idx in outer_contours if idx not in {o for o, _ in to_remove}]
    updated_inner = [idx for idx in inner_contours if idx not in {i for _, i in to_remove}]

    return updated_outer, updated_inner, to_remove

# 执行过滤过程
threshold_gradient = 0.15  # 气压梯度阈值 (Pa/km)
outer_contours, inner_most_contours, removed_pairs = filter_by_pressure_gradient_with_levels(
    outer_contours, inner_most_contours, filtered_contours, contour_levels, threshold_gradient
)

# 绘图更新
fig6 = plt.figure(figsize=(20, 20))
ax6 = fig6.add_subplot(1, 1, 1, projection=ccrs.NorthPolarStereo(central_longitude=0))
ax6.add_feature(cfeature.COASTLINE)
ax6.set_extent(img_extent, ccrs.PlateCarree())
ax6.gridlines(crs=ccrs.PlateCarree(), draw_labels=True, linewidth=1, color='gray', linestyle='--')

# 绘制更新后的最外层等压线（蓝色）
for outer_idx in outer_contours:
    outer_path = filtered_contours[outer_idx]
    ax6.plot(outer_path[:, 0], outer_path[:, 1], transform=ccrs.PlateCarree(),
             color='blue', linewidth=2, label=f'Outer {outer_idx}')

# 绘制更新后的最内层等压线（橙色）
for inner_idx in inner_most_contours:
    inner_path = filtered_contours[inner_idx]
    ax6.plot(inner_path[:, 0], inner_path[:, 1], transform=ccrs.PlateCarree(),
             color='orange', linewidth=2, linestyle='--', label=f'Inner {inner_idx}')

# 添加图例和标题
plt.legend()
plt.title(f"Filtered Contours Based on Pressure Gradient (Threshold: {threshold_gradient} Pa/km)")
plt.show()
'''