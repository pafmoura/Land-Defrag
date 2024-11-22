from myapi.utils.classes.defrag_classes import Defrag_Generator, Traker

class Redistribute:

    OBJECTID='OBJECTID'

    @classmethod
    def calculate_initial_areas(cls, gdf):
    
        initial_areas = {}
        for owner_id in gdf["OWNER_ID"].unique():
            initial_areas[owner_id] = gdf.loc[gdf["OWNER_ID"] == owner_id, "Shape_Area"].sum()
        return initial_areas

    @classmethod
    def find_available_terrains(cls, owner_id, visited_terrains, gdf):

        current_terrains = gdf.loc[gdf["OWNER_ID"] == owner_id, cls.OBJECTID].values

        if current_terrains.size == 0:
            # fica com o primeiro vazio disponível
            current_terrains = gdf.loc[gdf["OWNER_ID"].isnull(), cls.OBJECTID].values

        neighbors = set()

        for terrain_id in current_terrains:
            if terrain_id in visited_terrains:
                continue
            neighbors.update(gdf.loc[gdf[cls.OBJECTID] == terrain_id, "neighbors"].values[0])

        available_terrains = [
            t for t in neighbors
            if t not in visited_terrains and gdf.loc[gdf[cls.OBJECTID] == t, "OWNER_ID"].isnull().values[0]
        ]

        return available_terrains

    @classmethod
    def adjust_terrain(cls, owner_id, candidate_ids, area_change, gdf):
    

        if area_change > 0:
            # compra até ter a área suficiente
            for candidate_id in candidate_ids:
                candidate_area = gdf.loc[gdf[cls.OBJECTID] == candidate_id, "Shape_Area"].sum()
                if candidate_area <= 0:
                    continue

                gdf.loc[gdf[cls.OBJECTID] == candidate_id, "OWNER_ID"] = owner_id
                area_change -= candidate_area

                if area_change <= 0:
                    break  # atingiu área suficiente

        elif area_change < 0:
            # vende terrenos para atingir a area suficiente
            owned_ids = gdf.loc[gdf["OWNER_ID"] == owner_id, cls.OBJECTID].values
            for terrain_id in owned_ids:
                terrain_area = gdf.loc[gdf[cls.OBJECTID] == terrain_id, "Shape_Area"].values[0]
                if terrain_area <= 0:
                    continue

                # remove o terreno do proprietario
                gdf.loc[gdf[cls.OBJECTID] == terrain_id, "OWNER_ID"] = None
                area_change += terrain_area

                if area_change >= 0:
                    break  #atingiu area suficiente

    @classmethod
    def redistribute_areas(cls, gdf, initial_areas, tracker, threshold=50000):
        for owner_id, target_area in initial_areas.items():
            current_area = gdf.loc[gdf["OWNER_ID"] == owner_id, "Shape_Area"].sum()
            difference = target_area - current_area

            if abs(difference) <= threshold:
                continue  # dentro do limite

            if difference > 0:
                cls.buy_terrains(owner_id, difference, initial_areas, gdf, threshold)  
            elif difference < 0:
                cls.sell_terrains(owner_id, -difference, initial_areas, gdf, threshold)  

            
    @classmethod
    def buy_terrains(cls, owner_id, area_needed, initial_areas, gdf, threshold):
        visited_terrains = set()  # terrenos ja visitados

        while area_needed > 0:
            candidate_ids = cls.find_available_terrains(owner_id, visited_terrains, gdf)
            
            if not candidate_ids:
                candidate_ids = gdf.loc[gdf["OWNER_ID"].isnull(), cls.OBJECTID].values
                break

            cls.adjust_terrain(owner_id, candidate_ids, area_needed, gdf)
            
            current_area = gdf.loc[gdf["OWNER_ID"] == owner_id, "Shape_Area"].sum()
            area_needed = initial_areas[owner_id] - current_area
            
            # limite da diferenca
            if abs(area_needed) <= threshold:
                break  # atingiu limite, para

    @classmethod
    def sell_terrains(cls, owner_id, area_needed, initial_areas, gdf, threshold):
        print("está na venda")
        owned_ids = gdf.loc[gdf["OWNER_ID"] == owner_id, cls.OBJECTID].values
        while area_needed > 0:
            for terrain_id in owned_ids:
                terrain_area = gdf.loc[gdf[cls.OBJECTID] == terrain_id, "Shape_Area"].values[0]
                if terrain_area <= 0:
                    continue

                gdf.loc[gdf[cls.OBJECTID] == terrain_id, "OWNER_ID"] = None
                area_needed -= terrain_area

                if area_needed <= 0:
                    break  # atingiu o limite, nao vende

        if abs(area_needed) <= threshold:
            return  # atingiu o limite do treshold            



    @classmethod
    def redistribute(cls, gdf, tracker=None, limit=100, threshold=70000, **kwargs):
    
        if tracker is None:
            tracker = Traker()  

        initial_areas = cls.calculate_initial_areas(gdf)

        for owner_id, area in initial_areas.items():
            print(f"{owner_id} : {area}")

        
        gdf["OWNER_ID"] = None

        #DAR SORT NA LISTA POR MAIORES AREAS
        initial_areas = dict(sorted(initial_areas.items(), key=lambda item: item[1], reverse=True))


     
        cls.redistribute_areas(gdf, initial_areas, tracker, threshold)
        
        max_difference = max(
            abs(initial_areas[owner] - gdf.loc[gdf["OWNER_ID"] == owner, "Shape_Area"].sum())
            for owner in initial_areas
        )
        print(f"Máxima diferença de área = {max_difference}")
        aggregation_error = Defrag_Generator.calculate_aggregation_error(gdf)
        print(f"Erro de agregação = {aggregation_error}")
        print(f"Terrenos por atibuir: {len(gdf.loc[gdf['OWNER_ID'].isnull()])}")


        


        # TERRENOS QUE AINDA NAO FORAM ALOCADOS
        unassigned_terrains = gdf[gdf["OWNER_ID"].isnull()]
        if not unassigned_terrains.empty:
            print(f"terrenos não alocados: {len(unassigned_terrains)}")

            # owners abaixo da meta, reodernar
            owners_below_target = [
                owner_id for owner_id, target_area in initial_areas.items()
                if gdf.loc[gdf["OWNER_ID"] == owner_id, "Shape_Area"].sum() < target_area
            ]
            owners_below_target.sort(
                key=lambda x: initial_areas[x] - gdf.loc[gdf["OWNER_ID"] == x, "Shape_Area"].sum(), 
                reverse=True
            )

            for idx, terrain in unassigned_terrains.iterrows():
                available_owner = None
                for owner_id in owners_below_target:
                    current_area = gdf.loc[gdf["OWNER_ID"] == owner_id, "Shape_Area"].sum()
                    target_area = initial_areas[owner_id]
                    
                    if current_area < target_area:
                        available_owner = owner_id
                        break

                if available_owner:
                    visited_terrains = set(gdf[gdf["OWNER_ID"] == available_owner][cls.OBJECTID].values)
                    candidate_ids = cls.find_available_terrains(available_owner, visited_terrains, gdf)
                    
                    if candidate_ids:
                        cls.adjust_terrain(available_owner, candidate_ids, target_area - current_area, gdf)
                        gdf.at[idx, "OWNER_ID"] = available_owner
                        print(f"Atribuído terreno {terrain[cls.OBJECTID]} -> {available_owner}")

                    else:
                        # atribui terreno random livre
                        candidate_ids = gdf.loc[gdf["OWNER_ID"].isnull(), cls.OBJECTID].values
                        cls.adjust_terrain(available_owner, candidate_ids, target_area - current_area, gdf)
                        gdf.at[idx, "OWNER_ID"] = available_owner
                        print(f"Atribuído terreno {terrain[cls.OBJECTID]} -> {available_owner}")

        
        final_max_difference = max(
            initial_areas[owner] - gdf.loc[gdf["OWNER_ID"] == owner, "Shape_Area"].sum()
            for owner in initial_areas
        )
        final_agg_error = Defrag_Generator.calculate_aggregation_error(gdf)
        print(f"Erro de agregação final = {final_agg_error}")
        print(f"Diferença máxima final = {final_max_difference}")
        
        initial_areas = dict(sorted(initial_areas.items(), key=lambda item: item[1], reverse=True))
        

        

        for owner_id, area in initial_areas.items():
            final_area = gdf.loc[gdf["OWNER_ID"] == owner_id, "Shape_Area"].sum()
            print(f"Proprietário {owner_id}: Diferença de área = {area - final_area}")

        print(f"Erro de agregação final = {final_agg_error}")
        print(f"Diferença máxima final = {final_max_difference}")
        

        return gdf, tracker, list(gdf["OWNER_ID"].unique())
