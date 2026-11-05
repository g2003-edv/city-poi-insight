# 数据目录说明

仓库只保留体量较小、可公开分发的 POI 点数据与上海市区县边界；出租车轨迹数据包含可识别的车辆与时间信息，**不随仓库分发**。

## 目录结构

```
data/
├── TaxiOD.csv          # 出租车 OD 轨迹（不随仓库分发，需自行准备）
├── taxi_od_grid.csv    # 历史分析中间产物（不随仓库分发，当前 pipeline 不生成）
├── shanghai_shp/       # 上海市区县行政边界（随仓库分发）
└── 上海poi/            # 上海 POI 点数据（随仓库分发）
```

## TaxiOD.csv：需自行准备

`data/TaxiOD.csv` 是**深圳**出租车轨迹 OD 数据，每一行包含车辆编号与精确到秒的上下车时间，属于可能关联到具体车辆或出行者的轨迹数据。仓库不收录该文件，请通过合法渠道自行获取、本地放置，并遵守数据提供方的许可协议与当地个人信息保护法规；请勿公开再分发。

- 路径：`data/TaxiOD.csv`（固定，加载器不会自动搜索其他位置）
- 编码：UTF-8、UTF-8 with BOM、GBK 均可（`src/data_loader.py` 依次尝试）
- 必需列（大小写敏感）：
  | 列名 | 含义 | 类型 |
  |------|------|------|
  | `SLng` | 上车点经度（WGS84 十进制度） | float，有效范围 70–140 |
  | `SLat` | 上车点纬度（WGS84 十进制度） | float，有效范围 15–55 |
  | `ELng` | 下车点经度（WGS84 十进制度） | float，有效范围 70–140 |
  | `ELat` | 下车点纬度（WGS84 十进制度） | float，有效范围 15–55 |
- 可选列：
  | 列名 | 含义 | 说明 |
  |------|------|------|
  | `VehicleNum` | 车辆 ID | 加载时按类别类型读取以节省内存 |
  | `Stime` / `Etime` | 上车 / 下车时间 | 当前分析未使用 |
  | `Distance` | 单次行程距离（km） | 存在则报告直接使用；不存在时报告用 haversine 从起终点经纬度现算 |
- 额外列会被忽略；缺少必需列会直接报错并提示。

当前样本规模供参考：文件 464,719 行（含表头，即 464,718 条 OD 记录）、11,036 个不同车辆 ID，坐标约 113.8–114.3°E / 22.5–22.7°N（深圳）。

> **城市不一致提醒**：TaxiOD 是深圳坐标，而本仓库的 POI（约 121.4°E / 31.2°N）与行政边界（上海）属于另一座城市。二者只能作为独立模块分别分析，不能叠加成“同城出租车 + POI”的联合结论。读取超过 32 MB 或 100 万行的 TaxiOD 时会自动分块读取，避免一次性占用过多内存。

## 上海poi/：随仓库分发

`src/data_loader.py` 读取以下 6 个文件：

```
shanghai_food.csv          餐饮
shanghai_hospital.csv      医院
shanghai_school.csv        学校
shanghai_Theatr_Cinema.csv 影院
shanghai_bus.csv           公交
shanghai_hotpot.csv        火锅
```

- 列：`name,address,adname,pname,type,lat,lon`，必需 `lat`、`lon`（十进制度）。
- 当前 6 类合计 41,511 个点位。
- 文件未标注坐标系；字段风格与高德 POI 相近，通常为 GCJ-02。本仓库不做 GCJ-02 → WGS84 纠偏，与 WGS84 边界叠加时可能存在数百米偏移。
- `上海poi/` 下其余 CSV（`中学.csv`、`大学.csv` 等）当前 pipeline 未读取，保留作扩展数据。

## shanghai_shp/：随仓库分发

`区县界_area.shp` 及同名 `.dbf/.shx/.prj/.shp.xml`，CRS 为 WGS84（`GEOGCS["GCS_WGS_1984"]`）。仅用于在 POI 聚类图上叠加行政区边界作为底图参考，不参与出租车坐标转换。

## 派生文件

`taxi_od_grid.csv` 与 `output/` 下的 CSV、PNG、HTML 都是分析产物或历史中间文件，已加入 `.gitignore`，不再入库。重新生成请运行 `python main.py`（输出写入 `output/`，目录不存在时会自动创建）。
