"""HTML 报告生成模块"""
import os

import numpy as np
import pandas as pd
from jinja2 import Template

OUTPUT_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'output')

EARTH_RADIUS_KM = 6371.0088


def haversine_km(lng1, lat1, lng2, lat2):
    """用 haversine 公式计算两点间大圆距离（km），支持 numpy 数组。"""
    lng1, lat1, lng2, lat2 = map(np.radians, (lng1, lat1, lng2, lat2))
    dlng = lng2 - lng1
    dlat = lat2 - lat1
    a = np.sin(dlat / 2.0) ** 2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlng / 2.0) ** 2
    return 2.0 * EARTH_RADIUS_KM * np.arcsin(np.sqrt(np.clip(a, 0.0, 1.0)))

REPORT_TEMPLATE = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <title>城市 POI 数据洞察报告</title>
    <style>
        body { font-family: 'Segoe UI', 'Microsoft YaHei', sans-serif; max-width: 1200px; margin: 0 auto; padding: 30px; background: #f5f7fa; }
        .header { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 40px; border-radius: 12px; margin-bottom: 30px; }
        .header h1 { margin: 0; font-size: 32px; }
        .header p { margin: 10px 0 0; opacity: 0.9; }
        .section { background: white; padding: 30px; border-radius: 12px; margin-bottom: 20px; box-shadow: 0 2px 8px rgba(0,0,0,0.06); }
        .section h2 { color: #333; border-left: 4px solid #667eea; padding-left: 15px; margin-top: 0; }
        .metric-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin: 20px 0; }
        .metric-card { background: #f8f9fa; padding: 20px; border-radius: 8px; text-align: center; }
        .metric-value { font-size: 28px; font-weight: bold; color: #667eea; }
        .metric-label { color: #666; margin-top: 5px; }
        .chart { text-align: center; margin: 20px 0; }
        .chart img { max-width: 100%; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); }
        .insight { background: #e8f4fd; border-left: 4px solid #2196F3; padding: 15px 20px; margin: 15px 0; border-radius: 0 8px 8px 0; }
        .insight h4 { margin-top: 0; color: #1976D2; }
        table { width: 100%; border-collapse: collapse; margin: 15px 0; }
        th, td { padding: 12px; text-align: left; border-bottom: 1px solid #eee; }
        th { background: #f5f7fa; font-weight: 600; }
    </style>
</head>
<body>
    <div class="header">
        <h1>城市 POI 数据洞察报告</h1>
        <p>出租车轨迹为深圳数据，POI 与行政边界为上海数据，两者独立分析 | 生成时间: {{ timestamp }}</p>
    </div>
    
    <div class="section">
        <h2>核心指标概览</h2>
        <div class="metric-grid">
            <div class="metric-card">
                <div class="metric-value">{{ total_orders }}</div>
                <div class="metric-label">分析订单总量</div>
            </div>
            <div class="metric-card">
                <div class="metric-value">{{ poi_count }}</div>
                <div class="metric-label">POI 点位数量</div>
            </div>
            <div class="metric-card">
                <div class="metric-value">{{ cluster_count }}</div>
                <div class="metric-label">识别商圈数量</div>
            </div>
            <div class="metric-card">
                <div class="metric-value">{{ avg_distance }}</div>
                <div class="metric-label">平均出行距离 (km)</div>
            </div>
            <div class="metric-card">
                <div class="metric-value">{{ max_cluster_share }}</div>
                <div class="metric-label">最大商圈 POI 占比</div>
            </div>
        </div>
    </div>
    
    <div class="section">
        <h2>上车点热力分布</h2>
        <div class="chart">
            <img src="pickup_heatmap.png" alt="上车点热力图">
        </div>
        <div class="insight">
            <h4>洞察</h4>
            <p>热力图显示，出租车订单高度集中在城市核心区及主要交通枢纽周边，形成明显热点区域，说明这些区域的出行需求最为旺盛。注：该图仅使用深圳出租车数据，与下方上海 POI 聚类不是同一城市，不能相互印证。</p>
        </div>
    </div>
    
    <div class="section">
        <h2>OD 出行矩阵</h2>
        <div class="chart">
            <img src="od_matrix_heatmap.png" alt="OD 矩阵">
        </div>
        <div class="insight">
            <h4>洞察</h4>
            <p>OD 矩阵揭示了区域间的出行流向模式。对角线颜色较深说明区域内短距离出行占主导，跨区出行主要集中在核心区与郊区之间。</p>
        </div>
    </div>
    
    <div class="section">
        <h2>POI 商圈聚类</h2>
        <div class="chart">
            <img src="poi_clustering.png" alt="POI 聚类">
        </div>
        <div class="insight">
            <h4>洞察</h4>
            <p>通过 DBSCAN 密度聚类（eps={{ eps_used }}°，min_samples={{ min_samples }}），识别出 {{ cluster_count }} 个高密度 POI 商圈。最大商圈包含 {{ max_cluster_share }} 的 POI；该比例过高说明 eps 偏大或 POI 本身高度集中，需要调小 eps 复核。噪声点主要分布在 POI 稀疏区域。聚类仅使用上海 POI 与上海区县边界，与上方深圳出租车热力图无关。</p>
        </div>
        {% if cluster_table %}
        <h3>商圈统计</h3>
        <table>
            <tr><th>商圈 ID</th><th>中心经度</th><th>中心纬度</th><th>POI 数量</th></tr>
            {% for row in cluster_table %}
            <tr>
                <td>{{ row.cluster_id }}</td>
                <td>{{ row.center_lng }}</td>
                <td>{{ row.center_lat }}</td>
                <td>{{ row.poi_count }}</td>
            </tr>
            {% endfor %}
        </table>
        {% endif %}
    </div>
    
    <div class="section">
        <h2>分析方法论</h2>
        <ul>
            <li><strong>数据清洗：</strong>过滤经纬度超出合理范围的记录，缺失坐标直接剔除</li>
            <li><strong>热力图：</strong>基于 Folium 与 Matplotlib 双引擎渲染；Folium 交互图对上车点采样 5,000 个以控制 HTML 体积，静态图对同一批采样点做 80×80 分箱（YlOrRd，线性色标）</li>
            <li><strong>OD 矩阵：</strong>按 0.05° 网格划分区域，统计 Top15 区域间出行流量</li>
            <li><strong>聚类算法：</strong>DBSCAN 密度聚类（eps={{ eps_used }}°，min_samples={{ min_samples }}，{{ eps_source }}），并输出最大簇占比作为聚类质量指标</li>
            <li><strong>平均距离口径：</strong>{{ distance_source }}</li>
            <li><strong>城市与坐标系：</strong>出租车轨迹为深圳 WGS84 坐标；POI 与行政边界为上海数据（POI 坐标系未标注，通常为 GCJ-02，未做纠偏），两组数据不做同城叠加分析</li>
        </ul>
    </div>
    
    <div class="section">
        <h2>技术栈</h2>
        <p>Python | Pandas | GeoPandas | Scikit-learn | Folium | Matplotlib | Seaborn | Jinja2</p>
    </div>
</body>
</html>"""


def generate_html_report(data):
    # TODO: HTML模板应该拆到单独文件里，现在嵌在代码里太长太难维护
    taxi_od = data['taxi_od']
    poi = data['poi']

    total_orders = len(taxi_od)
    poi_count = len(poi)

    # 平均出行距离：优先用 Distance 列，缺失时用起终点经纬度现算，不再输出 N/A
    if 'Distance' in taxi_od.columns:
        distances = pd.to_numeric(taxi_od['Distance'], errors='coerce')
        distance_source = '直接使用 TaxiOD 的 Distance 列（km）'
    else:
        missing = [c for c in ('SLng', 'SLat', 'ELng', 'ELat') if c not in taxi_od.columns]
        if missing:
            raise ValueError(
                f'TaxiOD 既无 Distance 列，也缺少坐标列 {missing}，无法计算平均出行距离'
            )
        distances = pd.Series(
            haversine_km(taxi_od['SLng'], taxi_od['SLat'], taxi_od['ELng'], taxi_od['ELat']),
            index=taxi_od.index,
        )
        distance_source = 'TaxiOD 无 Distance 列，按起终点经纬度用 haversine 现算（km）'
    avg_dist = float(distances.mean())
    if not np.isfinite(avg_dist):
        raise ValueError(
            '平均出行距离无法计算：Distance 列全为空或起终点坐标无效，请检查 TaxiOD 数据'
        )

    # 聚类结果只接受本次运行的内存结果，避免静默读取上一次的旧 CSV
    cluster_result = data.get('cluster_result')
    if not cluster_result or cluster_result.get('stats') is None:
        raise RuntimeError(
            '缺少聚类结果，无法生成报告：请先运行 cluster_poi()。'
            '本模块不再回退读取 output/cluster_statistics.csv 旧文件。'
        )
    cluster_stats = cluster_result['stats']
    cluster_count = len(cluster_stats)
    cluster_table = [
        {
            'cluster_id': int(row['cluster_id']),
            'center_lng': f"{row['center_lng']:.5f}",
            'center_lat': f"{row['center_lat']:.5f}",
            'poi_count': int(row['poi_count']),
        }
        for _, row in cluster_stats.iterrows()
    ]

    template = Template(REPORT_TEMPLATE)
    html = template.render(
        timestamp=pd.Timestamp.now().strftime('%Y-%m-%d %H:%M'),
        total_orders=f"{total_orders:,}",
        poi_count=f"{poi_count:,}",
        cluster_count=cluster_count,
        avg_distance=f"{avg_dist:.1f}",
        distance_source=distance_source,
        max_cluster_share=f"{cluster_result['max_cluster_share']:.1%}",
        eps_used=f"{cluster_result['eps']:.4f}",
        eps_source=cluster_result['eps_source'],
        min_samples=cluster_result['min_samples'],
        cluster_table=cluster_table,
    )

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    report_path = os.path.join(OUTPUT_DIR, 'insight_report.html')
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(html)

    print("  报告已生成: output/insight_report.html")
