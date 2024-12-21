import pandas as pd
import json
import os
from typing import Dict, List
from pypinyin import lazy_pinyin

def load_excel_data(file_path: str) -> pd.DataFrame:
    """
    从Excel文件加载行政区划数据
    Excel文件格式应该包含以下列：
    - 省份
    - 地市
    - 区县
    """
    return pd.read_excel(file_path)

def process_regions_data(df: pd.DataFrame) -> Dict:
    """
    处理行政区划数据，生成层级结构
    """
    regions_dict = {}
    
    # 遍历数据框
    for _, row in df.iterrows():
        province = row['省份']
        city = row['地市']
        district = row['区县']
        
        # 创建省份层级
        if province not in regions_dict:
            regions_dict[province] = {}
        
        # 创建地市层级
        if city not in regions_dict[province]:
            regions_dict[province][city] = {}
        
        # 添加区县信息
        regions_dict[province][city][district] = {
            "province": province,
            "city": city
        }
    
    return regions_dict

def save_regions_data(regions_dict: Dict, output_file: str):
    """
    保存处理后的数据到Python模块
    """
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("# 中国行政区划数据\n\n")
        f.write("REGIONS = ")
        f.write(json.dumps(regions_dict, ensure_ascii=False, indent=4))

def main():
    """
    主函数：处理Excel文件并生成Python模块
    """
    # 获取脚本所在目录
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_dir = os.path.dirname(script_dir)
    
    # 构建输入和输出文件的完整路径
    excel_file = os.path.join(project_dir, "data", "regions.xlsx")
    output_file = os.path.join(project_dir, "data", "administrative_regions.py")
    
    # 检查输入文件是否存在
    if not os.path.exists(excel_file):
        print(f"请先准备行政区划Excel文件：{excel_file}")
        return
    
    # 加载和处理数据
    df = load_excel_data(excel_file)
    regions_dict = process_regions_data(df)
    
    # 保存处理后的数据
    save_regions_data(regions_dict, output_file)
    print(f"行政区划数据已更新：{output_file}")

if __name__ == "__main__":
    main()
