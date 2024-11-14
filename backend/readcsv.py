import geopandas as gpd
import numpy as np
import random
import matplotlib.pyplot as plt

caminho_gpkg = "Madeira.gpkg"
gdf = gpd.read_file(caminho_gpkg, layer="Parcelas_RAM")
print(gdf.columns)


class Parcel:
    def __init__(self, objectid, par_id, par_num, shape_length, shape_area, geometry):
        self.objectid = objectid
        self.par_id = par_id
        self.par_num = par_num
        self.shape_length = shape_length
        self.shape_area = shape_area
        self.geometry = geometry
        self.neighbors = []
        self.owner_id = None


data = {
    "objectid": [],
    "par_id": [],
    "par_num": [],
    "shape_length": [],
    "shape_area": [],
    "geometry": [],
}

for _, row in gdf.iterrows():
    data["objectid"].append(row["OBJECTID"])
    data["par_id"].append(row["PAR_ID"])
    data["par_num"].append(row["PAR_NUM"])
    data["shape_length"].append(row["Shape_Length"])
    data["shape_area"].append(row["Shape_Area"])
    data["geometry"].append(row["geometry"])

gdf_parcels = gpd.GeoDataFrame(data, geometry="geometry")
gdf_parcels.crs = gdf.crs

num_parcelas = len(gdf_parcels)
num_proprietarios = (
    num_parcelas // 8
)  # méd de 8 propriedades por proprietário. Encontrei numa tese random

owner_ids = list(range(num_proprietarios))

random.shuffle(owner_ids)

owner_assignment = []

for i in range(num_parcelas):
    owner_id = owner_ids[i % num_proprietarios]
    owner_assignment.append(owner_id)

gdf_parcels["owner_id"] = owner_assignment

# Encontrar vizinhos
intersections = gpd.sjoin(gdf_parcels, gdf_parcels, how="inner", predicate="intersects")
print(intersections.columns)

neighbors_dict = {row.objectid_left: [] for row in intersections.itertuples()}

for row in intersections.itertuples():
    left_id = row.objectid_left
    right_id = row.objectid_right
    if left_id != right_id:
        neighbors_dict[left_id].append(right_id)

gdf_parcels["neighbors"] = gdf_parcels["objectid"].map(neighbors_dict)

for parcel in gdf_parcels.itertuples():
    print(
        f"Parcela: {parcel.objectid}, Vizinhos: {parcel.neighbors}, Proprietário: {parcel.owner_id}"
    )


def calculate_aggregation(gdf):
    aggregations = {}
    for owner_id in gdf["owner_id"].unique():
        parcels = gdf[gdf["owner_id"] == owner_id]
        total_area = parcels["shape_area"].sum()

        neighbor_count = (parcels["neighbors"].apply(lambda x: (len(
                        [
                            n
                            for n in x
                            if gdf.loc[gdf["objectid"] == n, "owner_id"].values[0]
                            == owner_id
                        ]
                    )
                    if isinstance(x, list)
                    else 0
                )
            )
            .sum()
        )

        aggregations[owner_id] = total_area + neighbor_count

    return aggregations


# agregacao_resultados = calculate_aggregation(gdf_parcels)

# sort por agregacao
# sorted_agregacao = sorted(agregacao_resultados.items(), key=lambda x: x[1], reverse=True)
# for owner_id, agregacao in sorted_agregacao:
#  print(f'Proprietário: {owner_id}, Agregação: {agregacao}')


def plot_parcels(gdf):
    gdf.plot(column="owner_id", cmap="viridis", edgecolor="black", legend=True)
    plt.title("Parcelas por owner")
    plt.xlabel("Longitude")
    plt.ylabel("Latitude")
    plt.show()


plot_parcels(gdf_parcels)
