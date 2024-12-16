import os
import time
from django.core.files.storage import FileSystemStorage
from myapi.utils.classes.populate_classes import Population_Generator
from myapi.utils.classes.stats import Stats
from myapi.utils.geopandas_wrapper import add_neighbours, save_file


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


def defrag_save(gdf, defrag_function, defrag_file_name, new_defrag):
    start_time = time.time()
    gdf_new, tk, owners, uses_owners =  defrag_function(gdf=gdf)
    time_elapsed = time.time() - start_time
    print("Elapsed time:", time_elapsed)
    save_file(gdf_new, defrag_file_name)

    stats = Stats.get_json(gdf_new, owners, is_using_class_Onwer=uses_owners)
    fs = FileSystemStorage()
    file_path = fs.path(defrag_file_name)
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    Stats.save(stats, file_path+ ".json")

    new_defrag.is_completed = True

    new_defrag.save()



