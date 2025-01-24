import xarray as xr
import matplotlib.pyplot as plt
import numpy as np
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import scipy.ndimage as ndimage
import scipy.interpolate as interpolate

# 读取上传的 netCDF 文件
file_path = 'E:/GEO/test/test_1.nc'
data = xr.open_dataset(file_path)

# 获取经度、纬度和地表气压数据
lon = data['longitude'].values
lat = data['latitude'].values
pressure = data['sp'].values.squeeze() / 100  # 转换为百帕 (hPa) 以符合常见单位
# 只选择气压值大于950 hPa的区域
pressure_above_1010 = np.where(pressure >= 1010, pressure, np.nan)
# 动态调整等压线间隔的函数
def dynamic_interval(pressure_data, base_interval=5):
    density = np.count_nonzero(~np.isnan(pressure_data)) / pressure_data.size
    if density > 0.5:  # 如果等压线非常密集，扩大间隔
        return base_interval * 2
    elif density > 0.7:  # 更密集时，进一步扩大间隔
        return base_interval * 3
    return base_interval

# 根据等压线密集程度选择间隔
interval = dynamic_interval(pressure_above_1010)
proj =ccrs.LambertAzimuthalEqualArea(central_longitude=0, central_latitude=90)
leftlon, rightlon, lowerlat, upperlat = (-180,180,0,90)#经纬度范围
img_extent = [leftlon, rightlon, lowerlat, upperlat]

# 绘制等压线图
fig1 = plt.figure(figsize=(12, 10))
f1_ax1 = fig1.add_axes([0.2, 0.3, 0.5, 0.5],projection = ccrs.NorthPolarStereo(central_longitude=0))#绘制地图位置
f1_ax1.gridlines(crs=ccrs.PlateCarree(), draw_labels=True,
                  linewidth=1, color='grey',linestyle='--')
f1_ax1.add_feature(cfeature.COASTLINE)
f1_ax1.set_extent(img_extent, ccrs.PlateCarree())

contour = plt.contour(lon, lat, pressure_above_1010, levels=np.arange(1010, pressure.max(), interval), transform=ccrs.PlateCarree(), cmap='jet')
plt.clabel(contour, inline=True, fontsize=8, fmt='%1.0f hPa')
plt.title(f'Surface Pressure Contour Lines (Above 1010 hPa, Interval: {interval} hPa)')
plt.colorbar(contour, ax=f1_ax1, orientation='vertical', label='Pressure (hPa)')

plt.show()

