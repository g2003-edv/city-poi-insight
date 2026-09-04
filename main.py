"""
城市 POI 数据洞察
基于上海出租车 GPS 与 POI 数据的多维度空间分析
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
    cluster_poi(data)
    
    print("[*] 生成 HTML 洞察报告...")
    generate_html_report(data)
    
    print("\n全部完成，输出文件在 output/ 目录")


if __name__ == '__main__':
    main()
