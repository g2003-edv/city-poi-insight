"""商圈聚类分析模块"""
import os
import pandas as pd
from sklearn.cluster import DBSCAN
import matplotlib.pyplot as plt

OUTPUT_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'output')


def cluster_poi(data):
    poi = data['poi']
    if poi.empty:
        print("  POI 数据为空，跳过聚类")
        return
    
    lat_col = None
    lng_col = None
    for c in poi.columns:
        if 'lat' in c.lower() or '纬度' in c:
            lat_col = c
        if 'lon' in c.lower() or 'lng' in c.lower() or '经度' in c:
            lng_col = c
    
    if lat_col is None or lng_col is None:
        print(f"  无法识别经纬度列，可用列: {list(poi.columns)}")
        return
    
    coords = poi[[lng_col, lat_col]].dropna()
    coords = coords[(coords[lng_col] > 70) & (coords[lng_col] < 140)]
    coords = coords[(coords[lat_col] > 15) & (coords[lat_col] < 55)]
    
    eps = 0.01
    db = DBSCAN(eps=eps, min_samples=5).fit(coords.values)
    coords['cluster'] = db.labels_
    
    n_clusters = len(set(db.labels_)) - (1 if -1 in db.labels_ else 0)
    n_noise = list(db.labels_).count(-1)
    
    plt.figure(figsize=(12, 10))
    scatter = plt.scatter(
        coords[lng_col], coords[lat_col], 
        c=coords['cluster'], cmap='tab20', s=15, alpha=0.7
    )
    plt.colorbar(scatter, label='聚类标签')
    plt.xlabel('Longitude')
    plt.ylabel('Latitude')
    plt.title(f'POI Business District Clustering (DBSCAN)\nFound {n_clusters} districts, {n_noise} noise points')
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, 'poi_clustering.png'), dpi=150)
    plt.close()
    
    cluster_stats = coords.groupby('cluster').agg({
        lng_col: ['mean', 'count'],
        lat_col: 'mean'
    }).reset_index()
    cluster_stats.columns = ['cluster_id', 'center_lng', 'poi_count', 'center_lat']
    cluster_stats = cluster_stats[cluster_stats['cluster_id'] != -1]
    cluster_stats.to_csv(os.path.join(OUTPUT_DIR, 'cluster_statistics.csv'), index=False, encoding='utf-8-sig')
    
    print(f"  聚类完成: 发现 {n_clusters} 个商圈，保存至 output/poi_clustering.png")
