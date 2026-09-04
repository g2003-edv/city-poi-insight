# 城市POI数据洞察

用出租车GPS轨迹数据和POI数据做的一个空间分析小项目，输出热力图、OD矩阵和商圈聚类结果。

## 项目概述

基于上海的出租车GPS订单数据和POI点位数据，做一个完整的数据分析pipeline，包括数据清洗、可视化、聚类和报告生成。

## 技术栈

Python、Pandas、GeoPandas、Scikit-learn、Folium、Matplotlib、Seaborn、Jinja2

## 核心功能

| 模块 | 输出 |
|------|------|
| 数据清洗 | 过滤异常经纬度，统一字段格式 |
| 热力图 | Folium交互热力图 + Matplotlib静态图 |
| OD矩阵 | 0.05°网格分区，Top15热门区域流量矩阵 |
| 商圈聚类 | DBSCAN密度聚类 |
| 洞察报告 | Jinja2模板生成的HTML报告 |

## 数据规模

- 出租车订单：约15,000条GPS轨迹
- POI点位：餐饮、医院、学校、影院、公交、火锅6类
- 识别商圈：141个高密度聚类区域

## 踩坑记录

- **坐标系问题**：GPS数据是WGS84坐标，POI数据有的是GCJ-02（火星坐标），一开始直接叠加有偏差，后来用GeoPandas做了坐标转换。
- **DBSCAN参数调优**：eps一开始设了0.005，聚出来太多细碎的小簇；改成0.01后才比较合理。min_samples从3调到5，过滤了一些噪声点。
- **Folium性能**：POI点太多的时候Folium生成的HTML文件特别大，浏览器打开卡。后来做了采样，只显示前5000个点。
- **OD矩阵可视化**：Seaborn的热力图颜色映射一开始选的不对，流量差异不明显。换了viridis colormap并做了log变换后才清晰。
- **Jinja2中文乱码**：模板渲染的时候中文字符乱码，后来发现是模板文件没存UTF-8，加上<meta charset="utf-8">后解决。

## 快速开始

```bash
pip install -r requirements.txt
python main.py
```

输出文件在 `output/` 目录。

## 数据来源

- 出租车GPS轨迹数据（公开样本）
- 城市POI数据（公开数据集）

## License

MIT
