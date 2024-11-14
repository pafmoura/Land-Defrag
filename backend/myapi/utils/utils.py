from myapi.utils.classes.populate_classes import Population_Generator
from myapi.utils.geopandas_wrapper import add_neighbours


def preprocess_geopandas(gdf, name, owners_average_land):
    functional_gdf = gdf.copy()
    functional_gdf = functional_gdf.loc[~functional_gdf["geometry"].is_empty]


    generator = Population_Generator.create_generator(
        name=name,
        num_rows_geopandas=len(functional_gdf),
        owners_average_land=owners_average_land,
    )

    functional_gdf["OWNER_ID"] = generator.populate()

    add_neighbours(functional_gdf)

    return functional_gdf