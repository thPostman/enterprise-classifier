from fastapi import FastAPI, File, Form, UploadFile, HTTPException
from fastapi.responses import FileResponse
import jieba
from typing import Dict, List, Optional
from data.administrative_regions import REGIONS
from data.business_types import COMPANY_TYPES
from data.industry_categories import get_industry_info
import pandas as pd
import os
from datetime import datetime

app = FastAPI(title="企业名称分类系统")

def find_region(company_name: str) -> Dict[str, str]:
    """查找并匹配行政区划信息"""
    result = {"province": "", "city": "", "district": ""}
    
    # 直辖市列表
    municipalities = ["北京", "上海", "天津", "重庆"]
    
    # 特殊区县名称，需要更严格的匹配规则
    special_districts = {
        "市中": ["济宁", "内江", "乐山", "枣庄", "泸州"],
        "城中": ["柳州", "玉林", "百色"],
        "市北": ["青岛"],
        "市南": ["青岛"],
        "明山": ["本溪"]
    }
    
    def is_valid_region_combination(province: str, city: str, district: str) -> bool:
        """检查省市区组合是否有效"""
        if not province and (city or district):
            return False
        if not city and district:
            return False
            
        if city and province:
            # 检查城市是否属于该省份
            for p, cities in REGIONS.items():
                if province in p:
                    if not any(city in c for c in cities.keys()):
                        return False
                    
        if district and city:
            # 检查区县是否属于该城市
            for p, cities in REGIONS.items():
                for c, districts in cities.items():
                    if city in c:
                        if district in special_districts:
                            return city in special_districts[district]
                        return any(district in d for d in districts)
        return True
    
    def find_regions_in_text(text: str, start_pos: int = 0) -> Dict[str, str]:
        """在文本中查找行政区划，可以指定起始位置"""
        temp_result = {"province": "", "city": "", "district": ""}
        
        # 获取省份和地市的最大字数
        max_province_len = max(len(p.replace("省", "").replace("自治区", "")) for p in REGIONS.keys())
        max_city_len = max(len(c.replace("市", "").replace("地区", "")) 
                          for cities in REGIONS.values() 
                          for c in cities.keys())
        max_district_len = max(len(d.replace("区", "").replace("县", "").replace("市", ""))
                             for cities in REGIONS.values()
                             for districts in cities.values()
                             for d in districts)
        max_region_len = max(max_province_len, max_city_len, max_district_len)
        
        # 在指定范围内查找省份和地市
        search_text = text[start_pos:start_pos + max_region_len * 2]  # 扩大搜索范围
        
        # 1. 先处理直辖市
        for mun in municipalities:
            if mun in search_text:
                temp_result["province"] = mun
                temp_result["city"] = mun
                return temp_result
        
        # 2. 处理普通省份
        for province, cities in REGIONS.items():
            province_name = province.replace("市", "").replace("省", "").replace("自治区", "")
            if province_name in search_text:
                temp_result["province"] = province_name
                
                # 在省份名称后查找城市和县级市
                remaining_text = text[text.find(province_name) + len(province_name):]
                
                # 先尝试匹配地级市
                for city in cities:
                    city_name = city.replace("市", "").replace("地区", "")
                    if len(city_name) >= 2 and city_name in remaining_text:
                        # 检查是否是有效的省市组合
                        if is_valid_region_combination(temp_result["province"], city_name, ""):
                            temp_result["city"] = city_name
                            break
                
                # 如果没找到地级市，尝试匹配县级市
                if not temp_result["city"]:
                    for city, districts in cities.items():
                        for district in districts:
                            if district.endswith("市"):  # 县级市
                                district_name = district.replace("市", "")
                                if len(district_name) >= 2 and district_name in remaining_text:
                                    temp_result["city"] = city.replace("市", "").replace("地区", "")
                                    temp_result["district"] = district_name
                                    return temp_result
                break
        
        # 如果在指定范围内没找到省份，尝试直接匹配城市和县级市
        if not temp_result["province"]:
            # 先匹配地级市
            for province, cities in REGIONS.items():
                for city in cities:
                    city_name = city.replace("市", "").replace("地区", "")
                    if len(city_name) >= 2 and city_name in search_text:
                        temp_result["city"] = city_name
                        temp_result["province"] = province.replace("市", "").replace("省", "").replace("自治区", "")
                        break
                if temp_result["city"]:
                    break
            
            # 如果没找到地级市，尝试匹配县级市
            if not temp_result["city"]:
                for province, cities in REGIONS.items():
                    for city, districts in cities.items():
                        for district in districts:
                            if district.endswith("市"):  # 县级市
                                district_name = district.replace("市", "")
                                if len(district_name) >= 2 and district_name in search_text:
                                    temp_result["province"] = province.replace("市", "").replace("省", "").replace("自治区", "")
                                    temp_result["city"] = city.replace("市", "").replace("地区", "")
                                    temp_result["district"] = district_name
                                    return temp_result
        
        # 3. 如果找到了城市，尝试匹配对应的区县
        if temp_result["city"]:
            for province, cities in REGIONS.items():
                if temp_result["province"] in province:
                    for city, districts in cities.items():
                        if temp_result["city"] in city:
                            for district in districts:
                                district_name = district.replace("区", "").replace("县", "").replace("市", "")
                                if len(district_name) >= 2 and district_name in search_text:
                                    # 检查是否是有效的省市区组合
                                    if is_valid_region_combination(temp_result["province"],
                                                                temp_result["city"],
                                                                district_name):
                                        temp_result["district"] = district_name
                                        break
                            break
                    break
        
        return temp_result
    
    # 处理分公司情况
    if "分公司" in company_name:
        # 找到分公司位置
        branch_pos = company_name.find("分公司")
        # 先尝试匹配分公司前面最近的部分（从分公司位置往前10个字符）
        start_pos = max(0, branch_pos - 10)
        result = find_regions_in_text(company_name[start_pos:branch_pos])
        if result["province"] or result["city"]:
            return result
        # 如果在分公司前找不到，再匹配整个名称
        return find_regions_in_text(company_name)
    
    # 检查括号中的地名
    import re
    brackets_pattern = r'[（(][^）)]*[）)]'
    brackets_content = re.findall(brackets_pattern, company_name)
    
    # 处理括号中的地名
    for bracket in brackets_content:
        result = find_regions_in_text(bracket)
        if result["province"] or result["city"]:
            return result
    
    # 其他情况，从左往右匹配整个名称
    return find_regions_in_text(company_name)

def find_industry_type(company_name: str) -> Dict[str, List[str]]:
    """查找并匹配行业类别"""
    industry_info = get_industry_info(company_name)
    return {
        'categories': industry_info['category'],
        'types': industry_info['types']
    }

def find_company_type(company_name: str) -> Optional[str]:
    """识别公司类型"""
    for company_type, keywords in COMPANY_TYPES.items():
        for keyword in keywords:
            if keyword in company_name:
                return company_type
    return None

def extract_company_name(company_name: str, region_result: dict, industry_types: List[str], company_type: str) -> str:
    """提取企业名称（去除行政区划、行业类别和公司类别）"""
    name = company_name
    
    # 需要去除的行业相关词汇
    industry_words = ["科技", "网络", "文化", "传媒", "信息", "技术", "软件", "互联网", "电子", "数字", 
                     "通信", "教育", "咨询", "服务", "工程", "贸易", "商务", "投资", "管理"]
    
    # 处理括号中的内容
    import re
    brackets_pattern = r'[（(][^）)]*[）)]'
    brackets_content = re.findall(brackets_pattern, name)
    
    # 移除括号中的地名和行业词
    for bracket in brackets_content:
        should_remove = False
        if region_result:
            for region in [region_result.get('province', ''), region_result.get('city', ''), region_result.get('district', '')]:
                if region and region in bracket:
                    should_remove = True
                    break
        for word in industry_words:
            if word in bracket:
                should_remove = True
                break
        if should_remove:
            name = name.replace(bracket, '')
    
    # 移除行政区划
    if region_result:
        # 先移除完整的行政区划名称（包含单位）
        for region in [region_result.get('province', ''), region_result.get('city', ''), region_result.get('district', '')]:
            if region:
                name = name.replace(region + "市", '')
                name = name.replace(region + "省", '')
                name = name.replace(region + "区", '')
                name = name.replace(region + "县", '')
                # 再移除没有单位的地名
                name = name.replace(region, '')
        
        # 处理可能残留的单独的行政区划单位
        name = re.sub(r'^(市|区|县|省)', '', name)  # 移除开头的单位
        name = re.sub(r'(市|区|县|省)(?=[^市区县省]|$)', '', name)  # 移除不属于其他地名的单位
    
    # 移除公司类别
    if company_type:
        name = name.replace(company_type, '')
    
    # 使用jieba分词优化行业词移除
    words = list(jieba.cut(name))
    filtered_words = []
    for word in words:
        # 跳过行业相关词汇，但只处理词尾
        if word in industry_words and len(filtered_words) > 0:
            continue
        filtered_words.append(word)
    name = ''.join(filtered_words)
    
    # 清理多余的标点和空格
    name = re.sub(r'[（(][^）)]*[）)]', '', name)  # 移除所有括号内容
    name = name.replace('（', '').replace('）', '')
    name = name.replace('(', '').replace(')', '')
    name = name.strip('、').strip()
    
    # 确保提取的名称至少保留两个字
    if len(name) < 2:
        # 如果处理后太短，尝试使用jieba分词获取第一个有意义的词组
        words = list(jieba.cut(company_name))
        for word in words:
            if len(word) >= 2 and word not in industry_words:
                name = word
                break
        if len(name) < 2:  # 如果还是没找到合适的词，使用原名称的前两个字
            name = company_name[:2]
    
    return name

@app.post("/classify/")
async def classify_company(company_name: str = Form(...)):
    """企业名称分类接口"""
    # 识别行政区划
    region_result = find_region(company_name)
    
    # 识别行业类型
    industry_info = find_industry_type(company_name)
    
    # 识别公司类型
    company_type = find_company_type(company_name)
    
    # 提取企业名称
    enterprise_name = extract_company_name(company_name, region_result, industry_info['types'], company_type)
    
    # 返回分类结果
    return {
        "company_name": company_name,
        "enterprise_name": enterprise_name,
        "administrative_region": region_result,
        "industry_types": industry_info['types'],
        "industry_categories": industry_info['categories'],
        "company_type": company_type
    }

@app.post("/batch_classify/")
async def batch_classify(file: UploadFile = File(...)) -> FileResponse:
    """批量处理企业名称分类"""
    # 创建临时文件来保存上传的内容
    temp_input = "data/temp_input.csv"
    with open(temp_input, "wb") as buffer:
        content = await file.read()
        buffer.write(content)
    
    # 读取文件（支持CSV和Excel）
    try:
        if file.filename.endswith('.csv'):
            df = pd.read_csv(temp_input)
        else:
            df = pd.read_excel(temp_input, engine='openpyxl')
    except Exception as e:
        if os.path.exists(temp_input):
            os.remove(temp_input)
        raise HTTPException(status_code=400, detail=f"无法读取文件: {str(e)}")
    
    if '企业名称' not in df.columns:
        if os.path.exists(temp_input):
            os.remove(temp_input)
        raise HTTPException(status_code=400, detail="文件必须包含'企业名称'列")
    
    # 处理每一行数据
    results = []
    for company_name in df['企业名称']:
        # 调用单个企业的处理函数
        region_result = find_region(company_name)
        industry_info = find_industry_type(company_name)
        company_type = find_company_type(company_name)
        enterprise_name = extract_company_name(company_name, region_result, industry_info['types'], company_type)
        
        results.append({
            '企业名称': company_name,
            '企业简称': enterprise_name,
            '省份': region_result.get('province', ''),
            '地市': region_result.get('city', ''),
            '区县': region_result.get('district', ''),
            '行业大类': '、'.join(industry_info['categories']) if industry_info['categories'] else '',
            '行业类别': '、'.join(industry_info['types']) if industry_info['types'] else '',
            '公司类别': company_type if company_type else ''
        })
    
    # 创建结果DataFrame
    result_df = pd.DataFrame(results)
    
    # 生成输出文件
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_filename = f"企业分类结果_{timestamp}.xlsx"
    output_path = os.path.join("data", output_filename)
    
    # 确保输出目录存在
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    # 保存结果
    result_df.to_excel(output_path, index=False, engine='openpyxl')
    
    # 清理临时文件
    if os.path.exists(temp_input):
        os.remove(temp_input)
    
    # 返回文件
    return FileResponse(
        path=output_path,
        filename=output_filename,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

@app.get("/")
async def root():
    return {
        "message": "欢迎使用企业名称分类系统",
        "version": "2.0",
        "features": [
            "行政区划识别（省/市/区）",
            "行业类型识别",
            "公司类型识别",
            "批量处理企业名称"
        ]
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
