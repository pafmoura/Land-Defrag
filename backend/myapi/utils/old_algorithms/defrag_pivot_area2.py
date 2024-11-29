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

    def hard_buy_terrain(self, ids_to_filter, gdf):
        for id in ids_to_filter:
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

    def get_clusters(self, gdf):
        def find_neighbors(neighbour, ids, num_cluster):
            neighbors = gdf.loc[gdf["OBJECTID"] == neighbour].iloc[0]["neighbors"]
            ids_neighbors.loc[ids_neighbors["OBJECTID"] == neighbour, "cluster"] = num_cluster
            for neighbor in neighbors:
                if len(ids_neighbors.loc[ids_neighbors["OBJECTID"] == neighbor]) != 0 and ids_neighbors.loc[ids_neighbors["OBJECTID"]  == neighbor].iloc[0]["cluster"] == -1:
                    find_neighbors(neighbor, ids, num_cluster)

        ids_neighbors = gdf.loc[gdf["OWNER_ID"] == self.id].copy()
        ids_neighbors.loc[:, "cluster"] = -1
        ids_neighbors_to_search = ids_neighbors.copy()
        cluster_num = 0

        while len(ids_neighbors_to_search) != 0:
            row = ids_neighbors_to_search.iloc[0]
            ids_neighbors.loc[ids_neighbors["OBJECTID"] == row["OBJECTID"] ,"cluster"] = cluster_num 
            neighbors = row["neighbors"]

            for neighbor in neighbors:
                if len(ids_neighbors.loc[ids_neighbors["OBJECTID"] == neighbor]) != 0 and ids_neighbors.loc[ids_neighbors["OBJECTID"] == neighbor].iloc[0]["cluster"] == -1:
                    find_neighbors(neighbor, ids_neighbors, cluster_num)

            ids_neighbors_to_search = ids_neighbors.loc[ids_neighbors["cluster"] == -1]
            cluster_num += 1

        return ids_neighbors
                        

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
    def calculater_cluster_area(cls, owner_id, cluster_id, gdf):
        return sum(gdf.loc[(gdf["OWNER_ID"] == owner_id) & (gdf["cluster"] == cluster_id)& (gdf["SELL"] == False)]["Shape_Area"])
    
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
    def error_diff(cls, gdf, owners):
        rmsd = 0
        diff_area_owner = []
        for owner in owners:
            area = owner.desired_area - Owner.calculate_area(owner.id, gdf)
            diff_area_owner.append((owner, area))
            rmsd += (area) ** 2

        return np.sqrt(rmsd/len(owners)), diff_area_owner

    @classmethod
    def min_dist(cls, gdf, id, i):
        location = gdf.loc[gdf["OBJECTID"] == id].iloc[0]["geometry"]
        distances = gdf[["OBJECTID", "OWNER_ID"]].copy() 
        distances["distance"] = gdf["geometry"].distance(location)
        distances = distances.sort_values(by="distance").reset_index(drop=True)
        idxs = distances.groupby("OWNER_ID")["distance"].idxmin()
        distances = distances.loc[idxs]
        distances = distances.iloc[:10, :]
        if  i < len(distances):
            return distances.iloc[i]
        else:
            return None

    @classmethod
    def sell_clusters(cls, gdf, owners):
        _rmsd, diff_area_owner = Defrag_Generator.error_diff(gdf, owners)
        diff_area_owner = sorted(diff_area_owner, key=lambda x: x[1])
        new_owners = []
        clusters_to_sell = []
        potential_owners = []
        for owner, area in diff_area_owner:
            if area > 0:
                clusters = owner.get_clusters(gdf)
                best_area = 0
                best_cluster = -1
                for cluster_id in clusters["cluster"].unique():
                    potential_area = Owner.calculater_cluster_area(owner.id, cluster_id, clusters)
                    if np.abs(area - best_area) >= np.abs(area - potential_area):
                        best_area = potential_area
                        best_cluster = cluster_id
                ids_filter = clusters.loc[clusters["cluster"] == best_cluster, "OBJECTID"].values
                area_cluster = sum(gdf.loc[gdf["OBJECTID"].isin(ids_filter)]["Shape_Area"])
                neighbors = gdf.loc[gdf["OBJECTID"].isin(ids_filter)]["neighbors"].values
                clusters_to_sell.append((ids_filter, area_cluster, neighbors))
                new_owners.append(owner)
            elif area < 0:
                potential_owners.append((owner, np.abs(area)))
        
        return new_owners, potential_owners, clusters_to_sell
    
    @classmethod
    def buy_clusters(cls, gdf, new_owners, potential_owners, clusters_to_sell):
        for ids, area, neighbors in clusters_to_sell:
            potential_owners = sorted(potential_owners, key=lambda x: np.abs(area - x[1]))
            sorter_helper = {}
            for i in range(len(potential_owners)):
                sorter_helper[potential_owners[i]] = i
            available_owners = list(set(gdf.loc[gdf["OBJECTID"].isin(neighbors), "OWNER_ID"].values))
            available_owners_sorted = [-1 for _i in potential_owners]
            for owner in potential_owners:
                if owner in available_owners:
                    available_owners_sorted[sorter_helper[owner]] = owner
            available_owners_sorted = list(filter(lambda x: x != -1, available_owners_sorted))
            for owner in available_owners_sorted:
                if owner in potential_owners:
                    owner.hard_buy_terrain(ids, gdf)
            potential_owners.remove(owner)
            new_owners.append(owner)

        return gdf, new_owners

    @classmethod
    def defrag(cls, gdf, add_pivots, limit = -1, patience = 3):
        def is_making_decisions(num_consecutive_aggr, best_consecutive_aggr, gdf, owners):
            limits = [patience + i for i in range(2)]
            if best_consecutive_aggr >= limits[1] :
                return False
            if num_consecutive_aggr >= limits[1]:
                new_owners, potential_owners, clusters_to_sell = Defrag_Generator.sell_clusters(gdf, owners)
                gdf, owners = Defrag_Generator.buy_clusters(gdf, new_owners, potential_owners, clusters_to_sell)
            elif num_consecutive_aggr >= limits[0]:
                reset_gdf()

            return (limit == -1 or i < limit)
        
        def reset_gdf():
            gdf["SELL"] = False
            gdf["locked"] = False

        def init_states():
            gdf["potential_owner"] = min(gdf["OWNER_ID"].unique())
    
        def update_variables(i, past_aggr, aggr_error, best_error):
           return i + 1, aggr_error, ((num_consecutive_aggr + 1) * (past_aggr == aggr_error)), ((best_consecutive_aggr + 1) * (best_error <= aggr_error))
        
        init_states()
        continue_search = True
        best_gdf = gdf.copy()
        i = 0
        tk = Traker()
        owners = Defrag_Generator.create_owners(gdf, tk)
        first_best_aggr = Defrag_Generator.calculate_aggregation_error(gdf)

        while continue_search:
            reset_gdf()
            num_consecutive_aggr = 0
            best_consecutive_aggr = 0
            best_error = first_best_aggr
            past_aggr = best_error
            
            while is_making_decisions(num_consecutive_aggr, best_consecutive_aggr, gdf, owners):
                add_pivots(owners, gdf)
                Defrag_Generator.swap_owners(owners, gdf)

                aggr_error = Defrag_Generator.calculate_aggregation_error(gdf)
                tk.add_error(aggr_error)

                print(f"Iteration: {i} -> Error: {aggr_error}")

                i, past_aggr, num_consecutive_aggr, best_consecutive_aggr = update_variables(i, past_aggr, aggr_error, best_error)
                
                if best_error >= aggr_error:
                    best_gdf = gdf.copy()
                    best_error = aggr_error

            ids = best_gdf.loc[best_gdf["SELL"] == True, "OBJECTID"].values
            for id in ids:
                closest_num = gdf.loc[gdf["OBJECTID"] ==id].iloc[0]["potential_owner"]
                gdf.loc[gdf["OBJECTID"] ==id].iloc[0]["potential_owner"] = closest_num + 1
                row = Defrag_Generator.min_dist(gdf, id, closest_num)
                if row is None:
                    continue_search = False
                    break
                gdf.loc[gdf["OBJECTID"] ==id, "OWNER_ID"] = row["OWNER_ID"]
    
        return best_gdf, tk, owners