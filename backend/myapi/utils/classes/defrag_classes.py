import numpy as np
# Melhor

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
        
    
class Owner:
    owners = {}
    tracker = None

    def __init__(self, id, area, tracker):
        self.id = id
        self.desired_area = area
        self.pivot = None
        self.tracker = tracker

    def set_pivot(self, pivot):
        self.pivot = pivot

    def get_terrains(self, gdf):
        return gdf.loc[gdf["OWNER_ID"] == self.id]
    
    def get_neighbors(self, gdf):
        row = gdf.loc[gdf["OBJECTID"] == self.pivot].iloc[0]
        neighbors = []
        
        for neighbor in row["neighbors"]:
            if gdf.loc[gdf["OBJECTID"] == neighbor].iloc[0]["locked"] == False:
                neighbors.append(neighbor)
        
        if len(neighbors) != 0:
            return neighbors
        
        non_locked = gdf.loc[gdf["locked"] == False]
        non_locked = non_locked.reset_index(drop=True)

        return [non_locked.iloc[non_locked["geometry"].distance(row["geometry"]).idxmin()]["OBJECTID"]]
    
    def sell_unlocked_terrains(self, gdf):
        gdf.loc[(gdf["OWNER_ID"] == self.id) & (gdf["locked"] == False), "SELL"] = True


    def swap(self, new_id, gdf):
        owner_id = gdf.loc[gdf["OBJECTID"] == new_id, "OWNER_ID"].iloc[0]
        gdf.loc[gdf["OBJECTID"] == new_id, "OWNER_ID"] = self.id
        neighbors = Owner.owners[owner_id].get_neighbors(gdf)
        availables = gdf.loc[(gdf["OWNER_ID"] == self.id) & ((gdf["SELL"] == True) | (gdf["locked"] == False)), "OBJECTID"].values
        index = None
        for i in range(len(availables)):
            if availables[i] in neighbors:
                index = i
        if index is not None:
            gdf.loc[gdf["OBJECTID"] == (gdf.loc[(gdf["OWNER_ID"] == self.id) & ((gdf["SELL"] == True) | (gdf["locked"] == False)), "OBJECTID"].iloc[index]), "OWNER_ID"] = owner_id


    def filter_areas(self, ids_to_filter, area, gdf):
        ids_areas = gdf.loc[gdf["OBJECTID"].isin(ids_to_filter), ["OBJECTID", "Shape_Area"]].values
        combination, sum_approximation = Owner.closest_sum(ids_areas, area)
        ids = [item[0] for item in combination]
        gdf.loc[gdf["OBJECTID"].isin(ids), "SELL"] = True

    def buy_terrain(self, ids_to_filter, area, gdf):
        ids_areas = gdf.loc[(gdf["OBJECTID"].isin(ids_to_filter)) & (gdf["SELL"] == True), ["OBJECTID", "Shape_Area"]].values
        combination, sum_approximation = Owner.closest_sum(ids_areas, area)
        ids = [item[0] for item in combination]
        for id in ids:
            self.swap(id, gdf)
    
    def get_border_ids(self, gdf):
        ids_neighbors = gdf.loc[gdf["OWNER_ID"] == self.id, ["OBJECTID", "neighbors"]] 
        filtered = []
        neighbors_list = []
        for i in range(len(ids_neighbors)):
            row = ids_neighbors.iloc[i] 
            neighbors = row["neighbors"]
            for neighbor in neighbors:
                if gdf.loc[gdf["OBJECTID"] == neighbor].iloc[0]["OWNER_ID"] != self.id:
                    filtered.append(row["OBJECTID"])
                    neighbors_list.append(neighbor)
            if len(neighbors) == 0:
                filtered.append(row["OBJECTID"])
        return list(set(filtered)), neighbors_list

    @classmethod
    def create_owner(cls, id, area, tracker):
        if cls.tracker is None:
            cls.tracker = tracker
        
        owner = Owner(id, area, tracker)
        cls.owners[id] = owner

        return owner

    @classmethod
    def calculate_area(cls, owner_id, gdf):
        return sum(gdf.loc[gdf["OWNER_ID"] == owner_id]["Shape_Area"])

    @classmethod
    def calculate_locked_area(cls, owner_id, gdf):
        return sum(gdf.loc[(gdf["OWNER_ID"] == owner_id) & (gdf["locked"] == True) & (gdf["SELL"] == False)]["Shape_Area"])
    
    @classmethod
    def get_owner(cls, id1):
        return cls.owners[id1]

    @classmethod
    def closest_sum(cls, values, target):
        closest_combination = []
        closest_sum = float('inf')

        def backtrack(start, current_combination, current_sum):
            nonlocal closest_combination, closest_sum

            if abs(target - current_sum) < abs(target - closest_sum):
                closest_combination = current_combination[:]
                closest_sum = current_sum

            if current_sum >= target:
                return

            for i in range(start, len(values)):
                current_combination.append(values[i])
                backtrack(i + 1, current_combination, current_sum + values[i][1])
                current_combination.pop()

        backtrack(0, [], 0)
        return closest_combination, closest_sum    


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
            owner = Owner.create_owner(owner_id, Owner.calculate_area(owner_id, gdf), tk)
            owners.append(owner)

        return owners
    
    @classmethod
    def add_pivots_by_area(cls, owners, gdf):        
        def calculate_area(index, terrenos):
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
            terrains = terrains.reset_index(drop=True)
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
                gdf.loc[gdf["OBJECTID"] == owner.pivot, "locked"] = True      

    @classmethod
    def get_heuristic_and_action(cls, gdf, new_id):
        new_row = gdf.loc[gdf["OBJECTID"] == new_id].iloc[0]
        owner = Owner.get_owner(new_row["OWNER_ID"])
        new_area = owner.desired_area - (Owner.calculate_locked_area(owner.id, gdf) + new_row["Shape_Area"])
        return new_area, new_id
    
    @classmethod
    def swap_owners(cls, owners, gdf):
        owners_neighbors = []
        for owner in owners:
            owners_neighbors.append((owner, owner.get_neighbors(gdf)))
        
        owners_neighbors = sorted(owners_neighbors, key=lambda x: len(x[1]))
        
        for owner_neighbors in owners_neighbors:
            owner, neighbors = owner_neighbors
            neighbors_actions = [Defrag_Generator.get_heuristic_and_action(gdf, neighbor) for neighbor in neighbors]
            neighbors_actions = sorted(neighbors_actions, key=lambda x: np.abs(x[0]))
            area, neighbor = neighbors_actions[0]
            owner.swap(neighbor, gdf)

            ids_filter, neighbors_filter = owner.get_border_ids(gdf)

            if area == 0:
                gdf.loc[gdf["OBJECTID"] == neighbor, "locked"] = True
                owner.sell_unlocked_terrains(gdf)
            
            elif area < 0:
                owner.filter_areas(ids_filter, np.abs(area), gdf)
            else:
                owner.buy_terrain(neighbors_filter, np.abs(area), gdf)


    @classmethod
    def defrag(cls, gdf, add_pivots, limit = -1, reset = False, patience = 3):
        def continue_search():
            if limit == -1:
                return num_locked != len(gdf)
            return i < limit and num_locked != len(gdf)


        def set_reset(num_consecutive_filters):
            reset = True
            if num_consecutive_filters < (patience + 4) :
                reset = False

            if reset:
                gdf["SELL"] = False
                gdf["locked"] = False
        
        set_reset(reset * (patience + 4))
        num_locked = 0
        tk = Traker()
        owners = Defrag_Generator.create_owners(gdf, tk)
        past = [Defrag_Generator.calculate_aggregation_error(gdf)]
        i = 0
        num_consecutive_filters = 0

        while continue_search():
            add_pivots(owners, gdf)
            Defrag_Generator.swap_owners(owners, gdf)

            aggr_error = Defrag_Generator.calculate_aggregation_error(gdf)
            set_reset(num_consecutive_filters)

            tk.add_error(aggr_error)
            print(f"Iteration: {i} -> Error: {aggr_error}")
            num_locked = len(gdf.loc[gdf["locked"] == True, "OBJECTID"])
            if i % 500 == 0:
                print("Locked:", num_locked)
            i += 1
        return gdf, tk, owners, True