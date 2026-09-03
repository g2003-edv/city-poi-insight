# 城市 POI 数据洞察

基于上海出租车 GPS 轨迹与 POI 数据的多维度空间分析项目。

## 项目概述

本项目通过对上海市出租车订单数据与 POI（兴趣点）数据进行融合分析，输出热力分布、OD 出行矩阵、商圈聚类及可视化洞察报告，为城市交通规划与商业选址提供数据支持。

## 核心功能

| 模块 | 输出 | 说明 |
|------|------|------|
| 热力图 | `pickup_heatmap.html` + `.png` | 出租车上下车点空间密度分布 |
| OD 矩阵 | `od_matrix_heatmap.png` | 区域间出行流量矩阵 |
| 商圈聚类 | `poi_clustering.png` | 基于 DBSCAN 的 POI 密度聚类 |
| 洞察报告 | `insight_report.html` | 带图表的完整分析报告 |

## 快速开始

```bash
pip install -r requirements.txt
python main.py
```

输出文件位于 `output/` 目录。

## 技术栈

Python | Pandas | GeoPandas | Scikit-learn | Folium | Matplotlib | Seaborn | Jinja2

## 数据来源

- 上海出租车 GPS 轨迹数据（样本）
- 上海 POI 数据（餐饮、医院、学校、影院等）
