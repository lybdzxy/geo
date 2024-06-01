import pandas as pd
import xarray as xr

# 读取 Excel 文件中的数据存储到字典中
w_path = 'E:/GEO/etccdi/qpm/CRI - 副本.xlsx'
indices = ['prcptot', 'r95p', 'r99p', 'r95ptot', 'r99ptot', 'sdii', 'rx1day', 'r10mm', 'r20mm']
index_data = {}
wi = {}

for index in indices:
    df = pd.read_excel(w_path, sheet_name=index)
    index_data[index] = df
    wi[index] = index_data[index]['Wi'].values

models = ['BCC-CSM2-MR','CMCC-CM2-SR5','CMCC-ESM2',
            'EC-Earth3','EC-Earth3-Veg','GFDL-ESM4',
            'INM-CM4-8','INM-CM5-0','MPI-ESM1-2-HR',
            'MRI-ESM2-0','NorESM2-MM','TaiESM1']
ssps = ['126', '245', '370', '585']

for index in indices:
    for ssp in ssps:
        for year in range(2015, 2069):
            mme = None  # Initialize mme
            for mod in models:
                data_path = f'E:/GEO/etccdi/qpm/{index}_{mod}_{ssp}_{year}.nc'
                data = xr.open_dataset(data_path)
                wighted_data = data['__xarray_dataarray_variable__'] * wi[index][models.index(mod)]  # Corrected indexing
                if mme is None:
                    mme = wighted_data.copy()  # Make sure to copy the data to avoid reference issues
                else:
                    mme += wighted_data  # Accumulate the weighted data
            output_path = f'E:/GEO/etccdi/qpm/mme/new/{index}_{ssp}_{year}.nc'
            mme.to_netcdf(output_path)  # Corrected method name
