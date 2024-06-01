import xarray as xr

merged = None  # 将 merged 初始化为 None

for year in range(1961, 2023):
    data = xr.open_dataset(f'E:/GEO/eof/prcptot/prcptot{year}.nc')

    if merged is None:
        merged = data  # 如果 merged 为 None，直接将当前年份的数据赋值给 merged
    else:
        merged = xr.concat([merged, data], dim="time")  # 否则，使用 xr.concat 连接数据
merged = merged.rename({'latitude': 'lat', 'longitude': 'lon'})
print(merged)
merged.to_netcdf('E:/GEO/eof/CHM_PRE_PRCPTOT.nc')
