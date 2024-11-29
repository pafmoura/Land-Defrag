from myapi.utils.old_algorithms.defrag_pivot_area import Owner
import numpy as np


class Stats:
    def __init__(self):
        pass

    @classmethod
    def error_diff_with_Owner_class(cls, gdf, owners):
        rmsd = 0
        diff_area_owner = []
        for owner in owners:
            area = owner.desired_area - Owner.calculate_area(owner.id, gdf)
            diff_area_owner.append((owner, area))
            rmsd += (area) ** 2

        return np.sqrt(rmsd/len(owners)), diff_area_owner
    
    @classmethod
    def error_diff_with_redistribution(cls, gdf, initial_areas):
        # TODO
        rmsd = 0
        diff_area_owner = []
        for key in initial_areas:
            area = initial_areas[key] - Owner.calculate_area(key, gdf)
            diff_area_owner.append((key, area))
            rmsd += (area) ** 2

        return np.sqrt(rmsd/len(initial_areas)), initial_areas

    @classmethod
    def calculate_aggregation_error(cls, gdf):
        def flatten_unique_neighbors(pairs):
            neighbors = [item[1] for item in pairs]
            result = []
            for sub_neighbours in neighbors:
                for neighbour in sub_neighbours:
                    result.append(neighbour)
            
            result = list(set(result))
            return result

        owners = gdf["OWNER_ID"].unique()
        num_penalties = 0

        for owner in owners:
            pairs = gdf.loc[gdf["OWNER_ID"] == owner, ["OBJECTID", "neighbors"]].values
            ids = []
            for pair in pairs:
                if len(pair[1]) != 0:
                    ids.append(pair[0])
            neighbors = flatten_unique_neighbors(pairs)
            
            for id in ids:
                if id not in neighbors:
                    num_penalties += 1

        return num_penalties / len(gdf)
    
    @classmethod
    def get_json(cls, gdf, initial_areas, is_using_class_Onwer = False):

        if is_using_class_Onwer:
            error_diff, diff_areas = Stats.error_diff_with_Owner_class(gdf, initial_areas)
        else:
            error_diff, diff_areas = Stats.error_diff_with_Owner_class(gdf, initial_areas)

        aggregation_error = Stats.calculate_aggregation_error(gdf)

        return {"error_diff": error_diff, "diff_areas": diff_areas, "aggregation_error": aggregation_error}
    
    @classmethod
    def save(cls, json, file_path):
        with open(file_path, "w") as f:
            f.write(str(json))
