"""商圈聚类分析模块"""
import os

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.cluster import DBSCAN
from sklearn.neighbors import NearestNeighbors

from .plot_config import setup_plot_style

OUTPUT_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'output')

DEFAULT_MIN_SAMPLES = 5
DEFAULT_EPS = 0.01
# 自动估计出的 eps 限制在合理范围内（单位：度）：约 55m ~ 5.5km
EPS_MIN = 0.0005
EPS_MAX = 0.05
# 最大簇占比超过该阈值时告警，说明 eps 可能过大、聚类退化
MAX_CLUSTER_SHARE_WARN = 0.5


def estimate_eps(coords, min_samples=DEFAULT_MIN_SAMPLES):
    """用 k-距离曲线的拐点估计 DBSCAN 的 eps。

    coords: shape=(n_samples, 2) 的经纬度数组。
    返回估计出的 eps（度）；样本量不足或曲线退化时返回 None。
    """
    n_samples = len(coords)
    if n_samples <= max(min_samples, 2):
        return None

    neighbors = NearestNeighbors(n_neighbors=min_samples).fit(coords)
    distances, _ = neighbors.kneighbors(coords)
    k_dist = np.sort(distances[:, -1])

    span = k_dist[-1] - k_dist[0]
    if span <= 0:
        return None

    x = np.linspace(0.0, 1.0, n_samples)
    y = (k_dist - k_dist[0]) / span
    # 拐点：到首尾连线（y=x）垂直距离最大的位置
    knee_index = int(np.argmax(np.abs(y - x)))
    eps = float(k_dist[knee_index])
    return float(np.clip(eps, EPS_MIN, EPS_MAX))


def _find_coord_columns(df):
    """识别 POI 表中的经纬度列。"""
    lat_col = lng_col = None
    for column in df.columns:
        name = str(column).lower()
        if lat_col is None and ('lat' in name or '纬度' in name):
            lat_col = column
        if lng_col is None and ('lon' in name or 'lng' in name or '经度' in name):
            lng_col = column
    return lat_col, lng_col


def _plot_boundary(ax, boundary):
    """把上海市区县边界叠加到聚类图上（仅作底图参考）。"""
    if boundary is None or boundary.empty:
        return
    try:
        if boundary.crs is not None and boundary.crs.to_epsg() != 4326:
            boundary = boundary.to_crs(4326)
        boundary.plot(
            ax=ax, facecolor='none', edgecolor='#555555', linewidth=0.6, alpha=0.8
        )
    except Exception as exc:  # 底图失败不影响主图输出
        print(f'  [警告] 行政边界叠加失败，已跳过: {exc}')


def cluster_poi(
    data,
    eps=None,
    min_samples=DEFAULT_MIN_SAMPLES,
    max_cluster_share_warn=MAX_CLUSTER_SHARE_WARN,
):
    """对 POI 做 DBSCAN 聚类。

    eps 为 None 时基于 k-距离曲线自动估计；也可传入固定值（单位：度）。
    返回聚类结果字典；无可用数据时返回 None。
    """
    poi = data['poi']
    if poi.empty:
        print('  POI 数据为空，跳过聚类')
        return None

    lat_col, lng_col = _find_coord_columns(poi)
    if lat_col is None or lng_col is None:
        print(f'  无法识别经纬度列，可用列: {list(poi.columns)}')
        return None

    coords = poi[[lng_col, lat_col]].dropna().copy()
    coords = coords[(coords[lng_col] > 70) & (coords[lng_col] < 140)]
    coords = coords[(coords[lat_col] > 15) & (coords[lat_col] < 55)]
    if len(coords) <= min_samples:
        print(f'  有效 POI 点仅 {len(coords)} 个，不足以聚类，跳过')
        return None

    if eps is None:
        eps = estimate_eps(coords[[lng_col, lat_col]].to_numpy(), min_samples)
        if eps is None:
            eps = DEFAULT_EPS
            eps_source = 'k-距离曲线退化，回退默认值'
        else:
            eps_source = 'k-距离曲线自动估计'
    else:
        eps = float(eps)
        if eps <= 0:
            raise ValueError(f'eps 必须大于 0，当前为 {eps}')
        eps_source = '手动指定'
    print(f'  eps={eps:.4f}°（{eps_source}），min_samples={min_samples}')

    db = DBSCAN(eps=eps, min_samples=min_samples).fit(coords[[lng_col, lat_col]].to_numpy())
    labels = db.labels_
    coords['cluster'] = labels

    n_clusters = len(set(labels)) - (1 if -1 in labels else 0)
    n_noise = int((labels == -1).sum())
    clustered = labels[labels != -1]
    if len(clustered):
        largest_cluster_size = int(np.bincount(clustered).max())
        max_cluster_share = largest_cluster_size / len(coords)
    else:
        largest_cluster_size = 0
        max_cluster_share = 0.0

    print(
        f'  聚类完成: {n_clusters} 个商圈，{n_noise} 个噪声点，'
        f'最大簇 {largest_cluster_size} 个点，占比 {max_cluster_share:.1%}'
    )
    if max_cluster_share > max_cluster_share_warn:
        print(
            f'  [警告] 最大簇占比 {max_cluster_share:.1%} 超过阈值 '
            f'{max_cluster_share_warn:.0%}，eps={eps:.4f}° 可能偏大，'
            '聚类结果接近“一个大簇 + 噪声”，建议调小 eps（见 README）'
        )

    setup_plot_style()
    fig, ax = plt.subplots(figsize=(12, 10))
    scatter = ax.scatter(
        coords[lng_col], coords[lat_col],
        c=coords['cluster'], cmap='tab20', s=15, alpha=0.7
    )
    fig.colorbar(scatter, ax=ax, label='聚类标签')
    _plot_boundary(ax, data.get('boundary'))
    ax.set_xlabel('Longitude')
    ax.set_ylabel('Latitude')
    ax.set_title(
        f'POI Business District Clustering (DBSCAN)\n'
        f'Found {n_clusters} districts, {n_noise} noise points, eps={eps:.4f}°'
    )
    fig.tight_layout()
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    fig.savefig(os.path.join(OUTPUT_DIR, 'poi_clustering.png'), dpi=150)
    plt.close(fig)

    cluster_stats = coords.groupby('cluster').agg({
        lng_col: ['mean', 'count'],
        lat_col: 'mean',
    }).reset_index()
    cluster_stats.columns = ['cluster_id', 'center_lng', 'poi_count', 'center_lat']
    cluster_stats = cluster_stats[cluster_stats['cluster_id'] != -1]
    cluster_stats['share_of_total'] = cluster_stats['poi_count'] / len(coords)
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    cluster_stats.to_csv(
        os.path.join(OUTPUT_DIR, 'cluster_statistics.csv'),
        index=False, encoding='utf-8-sig'
    )

    print('  聚类图已保存: output/poi_clustering.png')
    return {
        'stats': cluster_stats,
        'n_clusters': n_clusters,
        'n_noise': n_noise,
        'max_cluster_share': max_cluster_share,
        'largest_cluster_size': largest_cluster_size,
        'eps': eps,
        'min_samples': min_samples,
        'eps_source': eps_source,
    }
