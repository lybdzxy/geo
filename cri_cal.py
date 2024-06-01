import pandas as pd

# 读取 Excel 文件中的每个 sheet
file_path = 'E:/GEO/etccdi/qpm/model_indices_summary.xlsx'
output_file_path = 'E:/GEO/etccdi/qpm/CRI.xlsx'
sheet_names = ['prcptot', 'r95p', 'r99p', 'r95ptot', 'r99ptot', 'sdii', 'rx1day', 'r10mm', 'r20mm']

with pd.ExcelWriter(output_file_path) as writer:
    for sheet_name in sheet_names:
        # 读取当前 sheet
        df = pd.read_excel(file_path, sheet_name=sheet_name)

        # 只保留需要的列
        df = df[['Model', 'RMSE', 'Correlation', 'Std_Dev_Predicted', 'NSE', 'KGE', 'ModIn']]

        # 排序并替换为排名
        df['RMSE'] = df['RMSE'].rank(ascending=True).astype(int)
        df['Std_Dev_Predicted'] = df['Std_Dev_Predicted'].rank(ascending=True).astype(int)
        df['Correlation'] = df['Correlation'].rank(ascending=False).astype(int)
        df['NSE'] = df['NSE'].rank(ascending=False).astype(int)
        df['KGE'] = df['KGE'].rank(ascending=False).astype(int)
        df['ModIn'] = df['ModIn'].rank(ascending=False).astype(int)

        # 将当前 sheet 保存到新的 Excel 文件中
        df.to_excel(writer, sheet_name=sheet_name, index=False)
