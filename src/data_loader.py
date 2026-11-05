"""数据加载模块。

数据城市说明：TaxiOD 为深圳出租车轨迹（约 114°E / 22.5°N），POI 与
行政边界为上海数据（约 121°E / 31.2°N）。两套数据来自不同城市，只做
独立分析，不能直接叠加。
"""
import os

import pandas as pd
import geopandas as gpd

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')

# CSV 编码兜底顺序：UTF-8 → UTF-8-BOM → GBK；带 BOM 的文件会优先用 utf-8-sig 读取
ENCODINGS = ('utf-8', 'utf-8-sig', 'gbk')

TAXI_COLUMNS = ['VehicleNum', 'Stime', 'SLng', 'SLat', 'ELng', 'ELat', 'Etime', 'Distance']
TAXI_REQUIRED = ['SLng', 'SLat', 'ELng', 'ELat']

# 超过该大小或行数时按 CHUNK_SIZE 分块读取并逐块过滤，降低大文件的内存峰值
CHUNK_THRESHOLD_BYTES = 32 * 1024 * 1024
ROW_CHUNK_THRESHOLD = 1_000_000
CHUNK_SIZE = 200_000
# 行数超过该阈值时提示，避免误用超大文件
ROW_WARN_THRESHOLD = 2_000_000

LNG_RANGE = (70, 140)
LAT_RANGE = (15, 55)


def _normalize_columns(df):
    """去掉列名上的 BOM 和首尾空白（UTF-8 BOM 文件用 utf-8 读取时会出现）。"""
    df.columns = [str(c).lstrip('\ufeff').strip() for c in df.columns]
    return df


def _candidate_encodings(path):
    """有 UTF-8 BOM 时优先 utf-8-sig，避免 BOM 混入首列列名。"""
    try:
        with open(path, 'rb') as f:
            has_bom = f.read(3) == b'\xef\xbb\xbf'
    except OSError:
        has_bom = False
    if has_bom:
        return ('utf-8-sig',) + tuple(e for e in ENCODINGS if e != 'utf-8-sig')
    return ENCODINGS


def read_csv_with_encoding(path, **kwargs):
    """按 utf-8 → utf-8-sig → gbk 依次尝试读取 CSV。"""
    last_error = None
    for encoding in _candidate_encodings(path):
        try:
            return _normalize_columns(pd.read_csv(path, encoding=encoding, **kwargs))
        except UnicodeDecodeError as exc:
            last_error = exc
    if last_error is not None:
        raise last_error
    raise RuntimeError(f'无法读取 CSV: {path}')


def _read_csv_chunked(path, transform=None, **kwargs):
    """分块读取并按块做转换；遇到编码错误时丢弃已读结果后用下一种编码重试。"""
    last_error = None
    for encoding in _candidate_encodings(path):
        parts = []
        try:
            reader = pd.read_csv(
                path, encoding=encoding, chunksize=CHUNK_SIZE, **kwargs
            )
            for chunk in reader:
                chunk = _normalize_columns(chunk)
                parts.append(transform(chunk) if transform else chunk)
            return parts
        except UnicodeDecodeError as exc:
            last_error = exc
    if last_error is not None:
        raise last_error
    raise RuntimeError(f'无法读取 CSV: {path}')


def _count_lines(path):
    """粗略统计文件行数（含表头），仅用于决定是否分块读取。"""
    with open(path, 'rb') as f:
        return sum(1 for _ in f)


def _filter_bbox(df):
    """过滤明显异常的经纬度（不在中国及周边合理范围内）。"""
    for column, (low, high) in (
        ('SLng', LNG_RANGE),
        ('SLat', LAT_RANGE),
        ('ELng', LNG_RANGE),
        ('ELat', LAT_RANGE),
    ):
        if column in df.columns:
            df = df[(df[column] > low) & (df[column] < high)]
    return df


def load_taxi_od():
    path = os.path.join(DATA_DIR, 'TaxiOD.csv')
    if not os.path.exists(path):
        raise FileNotFoundError(
            f'未找到出租车 OD 数据: {path}\n'
            '该数据含可识别车辆轨迹，不随仓库分发，请按 data/README.md 自行准备。'
        )

    header = read_csv_with_encoding(path, nrows=0)
    missing = [c for c in TAXI_REQUIRED if c not in header.columns]
    if missing:
        raise ValueError(
            f'TaxiOD.csv 缺少必需列 {missing}，实际列: {list(header.columns)}；'
            '列名要求见 data/README.md'
        )

    # 只读取分析需要的列并显式指定 dtype：
    # VehicleNum 用 category 存储可显著降低内存；时间列用 string 避免 object 开销
    usecols = [c for c in TAXI_COLUMNS if c in header.columns]
    dtype = {'VehicleNum': 'category', 'Stime': 'string', 'Etime': 'string', 'Distance': 'float64'}
    dtype = {k: v for k, v in dtype.items() if k in usecols}

    read_kwargs = dict(usecols=usecols, dtype=dtype, low_memory=False)
    file_size = os.path.getsize(path)
    if file_size > CHUNK_THRESHOLD_BYTES:
        should_chunk = True
        chunk_reason = f'文件 {file_size / 1024 / 1024:.1f} MB 超过 32 MB'
    else:
        row_count = _count_lines(path)
        should_chunk = row_count > ROW_CHUNK_THRESHOLD
        chunk_reason = f'行数 {row_count:,} 超过 {ROW_CHUNK_THRESHOLD:,}'
    if should_chunk:
        print(f'  {chunk_reason}，按 {CHUNK_SIZE:,} 行分块读取: {path}')
        parts = _read_csv_chunked(path, transform=_filter_bbox, **read_kwargs)
        df = pd.concat(parts, ignore_index=True) if parts else header.iloc[0:0]
        if 'VehicleNum' in df.columns and df['VehicleNum'].dtype.name != 'category':
            df['VehicleNum'] = df['VehicleNum'].astype('category')
    else:
        df = read_csv_with_encoding(path, **read_kwargs)
        df = _filter_bbox(df)

    if len(df) > ROW_WARN_THRESHOLD:
        print(
            f'  [警告] 出租车 OD 数据 {len(df):,} 行，超过 {ROW_WARN_THRESHOLD:,} 行，'
            '分析耗时和内存占用会明显增加，建议先抽样'
        )
    return df


def load_poi_data():
    poi_dir = os.path.join(DATA_DIR, '上海poi')
    poi_files = {
        '餐饮': 'shanghai_food.csv',
        '医院': 'shanghai_hospital.csv',
        '学校': 'shanghai_school.csv',
        '影院': 'shanghai_Theatr_Cinema.csv',
        '公交': 'shanghai_bus.csv',
        '火锅': 'shanghai_hotpot.csv',
    }
    poi_list = []
    for category, filename in poi_files.items():
        path = os.path.join(poi_dir, filename)
        if os.path.exists(path):
            df = read_csv_with_encoding(path)
            df['category'] = category
            poi_list.append(df)
    if poi_list:
        return pd.concat(poi_list, ignore_index=True)
    print(f'  [警告] 未找到 POI 数据文件: {poi_dir}')
    return pd.DataFrame()


def load_shanghai_boundary():
    """加载上海市区县边界（WGS84），仅用于聚类图叠加底图。"""
    shp_dir = os.path.join(DATA_DIR, 'shanghai_shp')
    shp_path = os.path.join(shp_dir, '区县界_area.shp')
    if os.path.exists(shp_path):
        return gpd.read_file(shp_path)
    print(f'  [警告] 未找到上海行政边界: {shp_path}')
    return None


def load_all_data():
    return {
        'taxi_od': load_taxi_od(),
        'poi': load_poi_data(),
        'boundary': load_shanghai_boundary(),
    }
