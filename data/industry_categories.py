# 行业大类定义
INDUSTRY_CATEGORIES = {
    "信息科技": {
        "keywords": ["信息", "科技", "网络", "互联网", "软件", "数字", "智能", "人工智能", "大数据", "技术"],
        "subcategories": [
            "信息科技",
            "网络科技",
            "互联网科技",
            "软件科技",
            "数字科技",
            "智能科技",
            "网络技术",
            "信息技术",
            "网络信息",
            "科技创新",
            "科技服务",
            "人工智能",
            "大数据",
            "技术服务",
            "技术开发",
        ],
        "priority": 0  # 最低优先级
    },
    "文化教育": {
        "keywords": ["文化", "传媒", "教育", "艺术", "出版", "影视", "娱乐", "培训", "教学", "学校", "补习", "辅导"],
        "subcategories": [
            "文化传媒",
            "教育文化",
            "文化艺术",
            "文化创意",
            "出版传媒",
            "影视文化",
            "文化娱乐",
            "教育科技",
            "教育培训",
            "艺术培训",
            "教育咨询",
            "学校教育",
            "课外辅导",
            "素质教育",
            "职业教育",
        ],
        "priority": 2  # 最高优先级
    },
    "电子商务": {
        "keywords": ["电商", "电子商务", "贸易", "商贸", "零售", "批发", "商业", "购物", "商城"],
        "subcategories": [
            "电子商务",
            "网络贸易",
            "跨境电商",
            "电商平台",
            "网络零售",
            "网络批发",
            "商贸服务",
            "网上商城",
            "购物平台",
            "跨境贸易",
        ],
        "priority": 2  # 最高优先级
    }
}

def get_industry_info(company_name: str) -> dict:
    """
    根据企业名称获取行业信息
    返回：{
        'category': '行业大类',
        'types': ['具体行业类别', ...]
    }
    """
    result = {
        'category': [],
        'types': []
    }
    
    # 记录每个匹配的行业大类及其优先级
    matched_categories = []
    
    # 遍历每个行业大类
    for category, info in INDUSTRY_CATEGORIES.items():
        # 检查关键词
        if any(keyword in company_name for keyword in info['keywords']):
            matched_categories.append({
                'category': category,
                'priority': info.get('priority', 0)
            })
        
        # 检查具体类别
        for subtype in info['subcategories']:
            if subtype in company_name:
                result['types'].append(subtype)
    
    # 根据优先级排序匹配的行业大类
    matched_categories.sort(key=lambda x: (-x['priority'], x['category']))
    
    # 如果只有一个匹配的行业大类，直接使用
    if len(matched_categories) == 1:
        result['category'].append(matched_categories[0]['category'])
    # 如果有多个匹配的行业大类
    elif len(matched_categories) > 1:
        # 检查是否有非科技类
        non_tech_categories = [m for m in matched_categories if m['category'] != "信息科技"]
        if non_tech_categories:
            # 如果有非科技类，优先使用非科技类
            result['category'].extend(c['category'] for c in non_tech_categories)
        else:
            # 如果只有科技类，则使用科技类
            result['category'].append("信息科技")
    
    return result
