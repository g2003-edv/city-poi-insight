"""
城市 POI 数据洞察
出租车轨迹（深圳）与 POI / 行政边界（上海）为两套独立数据，分别做空间分析与聚类
"""
import os

from src.data_loader import load_all_data
from src.heatmap import generate_heatmap
from src.od_matrix import analyze_od_matrix
from src.clustering import cluster_poi
from src.report_generator import generate_html_report


def main():
    print("=== 城市 POI 数据洞察 ===")
    # TODO: 应该把分析步骤和参数配置化，现在改个路径要动代码

    print("[1/4] 加载数据...")
    data = load_all_data()

    print("[2/4] 生成上车点热力图...")
    generate_heatmap(data)

    print("[3/4] OD 矩阵分析...")
    analyze_od_matrix(data)

    print("[4/4] 商圈聚类分析...")
    eps_env = os.environ.get('CLUSTER_EPS')
    eps = float(eps_env) if eps_env else None
    min_samples = int(os.environ.get('CLUSTER_MIN_SAMPLES', '5'))
    data['cluster_result'] = cluster_poi(data, eps=eps, min_samples=min_samples)

    print("[*] 生成 HTML 洞察报告...")
    generate_html_report(data)

    print("\n全部完成，输出文件在 output/ 目录")


if __name__ == '__main__':
    main()
