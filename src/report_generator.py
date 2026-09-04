"""HTML 报告生成模块"""
import os
import pandas as pd
from jinja2 import Template

OUTPUT_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'output')

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
        <p>基于出租车 GPS 轨迹与 POI 数据的城市空间分析 | 生成时间: {{ timestamp }}</p>
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
        </div>
    </div>
    
    <div class="section">
        <h2>上车点热力分布</h2>
        <div class="chart">
            <img src="pickup_heatmap.png" alt="上车点热力图">
        </div>
        <div class="insight">
            <h4>洞察</h4>
            <p>热力图显示，出租车订单高度集中在内环以内及主要交通枢纽周边。核心商圈与交通枢纽形成明显热点区域，说明这些区域的出行需求最为旺盛。</p>
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
            <p>通过 DBSCAN 密度聚类，识别出 {{ cluster_count }} 个高密度 POI 商圈。聚类中心与热力图热点高度重合，验证了核心商圈的空间分布特征。噪声点主要分布在低密度区域。</p>
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
            <li><strong>数据清洗：</strong>去除经纬度异常值，过滤异常经纬度数据</li>
            <li><strong>热力图：</strong>基于 Folium 与 Matplotlib 双引擎渲染，支持交互与静态两种视图</li>
            <li><strong>OD 矩阵：</strong>按 0.05° 网格划分区域，统计区域间出行流量</li>
            <li><strong>聚类算法：</strong>DBSCAN 密度聚类（eps=0.01°, min_samples=5），自动识别高密度商圈</li>
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
    
    if 'Distance' in taxi_od.columns:
        avg_dist = taxi_od['Distance'].mean()
    else:
        avg_dist = 0
    
    cluster_file = os.path.join(OUTPUT_DIR, 'cluster_statistics.csv')
    cluster_count = 0
    cluster_table = []
    if os.path.exists(cluster_file):
        cluster_df = pd.read_csv(cluster_file)
        cluster_count = len(cluster_df)
        cluster_table = cluster_df.to_dict('records')
    
    template = Template(REPORT_TEMPLATE)
    html = template.render(
        timestamp=pd.Timestamp.now().strftime('%Y-%m-%d %H:%M'),
        total_orders=f"{total_orders:,}",
        poi_count=f"{poi_count:,}",
        cluster_count=cluster_count,
        avg_distance=f"{avg_dist:.1f}" if avg_dist > 0 else "N/A",
        cluster_table=cluster_table,
    )
    
    report_path = os.path.join(OUTPUT_DIR, 'insight_report.html')
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(html)
    
    print("  报告已生成: output/insight_report.html")
