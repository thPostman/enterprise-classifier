# 企业名称自动分类系统

这是一个基于FastAPI的企业名称智能分类系统，可以自动提取和分类企业名称中的关键信息，包括行政区划、行业类型、企业类型等。

## 主要特性

- 高性能：优化的批处理和多线程支持，处理1500条记录仅需0.42秒
- 准确性：针对江苏省等地区的县级市进行了特殊优化
- 灵活性：支持单条和批量处理，支持Excel文件导入导出
- 智能匹配：使用预编译正则表达式和LRU缓存提升性能
- 数据处理：支持行政区划、行业分类、企业类型等多维度分析

## 功能特点

- 使用 FastAPI 构建高性能 RESTful API
- 智能的中文分词和文本分类
- 支持批量处理和多线程并发
- 完善的行政区划识别（省、市、区/县）
- 智能的行业分类和企业类型识别
- Excel文件导入导出支持

## 安装说明

1. 克隆仓库：
```bash
git clone https://github.com/thPostman/enterprise-classifier.git
cd enterprise-classifier
```

2. 安装依赖：
```bash
pip install -r requirements.txt
```

3. 运行应用：
```bash
python app.py
```

## 使用说明

### 1. 启动服务
```bash
python app.py
```
服务将在 http://localhost:8000 启动

### 2. API接口

#### 2.1 单个企业名称分类
- 访问 http://localhost:8000/docs
- 使用 `/classify` 接口
- 输入企业名称
- 获取分类结果

示例响应：
```json
{
    "original_name": "江苏昆山科技有限公司",
    "province": "江苏",
    "city": "苏州",
    "district": "昆山",
    "industry_type": "科技",
    "company_type": "有限责任公司",
    "core_name": "昆山科技"
}
```

#### 2.2 批量处理
- 准备包含企业名称列的Excel文件
- 使用 `/batch` 接口上传文件
- 自动下载处理结果

### 3. 性能优化

系统采用多项优化措施提升性能：
- 使用预编译正则表达式
- 实现LRU缓存机制
- 多线程并发处理
- 批量处理优化

### 4. 注意事项

- 确保Excel文件格式正确
- 企业名称应包含完整信息
- 行政区划数据定期更新
- 批量处理时建议合理控制数据量

## 最新更新

- 优化了江苏省县级市的识别准确度
- 提升了批量处理性能
- 增加了多线程支持
- 优化了缓存机制

## 贡献指南

欢迎提交Issue和Pull Request来帮助改进项目。

## 许可证

MIT License
