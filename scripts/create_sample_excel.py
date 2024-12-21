import pandas as pd

# 创建示例数据
sample_companies = [
    "北京市海淀区中关村科技创新有限公司",
    "上海市浦东新区陆家嘴金融贸易有限公司",
    "广东省深圳市南山区腾讯科技有限公司",
    "浙江省杭州市西湖区阿里巴巴网络技术有限公司",
    "四川省成都市武侯区天府软件科技有限公司",
    "山东省青岛市崂山区海洋生物科技有限公司",
    "江苏省南京市鼓楼区东南大学科技园创新有限公司",
    "湖北省武汉市洪山区光谷生物医药有限公司",
    "陕西省西安市雁塔区西安交大科技创新有限公司",
    "重庆市渝中区两江新区金融服务有限公司"
]

# 创建DataFrame
df = pd.DataFrame({"企业名称": sample_companies})

# 保存为Excel文件
df.to_excel("data/sample_companies.xlsx", index=False, engine='openpyxl')
print("示例Excel文件已创建：data/sample_companies.xlsx")
