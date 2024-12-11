import numpy as np
# PODRE
class Swap:
    def __init__(self, id1, id2, owner1, owner2):
        self.id1 = id1
        self.id2 = id2
        self.owner1 = owner1
        self.owner2 = owner2

class Traker:
    def __init__(self):
        self.swaps = []
        self.errors = []
    
    def add_swap(self, swap):
        self.swaps.append(swap)

    def get_swaps(self):
        return self.swaps
    
    def add_error(self, error):
        self.errors.append(error)

    def cancel_swap(self, previous):
        del self.swaps[-previous:]
        del self.errors[-previous:]
        
    
class Owner:    
    def __init__(self, id, area, tracker):
        self.id = id
        self.desired_area = area
        self.pivot = None
        self.tracker = tracker

    def set_pivot(self, pivot):
        self.pivot = pivot

    def swap_terrain(self, id1, id2, owner, gdf):
        self.tracker.add_swap(Swap(id1, id2, owner, self))
        gdf.loc[gdf["OBJECTID"] == id1, "OWNER_ID"] = owner.id
        gdf.loc[gdf["OBJECTID"] == id2, "OWNER_ID"] = self.id

    def get_terrains(self, gdf):
        return gdf.loc[gdf["OWNER_ID"] == self.id]
    
    @classmethod
    def cancel_swap(cls, id1, id2, owners, gdf):
        Owner.swap_ids(id1,  id2, owners, gdf)
        owners[0].tracker.cancel_swap(2)

    @classmethod
    def calculate_area(cls, owner_id, gdf):
        return sum(gdf.loc[gdf["OWNER_ID"] == owner_id]["Shape_Area"])
    
    @classmethod
    def get_owners(cls, id1, id2, owners, gdf):
        owner_id1 = gdf.loc[gdf["OBJECTID"] == id1, "OWNER_ID"].iloc[0]
        owner_id2 = gdf.loc[gdf["OBJECTID"] == id2, "OWNER_ID"].iloc[0]
        owner1 = None
        owner2 = None
        for owner in owners:
            if owner.id == owner_id1:
                owner1 = owner
            if owner.id == owner_id2:
                owner2 = owner
        return owner1, owner2

    @classmethod
    def swap_ids(cls, id1, id2, owners, gdf):
        owner1, owner2 = Owner.get_owners(id1, id2, owners, gdf)
        if owner1 == None or owner2 == None:
            return False
        
        owner1.swap_terrain(id1, id2, owner2, gdf)
        return True

class Defrag_Generator:

    def __init__(self):
        pass
    
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
            ids = [item[0] for item in pairs]
            neighbors = flatten_unique_neighbors(pairs)
             
            for id in ids:
                if id not in neighbors:
                    num_penalties += 1

        return num_penalties / len(gdf)

    @classmethod
    def base_aggregation_error(cls, gdf):
        test = gdf.copy()
        test["OWNER_ID"] = 0
        return Defrag_Generator.calculate_aggregation_error(test)
    
    @classmethod
    def create_owners(cls, gdf, tk):
        owners_id = gdf["OWNER_ID"].unique()
        owners = []

        for owner_id in owners_id:
            owner = Owner(owner_id, Owner.calculate_area(owner_id, gdf), tk)
            owners.append(owner)

        return owners
    
    @classmethod
    def add_pivots_by_area(cls, owners, gdf):        
        def calculate_area(index, terrains):
            terrenos = terrains.reset_index(drop=True)
            indexes = [index]
            row = terrenos.iloc[index]
            owner_id = row["OWNER_ID"]
            neighbors = row["neighbors"]
            acc = row["Shape_Area"]
            
            
            while len(neighbors) > 0:
                new_neighbors = []
                for neighbor in neighbors:
                    row = terrenos.loc[terrenos["OBJECTID"] == neighbor]
                    if len(row) == 0 or row["OWNER_ID"].iloc[0] != owner_id or neighbor in visited:
                        continue
                    row = row.iloc[0]
                    indexes.append(terrenos.index[terrenos["OBJECTID"] == neighbor][0])
                    acc += row["Shape_Area"]
                    temp = row["neighbors"]
                    for value in temp:
                        new_neighbors.append(value)
                    visited.append(neighbor)
                neighbors = new_neighbors

            return acc, indexes
        visited = []
        for owner in owners:
            terrains = owner.get_terrains(gdf)
            areas = [0 for i in range(len(terrains))]
            for i in range(len(terrains)):
                row = terrains.iloc[i]
                if row["locked"]:
                    continue
                area, indexes = calculate_area(i, terrains)
                for index in indexes:
                    areas[index] = area

            if len(areas) != 0:
                owner.set_pivot(terrains.iloc[np.argmax(areas)]["OBJECTID"])   
        

    @classmethod
    def add_pivots_by_distance(cls, owners, gdf):
        for owner in owners:
            terrains = owner.get_terrains(gdf)
            distances = []
            for i in range(len(terrains)):
                row = terrains.iloc[i]
                if row["locked"]:
                    continue
                distances.append(terrains["geometry"].distance(row["geometry"]))
           
            loss_by_terrain = []
            for i in range(len(distances)):
                loss_by_terrain.append(distances[i].mean())

            if len(loss_by_terrain) != 0:
                owner.set_pivot(terrains.iloc[np.argmin(loss_by_terrain)]["OBJECTID"])            

    @classmethod
    def get_heuristic(cls, gdf, owners, current_id, new_id):
        ser_current = gdf.loc[gdf["OBJECTID"] == current_id].iloc[0]
        ser_new = gdf.loc[gdf["OBJECTID"] == new_id].iloc[0]
        diff_areas = np.abs(ser_current["Shape_Area"] - ser_new["Shape_Area"])
        owner1, owner2 = Owner.get_owners(ser_current["OBJECTID"], ser_new["OBJECTID"], owners, gdf)
        if owner1 == None or owner2 == None:
            return float("inf")
        penalise = new_id in gdf.loc[gdf["OBJECTID"] == owner1.pivot]["neighbors"]
        reward = new_id in gdf.loc[gdf["OBJECTID"] == owner2.pivot]["neighbors"]
        return diff_areas + penalise * diff_areas - reward * diff_areas
    
    @classmethod
    def get_heuristics(cls, gdf, current_list, owners):
        smallest = []
        current_list = [i for item in current_list for i in item]
        
        for i in range(len(current_list) - 1):
            dists = []
            for j in range(i + 1, len(current_list)):
                dists.append(Defrag_Generator.get_heuristic(gdf, owners, current_list[i], current_list[j]))
            
            smallest.append((i, dists.index(min(dists)), min(dists)))

        
        smallest = sorted(smallest, key=lambda x: x[2])
        clean = []
        skips = []
        for i in range(len(smallest)):
            if i in skips:
                continue
            index1, index2, heuristic = smallest[i]
            clean.append((current_list[index1], current_list[index2], heuristic))
            for j in range(i + 1, len(smallest)):
                indexskip1, indexskip2, _heuristic = smallest[j]
                if indexskip1 == index1 or indexskip1 == index2 or indexskip2 == index1 or indexskip2 == index2:
                    skips.append(j)

        return clean

    @classmethod
    def get_neighbours(cls, gdf, current_list):
        neighbors = []
        for id in current_list:
            neighbors.append(gdf.loc[gdf["OBJECTID"] == id]["neighbors"].iloc[0])
        return neighbors


    @classmethod
    def defrag(cls, gdf, add_pivots, patience = None, current_list = [], limit = -1):
        def continue_search():
            if limit == -1:
                return reset > 0 and num_locked != len(gdf)
            return i < limit and reset > 0 and num_locked != len(gdf)

        def update_variables(current_list):
            add_pivots(owners, gdf)
            to_remove = gdf.loc[gdf["locked"] == True, "OBJECTID"].values
            for i in to_remove:
                if i in current_list:
                    current_list.remove(i)

            for owner in owners:
                gdf.loc[gdf["OBJECTID"] == owner.pivot, "locked"] = True
                current_list.append(owner.pivot)
   

            return Defrag_Generator.get_heuristics(gdf, Defrag_Generator.get_neighbours(gdf, current_list), owners)

        num_locked = 0
        gdf["locked"] = False
        patience = patience if patience is not None else len(gdf) // 2
        reset = patience
        tk = Traker()
        owners = Defrag_Generator.create_owners(gdf, tk)
        past = Defrag_Generator.calculate_aggregation_error(gdf)
        
        heuristics = update_variables(current_list)
        i = 0
        while continue_search():
            if len(heuristics) == 0:
                heuristics = update_variables(current_list)

            id1, id2, heuristic = heuristics.pop(0)
            Owner.swap_ids(id1, id2, owners, gdf)

            aggr_error = Defrag_Generator.calculate_aggregation_error(gdf)
            tk.add_error(aggr_error)
            if aggr_error > past:
                Owner.cancel_swap(id1, id2, owners, gdf)
                
            if aggr_error == past:
                reset -= 1                    
            else:
                reset = patience
            past = aggr_error
            print(f"Iteration: {i} -> Error: {aggr_error}")
            num_locked = len(gdf.loc[gdf["locked"] == True, "OBJECTID"])
            if i % 500 == 0:
                print("Locked:", num_locked)
            i += 1
        return gdf, tk, current_list, True

    def create_and_defrag(cls, algorithm_name, gdf):
        match algorithm_name:
            case "by_area":
                return Defrag_Generator.defrag(gdf, Defrag_Generator.add_pivots_by_area, patience = None, current_list = [], limit = -1)
            case "by_distance":
                return Defrag_Generator.defrag(gdf, Defrag_Generator.add_pivots_by_distance, patience = None, current_list = [], limit = -1)
            
