"""数据加载模块"""
import os
import pandas as pd
import geopandas as gpd

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')


def load_taxi_od():
    path = os.path.join(DATA_DIR, 'TaxiOD.csv')
    # FIXME: 有些CSV是GBK编码，这里没指定encoding，碰到会报错
    df = pd.read_csv(path)
    df = df[(df['SLng'] > 70) & (df['SLng'] < 140)]
    df = df[(df['SLat'] > 15) & (df['SLat'] < 55)]
    df = df[(df['ELng'] > 70) & (df['ELng'] < 140)]
    df = df[(df['ELat'] > 15) & (df['ELat'] < 55)]
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
            df = pd.read_csv(path)
            df['category'] = category
            poi_list.append(df)
    if poi_list:
        return pd.concat(poi_list, ignore_index=True)
    return pd.DataFrame()


def load_shanghai_boundary():
    shp_dir = os.path.join(DATA_DIR, 'shanghai_shp')
    shp_path = os.path.join(shp_dir, '区县界_area.shp')
    if os.path.exists(shp_path):
        return gpd.read_file(shp_path)
    return None


def load_all_data():
    return {
        'taxi_od': load_taxi_od(),
        'poi': load_poi_data(),
        'boundary': load_shanghai_boundary(),
    }
