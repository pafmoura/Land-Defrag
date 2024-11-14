import ast
import os
from backend import settings
import geopandas as gpd
from django.core.files.storage import FileSystemStorage


def read_geopandas(file_name, file = None):
    fs = FileSystemStorage()
    file_path = fs.path(file_name)
    if file is not None:
        return gpd.read_file(file)

    return gpd.read_file(file_path)

def convert_types(gdf):
    gdf['neighbors'] = gdf['neighbors'].apply(lambda x: [int(i) for i in ast.literal_eval(x)])

def check_geopackage_status(file_name):
    fs = FileSystemStorage()
    file_path = fs.path(file_name)
    return fs.exists(file_path)


def add_neighbours(gdf):
    intersections = gpd.sjoin(gdf, gdf)
    neighbors_dict = {row.OBJECTID_left: [] for row in intersections.itertuples()}

    for row in intersections.itertuples():
        if row.OBJECTID_left != row.OBJECTID_right:
            neighbors_dict[row.OBJECTID_left].append(row.OBJECTID_right)

    gdf["neighbors"] = gdf["OBJECTID"].map(neighbors_dict)

def save_file(gdf, generated_file_name):
    fs = FileSystemStorage()
    file_path = fs.path(generated_file_name)

    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    
    gdf.to_file(file_path, driver="GPKG")