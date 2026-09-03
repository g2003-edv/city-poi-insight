"""OD 矩阵分析模块"""
import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

OUTPUT_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'output')


def analyze_od_matrix(data):
    taxi_od = data['taxi_od']
    
    taxi_od['S_grid_lon'] = (taxi_od['SLng'] / 0.05).astype(int)
    taxi_od['S_grid_lat'] = (taxi_od['SLat'] / 0.05).astype(int)
    taxi_od['E_grid_lon'] = (taxi_od['ELng'] / 0.05).astype(int)
    taxi_od['E_grid_lat'] = (taxi_od['ELat'] / 0.05).astype(int)
    
    taxi_od['S_zone'] = taxi_od['S_grid_lon'].astype(str) + '_' + taxi_od['S_grid_lat'].astype(str)
    taxi_od['E_zone'] = taxi_od['E_grid_lon'].astype(str) + '_' + taxi_od['E_grid_lat'].astype(str)
    
    top_zones = taxi_od['S_zone'].value_counts().head(15).index.tolist()
    
    od_filtered = taxi_od[
        taxi_od['S_zone'].isin(top_zones) & taxi_od['E_zone'].isin(top_zones)
    ]
    
    od_matrix = od_filtered.groupby(['S_zone', 'E_zone']).size().unstack(fill_value=0)
    
    plt.figure(figsize=(12, 10))
    sns.heatmap(od_matrix, cmap='YlOrRd', annot=False, fmt='d', cbar_kws={'label': '出行量'})
    plt.title('Top Area OD Travel Matrix', fontsize=14)
    plt.xlabel('Destination Zone')
    plt.ylabel('Origin Zone')
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, 'od_matrix_heatmap.png'), dpi=150)
    plt.close()
    
    od_stats = taxi_od.groupby('S_zone').agg({
        'ELng': 'mean',
        'ELat': 'mean',
    }).reset_index()
    od_stats.columns = ['zone', 'avg_dest_lng', 'avg_dest_lat']
    od_stats['order_count'] = taxi_od['S_zone'].value_counts().reindex(od_stats['zone']).values
    od_stats.to_csv(os.path.join(OUTPUT_DIR, 'od_statistics.csv'), index=False, encoding='utf-8-sig')
    
    print("  OD 矩阵已保存: output/od_matrix_heatmap.png, output/od_statistics.csv")
