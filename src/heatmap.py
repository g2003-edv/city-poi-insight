"""热力图生成模块"""
import os

import folium
from folium.plugins import HeatMap
import matplotlib.pyplot as plt

from .plot_config import setup_plot_style

OUTPUT_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'output')


def generate_heatmap(data):
    taxi_od = data['taxi_od']

    pickup_points = taxi_od[['SLng', 'SLat']].dropna()
    if pickup_points.empty:
        raise ValueError('出租车数据中没有可用的上车点坐标，无法生成热力图')
    pickup_points = pickup_points.sample(min(5000, len(pickup_points)), random_state=42)
    # TODO: 采样5000个点是为了防止Folium卡顿，但会丢失稀疏区域的信息，考虑用聚类聚合代替采样

    center_lat = pickup_points['SLat'].median()
    center_lng = pickup_points['SLng'].median()
    m = folium.Map(location=[center_lat, center_lng], zoom_start=11, tiles='CartoDB positron')
    HeatMap(pickup_points.values, radius=12, blur=15, max_zoom=13).add_to(m)

    title_html = '<div style="position: fixed; top: 10px; left: 50px; z-index: 9999; background: white; padding: 10px 15px; border-radius: 5px; box-shadow: 0 2px 5px rgba(0,0,0,0.2); font-weight: bold;">城市出租车上车点热力分布</div>'
    m.get_root().html.add_child(folium.Element(title_html))

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    m.save(os.path.join(OUTPUT_DIR, 'pickup_heatmap.html'))

    setup_plot_style()
    fig, ax = plt.subplots(figsize=(10, 8))
    ax.hist2d(pickup_points['SLng'], pickup_points['SLat'], bins=80, cmap='YlOrRd')
    fig.colorbar(ax.collections[0], ax=ax, label='Order Density')
    ax.set_xlabel('Longitude')
    ax.set_ylabel('Latitude')
    ax.set_title('城市出租车上车点热力分布（静态图）')
    fig.tight_layout()
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    fig.savefig(os.path.join(OUTPUT_DIR, 'pickup_heatmap.png'), dpi=150)
    plt.close(fig)

    print("  热力图已保存: output/pickup_heatmap.html, output/pickup_heatmap.png")
