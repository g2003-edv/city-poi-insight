# 城市 POI 数据洞察 — 时空数据分析与商圈聚类

> **技能关键词**：时空数据分析 · 地理信息可视化 · 热力图 · OD 矩阵 · DBSCAN 密度聚类 · 数据清洗 · 异常值过滤 · Pandas · GeoPandas · Folium · Matplotlib · Scikit-learn · Jinja2

## 项目概述

基于出租车 GPS 轨迹数据与 POI（兴趣点）数据，构建城市空间分析 pipeline，输出热力分布、OD 出行矩阵、商圈聚类及可视化洞察报告，为城市交通规划与商业选址提供数据支持。

**核心能力覆盖**：
- 大规模 GPS 轨迹数据清洗与异常值过滤（经纬度范围校验、缺失值处理）
- 空间热力图生成（Folium 交互式 + Matplotlib 静态双引擎）
- OD 出行矩阵构建（网格化区域划分、流量统计、Seaborn 热力图可视化）
- POI 密度聚类分析（DBSCAN 算法自动识别高密度商圈）
- 自动化 HTML 洞察报告生成（Jinja2 模板 + 核心指标卡片 + 图表嵌入）

## 技术栈

`Python` · `Pandas` · `GeoPandas` · `Scikit-learn` · `Folium` · `Matplotlib` · `Seaborn` · `Jinja2`

## 核心功能

| 模块 | 输出 | 技能实践 |
|------|------|---------|
| 数据清洗 | `data/` | 读取 CSV/SHP 多源数据，过滤异常经纬度，统一字段格式 |
| 热力图 | `pickup_heatmap.html` + `.png` | Folium 交互热力图 + Matplotlib 2D 密度直方图 |
| OD 矩阵 | `od_matrix_heatmap.png` | 0.05° 网格分区，Top 15 热门区域流量矩阵 |
| 商圈聚类 | `poi_clustering.png` | DBSCAN 密度聚类（eps=0.01°, min_samples=5）|
| 洞察报告 | `insight_report.html` | Jinja2 模板渲染，含核心指标、图表、方法论 |

## 数据规模

- **出租车订单**：~15,000 条 GPS 轨迹记录
- **POI 点位**：餐饮 / 医院 / 学校 / 影院 / 公交 / 火锅 6 大类别
- **识别商圈**：141 个高密度聚类区域

## 快速开始

```bash
pip install -r requirements.txt
python main.py
```

输出文件位于 `output/` 目录。

## 分析方法论

1. **数据清洗**：去除经纬度异常值，过滤市域范围外数据
2. **热力图**：双引擎渲染（Folium 交互式 + Matplotlib 静态）
3. **OD 矩阵**：按 0.05° 网格划分区域，统计区域间出行流量
4. **聚类算法**：DBSCAN 密度聚类，自动识别高密度商圈，过滤噪声点

## 数据来源

- 出租车 GPS 轨迹数据（公开样本）
- 城市 POI 数据（餐饮、医院、学校、影院等公开数据集）
