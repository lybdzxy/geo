import xarray as xr

dg_path = f'E:/GEO/result/ecm/126r95p_lom_GEV.nc'
db_path = f'E:/GEO/result/ecm/126r95p_mktest.nc'

dg = xr.open_dataset(dg_path)
db = xr.open_dataset(db_path)
print(dg)
print(db)