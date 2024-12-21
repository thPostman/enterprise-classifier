import requests
import json
import os
import pandas as pd

def fetch_github_data():
    """
    从GitHub获取最新的中国行政区划数据
    """
    # 获取省级数据
    provinces_url = "https://raw.githubusercontent.com/modood/Administrative-divisions-of-China/master/dist/provinces.json"
    cities_url = "https://raw.githubusercontent.com/modood/Administrative-divisions-of-China/master/dist/cities.json"
    areas_url = "https://raw.githubusercontent.com/modood/Administrative-divisions-of-China/master/dist/areas.json"
    
    try:
        provinces = requests.get(provinces_url).json()
        cities = requests.get(cities_url).json()
        areas = requests.get(areas_url).json()
        
        # 构建数据结构
        data = []
        
        # 创建城市和区县的查找字典
        city_dict = {city['code']: city for city in cities}
        province_dict = {province['code']: province for province in provinces}
        
        # 处理每个区县
        for area in areas:
            city_code = area['cityCode']
            city = city_dict.get(city_code, {})
            province_code = city.get('provinceCode', '')
            province = province_dict.get(province_code, {})
            
            if province and city:
                data.append([
                    province['name'],
                    city['name'],
                    area['name']
                ])
        
        # 创建DataFrame
        df = pd.DataFrame(data, columns=['省份', '地市', '区县'])
        
        # 获取脚本所在目录
        script_dir = os.path.dirname(os.path.abspath(__file__))
        project_dir = os.path.dirname(script_dir)
        excel_file = os.path.join(project_dir, "data", "regions.xlsx")
        
        # 保存为Excel文件
        df.to_excel(excel_file, index=False, engine='openpyxl')
        print(f"已从GitHub获取最新数据并保存到：{excel_file}")
        print(f"共获取到 {len(provinces)} 个省级行政区、{len(cities)} 个地级市、{len(areas)} 个区县")
        
    except Exception as e:
        print(f"获取数据时出错：{str(e)}")
        return None

if __name__ == "__main__":
    fetch_github_data()
