import geopandas as gpd


def add_neighbours(gdf):
    intersections = gpd.sjoin(gdf, gdf)
    neighbors_dict = {row.OBJECTID_left: [] for row in intersections.itertuples()}

    for row in intersections.itertuples():
        if row.OBJECTID_left != row.OBJECTID_right:
            neighbors_dict[row.OBJECTID_left].append(row.OBJECTID_right)

    gdf["neighbors"] = gdf["OBJECTID"].map(neighbors_dict)
