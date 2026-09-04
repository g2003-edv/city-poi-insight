"""热力图生成模块"""
import os
import pandas as pd
import folium
from folium.plugins import HeatMap
import matplotlib.pyplot as plt

OUTPUT_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'output')


def generate_heatmap(data):
    taxi_od = data['taxi_od']
    
    pickup_points = taxi_od[['SLng', 'SLat']].dropna()
    pickup_points = pickup_points.sample(min(5000, len(pickup_points)), random_state=42)
    # TODO: 采样5000个点是为了防止Folium卡顿，但会丢失稀疏区域的信息，考虑用聚类聚合代替采样
    
    center_lat = pickup_points['SLat'].median(); center_lng = pickup_points['SLng'].median(); m = folium.Map(location=[center_lat, center_lng], zoom_start=11, tiles='CartoDB positron')
    HeatMap(pickup_points.values, radius=12, blur=15, max_zoom=13).add_to(m)
    
    title_html = '<div style="position: fixed; top: 10px; left: 50px; z-index: 9999; background: white; padding: 10px 15px; border-radius: 5px; box-shadow: 0 2px 5px rgba(0,0,0,0.2); font-weight: bold;">城市出租车上车点热力分布</div>'
    m.get_root().html.add_child(folium.Element(title_html))
    
    m.save(os.path.join(OUTPUT_DIR, 'pickup_heatmap.html'))
    
    plt.figure(figsize=(10, 8))
    plt.hist2d(pickup_points['SLng'], pickup_points['SLat'], bins=80, cmap='YlOrRd')
    plt.colorbar(label='Order Density')
    plt.xlabel('Longitude')
    plt.ylabel('Latitude')
    plt.title('城市出租车上车点热力分布（静态图）')
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, 'pickup_heatmap.png'), dpi=150)
    plt.close()
    
    print("  热力图已保存: output/pickup_heatmap.html, output/pickup_heatmap.png")
