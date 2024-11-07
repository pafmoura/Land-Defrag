from backend import settings
import geopandas as gpd
from django.core.files.storage import FileSystemStorage


def read_geopandas(file_name):
    fs = FileSystemStorage()
    return gpd.read_file(
        f"{settings.MEDIA_ROOT}{fs.url(file_name)}", layer="layer"
    )


def add_neighbours(gdf):
    intersections = gpd.sjoin(gdf, gdf)
    neighbors_dict = {row.OBJECTID_left: [] for row in intersections.itertuples()}

    for row in intersections.itertuples():
        if row.OBJECTID_left != row.OBJECTID_right:
            neighbors_dict[row.OBJECTID_left].append(row.OBJECTID_right)

    gdf["neighbors"] = gdf["OBJECTID"].map(neighbors_dict)
