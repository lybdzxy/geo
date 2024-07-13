import pandas as pd

# 读取Excel文件
try:
    results_df = pd.read_excel('E:/GEO/etccdi/qpm/model_indices_results_new.xlsx')
except Exception as e:
    print(f"读取Excel文件时出错: {e}")
    exit()

# 创建一个Excel写入对象
try:
    with pd.ExcelWriter('E:/GEO/etccdi/qpm/model_indices_summary_new.xlsx', engine='openpyxl') as writer:
        # 按照不同指标分组
        for index, group in results_df.groupby('Index'):
            # 保留 'Model' 列，同时选择数值列
            numeric_cols = group.select_dtypes(include='number').columns
            necessary_cols = ['Model'] + list(numeric_cols)
            numeric_group = group[necessary_cols]
            # 按照 'Model' 计算均值
            model_means = numeric_group.groupby('Model').mean().reset_index()
            # 写入均值数据到当前工作表
            model_means.to_excel(writer, sheet_name=index, index=False)
    print("保存完成。")
except Exception as e:
    print(f"写入Excel文件时出错: {e}")