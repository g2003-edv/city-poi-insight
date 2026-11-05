# 城市POI数据洞察

用出租车 GPS 轨迹数据和 POI 点数据做的空间分析小项目，输出热力图、OD 矩阵、DBSCAN 商圈聚类和 HTML 报告。

> **先看这里：两套数据不是同一个城市。** `data/TaxiOD.csv` 是**深圳**出租车轨迹（约 113.8–114.3°E / 22.5–22.7°N），而 `data/上海poi/` 与 `data/shanghai_shp/` 是**上海**数据（POI 约 121.4°E / 31.2°N）。两者只能各自独立分析，不能叠加成“上海出租车 + 上海 POI”的联合结论。此前 README 写的“上海出租车”“GeoPandas 坐标转换”“15,000 条轨迹”等表述均已按代码和实际数据更正。

## 项目概述

项目包含两条相互独立的分析线：

1. **深圳出租车 OD**：坐标过滤 → 上车点热力图 → 0.05° 网格 OD 矩阵；
2. **上海 POI**：坐标过滤 → DBSCAN 密度聚类 → 商圈统计（叠加上海区县边界作底图）。

两条线的结果仅在同一份 HTML 报告中并列展示，不代表同城关系。

**分析流程**：

```
TaxiOD.csv（深圳）──▶ 过滤异常经纬度 ──┬──▶ 上车点热力图（Folium + Matplotlib）
                                      └──▶ OD 矩阵（0.05° 网格，Top15 区域）

POI（上海）+ 区县界（上海）──▶ DBSCAN 聚类 ──▶ 商圈统计
                                                │
                    热力图 / OD 矩阵 / 聚类结果 ─┴──▶ insight_report.html
```

## 技术栈

Python、Pandas、GeoPandas（仅用于读取/叠加上海区县边界）、Scikit-learn、Folium、Matplotlib、Seaborn、Jinja2。

## 核心功能

| 模块 | 实现与输出 |
|------|------------|
| 数据加载 | CSV 编码兜底（UTF-8 → UTF-8-BOM → GBK）；TaxiOD 只读所需列、指定 dtype，超过 32 MB 或 100 万行时分块读取；过滤超出 70–140°E / 15–55°N 的坐标 |
| 热力图 | Folium 交互图（上车点采样 5,000 个）+ Matplotlib 静态图（`hist2d`，80×80 分箱，`YlOrRd` 线性色标） |
| OD 矩阵 | 0.05° 网格分区，Top15 热门区域流量矩阵，`YlOrRd` 热力图 |
| 商圈聚类 | DBSCAN；`eps` 默认由 k-距离曲线自动估计，`min_samples=5`；输出最大簇占比并在超过 50% 时告警 |
| 洞察报告 | Jinja2 生成 HTML；无 `Distance` 列时用 haversine 现算平均距离；缺少聚类结果时直接报错 |

## 数据规模（当前本地样本）

- 出租车 OD：文件 464,719 行（含表头，即 **464,718 条记录**），**11,036 个车辆 ID**，文件约 35 MB。
- POI：共 **41,511 个点位**，读取餐饮、医院、学校、影院、公交、火锅 6 类；`上海poi/` 下另有 5 类文件当前未使用。
- 工作区现有的 `output/cluster_statistics.csv`（已从 git 索引移除）来自旧参数 `eps=0.01` 的运行结果：141 个簇；最大簇 34,051 个点，占全部 POI 的 **82.0%**（占非噪声点 83.3%）。这说明旧 `eps` 已让聚类退化成“一个大簇 + 若干碎片”，改用自动 `eps` 后簇数量会变化。

## 数据

`data/README.md` 详细说明了各文件的路径、列名、编码和许可注意事项，务必先读。

- `data/TaxiOD.csv`：**不随仓库分发**。它包含车辆 ID 与精确到秒的上下车时间，可能关联到具体车辆或出行者，请自行通过合法渠道获取并本地放置。
- `data/上海poi/*.csv`、`data/shanghai_shp/`：随仓库分发。
- `data/*.csv` 已写入 `.gitignore`，`output/`、`__pycache__/`、`.venv/`、`*.log` 也不再入库；仓库索引中已有的大文件/产物已用 `git rm --cached` 移除（磁盘文件保留）。

## 快速开始

```bash
# 1. 按 data/README.md 准备 data/TaxiOD.csv
pip install -r requirements.txt
python main.py
```

输出写入 `output/`（目录不存在会自动创建）：

```
output/
├── pickup_heatmap.html      # 交互热力图
├── pickup_heatmap.png       # 静态热力图
├── od_matrix_heatmap.png    # OD 矩阵热力图
├── od_statistics.csv        # 各上车网格统计
├── poi_clustering.png       # POI 聚类图（叠加上海区县边界）
├── cluster_statistics.csv   # 各商圈中心、POI 数量、占比
└── insight_report.html      # HTML 洞察报告
```

## 聚类参数怎么调

默认 `eps=None`，由 k-距离曲线拐点自动估计，并限制在 0.0005°–0.05°（上海纬度下约 55 m–5.5 km）。也可以用环境变量覆盖：

```bash
# 手动指定 eps（单位：度）
CLUSTER_EPS=0.003 python main.py

# 调整最小样本数
CLUSTER_MIN_SAMPLES=8 python main.py
```

调整建议：

- 控制台出现“最大簇占比超过阈值”警告时，说明 `eps` 过大，把 `CLUSTER_EPS` 调小（例如从 0.01 降到 0.003）；
- 簇数量过多、噪声点占比过高时，说明 `eps` 过小，适当调大；
- 每次运行都会打印 `eps`、簇数量、噪声点数和最大簇占比；报告与 `cluster_statistics.csv`（`share_of_total` 列）也会给出占比。

## 已知限制

- **城市不一致**：热力图/OD 是深圳，聚类是上海，报告中任何“热点与商圈重合”的说法都不成立。
- **POI 坐标系**：POI 文件未标注坐标系，字段风格与高德 POI 相近（通常为 GCJ-02）；本仓库不做 GCJ-02 → WGS84 纠偏，与 WGS84 边界叠加时可能有数百米偏移。
- **采样**：Folium 交互图只展示 5,000 个上车点以控制 HTML 体积，稀疏区域会被低估。
- **网格尺寸**：OD 的 0.05° 网格是硬编码的，换城市或换尺度需要改 `src/od_matrix.py`。
- **聚类退化**：即使自动选 `eps`，POI 本身高度集中时仍可能出现大簇，需结合最大簇占比人工复核。

## 数据来源与限制

- 出租车 GPS 轨迹：深圳出租车 OD 数据，字段与时间精度见 `data/README.md`。该数据**不随本仓库分发**，使用前请确认来源合法并遵守数据提供方的许可与个人信息保护要求，请勿公开再分发。
- POI：随仓库保留的上海 POI 点数据。原始来源与再分发许可需使用者自行确认，本仓库不对其授权状态作保证。
- 行政边界：上海市区县界 shapefile（WGS84）。

## 踩坑记录（按当前代码更正）

- **城市弄错**：早期文档把深圳出租车数据写成“上海出租车”，并假设能与上海 POI 联合分析。实际两地相距约 1,200 km，只能分别分析。
- **坐标系**：上海边界是 WGS84，POI 很可能是 GCJ-02。代码里没有“GPS 坐标转换”步骤；GeoPandas 只负责读取边界、必要时 `to_crs(4326)` 并叠加到底图。
- **DBSCAN 参数**：`eps=0.01` 会把 82% 的 POI 塞进同一个簇，已改为 k-距离曲线自动估计，并输出最大簇占比告警。
- **Folium 性能**：点太多时 HTML 很大，已对交互图采样 5,000 个点。
- **OD 配色**：实际代码使用 `YlOrRd`，**没有做 log 变换**；早期文档写的 viridis + log 与代码不符。
- **中文图表**：字体配置集中在 `src/plot_config.py`（Microsoft YaHei → SimHei → DejaVu Sans，并关闭负号乱码），热力图、OD、聚类图共用。

## License

MIT（仅覆盖代码与随仓库分发的小型数据文件；`data/TaxiOD.csv` 不在授权范围内）。
