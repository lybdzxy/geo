import cdsapi
from subprocess import call


def idmDownloader(task_url, folder_path, file_name):
    """
    IDM下载器
    :param task_url: 下载任务地址
    :param folder_path: 存放文件夹
    :param file_name: 文件名
    :return:
    """
    # IDM安装目录
    idm_engine = r"C:\Program Files (x86)\Internet Download Manager\IDMan.exe"
    # 将任务添加至队列
    call([idm_engine, '/d', task_url, '/p', folder_path, '/f', file_name, '/a'])
    # 开始任务队列
    call([idm_engine, '/s'])


if __name__ == '__main__':
    c = cdsapi.Client()  # 创建用户

    # 数据信息字典
    dic = {
        'product_type': 'reanalysis',  # 产品类型
        'format': 'netcdf',  # 数据格式
        'variable': 'total_precipitation',  # 变量名称
        'year': '',  # 年，设为空
        'month': [# 月
            '01'
        ],
        'day': [# 日
            '01'
        ],
        'time': '00:00'
    }

    for y in range(2023,2024):  # 遍历年
        dic['year'] = str(y)

        r = c.retrieve('reanalysis-era5-land', dic, )  # 文件下载器
        url = r.location  # 获取文件下载地址
        path = r'E:\testidm'  # 存放文件夹
        filename = str(y) + '.nc'  # 文件名
        idmDownloader(url, path, filename)  # 添加进IDM中下载