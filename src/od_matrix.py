"""OD 矩阵分析模块"""
import os

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

from .plot_config import setup_plot_style

OUTPUT_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'output')


def analyze_od_matrix(data):
    taxi_od = data['taxi_od']
    if taxi_od.empty:
        raise ValueError('出租车 OD 数据为空，无法生成 OD 矩阵')

    taxi_od['S_grid_lon'] = (taxi_od['SLng'] / 0.05).astype(int)
    taxi_od['S_grid_lat'] = (taxi_od['SLat'] / 0.05).astype(int)
    taxi_od['E_grid_lon'] = (taxi_od['ELng'] / 0.05).astype(int)
    taxi_od['E_grid_lat'] = (taxi_od['ELat'] / 0.05).astype(int)
    # FIXME: 0.05°网格大小是硬编码的，不同城市尺度不一样，应该根据数据范围自动计算

    taxi_od['S_zone'] = taxi_od['S_grid_lon'].astype(str) + '_' + taxi_od['S_grid_lat'].astype(str)
    taxi_od['E_zone'] = taxi_od['E_grid_lon'].astype(str) + '_' + taxi_od['E_grid_lat'].astype(str)

    top_zones = taxi_od['S_zone'].value_counts().head(15).index.tolist()

    od_filtered = taxi_od[
        taxi_od['S_zone'].isin(top_zones) & taxi_od['E_zone'].isin(top_zones)
    ]

    od_matrix = od_filtered.groupby(['S_zone', 'E_zone']).size().unstack(fill_value=0)

    setup_plot_style()
    fig, ax = plt.subplots(figsize=(12, 10))
    sns.heatmap(od_matrix, cmap='YlOrRd', annot=False, fmt='d', cbar_kws={'label': '出行量'}, ax=ax)
    ax.set_title('Top Area OD Travel Matrix', fontsize=14)
    ax.set_xlabel('Destination Zone')
    ax.set_ylabel('Origin Zone')
    fig.tight_layout()
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    fig.savefig(os.path.join(OUTPUT_DIR, 'od_matrix_heatmap.png'), dpi=150)
    plt.close(fig)

    od_stats = taxi_od.groupby('S_zone').agg({
        'ELng': 'mean',
        'ELat': 'mean',
    }).reset_index()
    od_stats.columns = ['zone', 'avg_dest_lng', 'avg_dest_lat']
    od_stats['order_count'] = taxi_od['S_zone'].value_counts().reindex(od_stats['zone']).values
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    od_stats.to_csv(os.path.join(OUTPUT_DIR, 'od_statistics.csv'), index=False, encoding='utf-8-sig')

    print("  OD 矩阵已保存: output/od_matrix_heatmap.png, output/od_statistics.csv")
