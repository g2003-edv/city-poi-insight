"""Matplotlib 公共配置（中文字体、负号显示等）。"""
import matplotlib.pyplot as plt

# 按优先级排列：Windows 常见中文字体 → 通用无衬线字体
FONT_FAMILIES = ['Microsoft YaHei', 'SimHei', 'DejaVu Sans']


def setup_plot_style():
    """统一图表样式，避免中文标题/坐标轴出现方块和负号乱码。"""
    plt.rcParams['font.sans-serif'] = FONT_FAMILIES
    plt.rcParams['axes.unicode_minus'] = False
