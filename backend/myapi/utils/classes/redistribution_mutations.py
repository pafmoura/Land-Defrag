import random
import numpy as np
import pandas as pd
from myapi.utils.classes.redistribution_defrag import Redistribute
from myapi.utils.classes.defrag_classes import Defrag_Generator
from myapi.utils.classes.stats import Stats

class MutationalRedistribute(Redistribute):
    @classmethod
    def calculate_cost(cls, gdf, initial_areas, alpha=0.6, beta=0.4):
        aggregation_error = Defrag_Generator.calculate_aggregation_error(gdf)
        
        rmse, _ = Stats.error_diff_with_redistribution(gdf, initial_areas)
        
        max_area = sum(initial_areas.values())  
        normalized_rmse = rmse / max_area if max_area > 0 else 0
        
        return alpha * aggregation_error + beta * normalized_rmse


    @classmethod
    def mutate(cls, gdf, initial_areas, beam_width=4):

        original_cost = cls.calculate_cost(gdf, initial_areas)
        best_states = [(gdf.copy(), original_cost)]
        
        for _ in range(beam_width):
            new_states = []
            for state, current_cost in best_states:
                candidates = []
                
                # mutação de troca (uma por uma)
                mutated_swap = state.copy()
                cls.swap_mutation(mutated_swap, initial_areas)
                swap_cost = cls.calculate_cost(mutated_swap, initial_areas)
                candidates.append((mutated_swap, swap_cost))
                

                # mutação de múltiplas trocas
                mutated_mult = state.copy()
                cls.multiple_swap_mutation(mutated_mult, initial_areas)
                mult_cost = cls.calculate_cost(mutated_mult, initial_areas)
                candidates.append((mutated_mult, mult_cost))

                # mutação de expansão de cluster
                mutated_cluster = state.copy()
                cls.cluster_expansion_mutation(mutated_cluster, initial_areas)
                cluster_cost = cls.calculate_cost(mutated_cluster, initial_areas)
                candidates.append((mutated_cluster, cluster_cost))

                
                # escolhe a melhor
                best_candidate = min(candidates, key=lambda x: x[1])
                if best_candidate[1] <= current_cost * 1.05:  # aumento custo... previnir minimo local 
                    new_states.append(best_candidate)
            
            if new_states:
                best_states = sorted(new_states, key=lambda x: x[1])[:beam_width]
            
        return min(best_states, key=lambda x: x[1])[0]


    @classmethod
    def cluster_expansion_mutation(cls, gdf, initial_areas):

        owned_terrains = gdf[gdf["OWNER_ID"].notnull()]
        if owned_terrains.empty:
            return
            
        # terreno aleatorio
        seed_terrain = owned_terrains.sample(1).iloc[0]
        owner_id = seed_terrain["OWNER_ID"]
        
        # terrenos conectados do mm dono
        cluster = set([seed_terrain["OBJECTID"]])
        border = set()
        
        # travessia para encontrar o cluster
        to_visit = [seed_terrain["OBJECTID"]]
        while to_visit:
            current = to_visit.pop(0)
            neighbors = gdf.loc[gdf["OBJECTID"] == current, "neighbors"].iloc[0]
            
            for neighbor in neighbors:
                if gdf.loc[gdf["OBJECTID"] == neighbor, "OWNER_ID"].iloc[0] == owner_id:
                    if neighbor not in cluster:
                        cluster.add(neighbor)
                        to_visit.append(neighbor)
                else:
                    border.add(neighbor)
        
        # troca terrenos na borda
        border_list = list(border)
        if border_list:
            num_swaps = min(len(border_list), random.randint(1, 3))
            for _ in range(num_swaps):
                target = random.choice(border_list)
                if not pd.isna(gdf.loc[gdf["OBJECTID"] == target, "OWNER_ID"].iloc[0]):
                    old_owner = gdf.loc[gdf["OBJECTID"] == target, "OWNER_ID"].iloc[0]
                    gdf.loc[gdf["OBJECTID"] == target, "OWNER_ID"] = owner_id
                    
                    # encontra terreno do cluster para trocar
                    edge_terrains = [t for t in cluster if old_owner in 
                                [gdf.loc[gdf["OBJECTID"] == n, "OWNER_ID"].iloc[0] 
                                    for n in gdf.loc[gdf["OBJECTID"] == t, "neighbors"].iloc[0]]]
                    
                    if edge_terrains:
                        swap_terrain = random.choice(edge_terrains)
                        gdf.loc[gdf["OBJECTID"] == swap_terrain, "OWNER_ID"] = old_owner


    @classmethod
    def multiple_swap_mutation(cls,gdf,initial_areas):
        
        number_of_owners = len(gdf["OWNER_ID"].unique())
        
        iterations = random.randint(1,number_of_owners) #pode ser melhor...

        for _ in range( iterations):
            cls.swap_mutation(gdf,initial_areas)


    




    @classmethod
    def swap_mutation(cls, gdf, initial_areas):

        owned_terrains = gdf[gdf["OWNER_ID"].notnull()]
        if owned_terrains.empty:
            return

        # terreno random
        selected_terrain = owned_terrains.sample(1).iloc[0]
        neighbors = selected_terrain["neighbors"]
        
        # filtra vizinhos com outros donos
        valid_neighbors = [
            n for n in neighbors 
            if not pd.isna(gdf.loc[gdf["OBJECTID"] == n, "OWNER_ID"].iloc[0]) 
            and gdf.loc[gdf["OBJECTID"] == n, "OWNER_ID"].iloc[0] != selected_terrain["OWNER_ID"]
        ]
        
        if valid_neighbors:
            neighbor_id = random.choice(valid_neighbors)
            neighbor = gdf.loc[gdf["OBJECTID"] == neighbor_id].iloc[0]
            
            # troca donos
            gdf.loc[gdf["OBJECTID"] == selected_terrain["OBJECTID"], "OWNER_ID"] = neighbor["OWNER_ID"]
            gdf.loc[gdf["OBJECTID"] == neighbor_id, "OWNER_ID"] = selected_terrain["OWNER_ID"]

    @classmethod
    def optimize(cls, gdf, tracker=None, max_iters=100, alpha=0.6, beta=0.4, temp=200, cooling_rate=0.995, patience=20, add_pivots=None, reset=False, limit=-1):
        initial_areas = cls.calculate_initial_areas(gdf)
        gdf, tracker, _, _ = cls.redistribute(gdf, tracker=tracker)

        best_gdf = gdf.copy()
        best_cost = cls.calculate_cost(best_gdf, initial_areas, alpha, beta)
        
        current_gdf = gdf.copy()
        current_cost = best_cost

        explored_states = [(current_gdf.copy(), current_cost)]  #  guardar soluções exploradas
        max_explored_states = 100  #  máximo de estados armazenados
        
        no_improvement = 0
        reset_counter = 0
        max_resets = 3
        
        print(f"Custo inicial: {best_cost:.4f}")

        for i in range(max_iters):
            # tenta mutar
            mutated_gdf = cls.mutate(current_gdf, initial_areas)
            new_cost = cls.calculate_cost(mutated_gdf, initial_areas, alpha, beta)
            
            delta = new_cost - current_cost
            acceptance_prob = np.exp(-delta / temp) if temp > 0 else 0
            
            if delta < 0 or (random.random() < acceptance_prob and delta < current_cost * 0.1):  # limita custo máximo
                current_gdf = mutated_gdf.copy()
                current_cost = new_cost

                # nova soluçao armazenada
                explored_states.append((current_gdf.copy(), current_cost))
                if len(explored_states) > max_explored_states:  # tamanho máximo da lista
                    explored_states.pop(0)
                
                if new_cost < best_cost:
                    best_gdf = current_gdf.copy()
                    best_cost = new_cost
                    no_improvement = 0
                else:
                    no_improvement += 1
            else:
                no_improvement += 1
            
            if no_improvement >= patience:
                if reset_counter < max_resets:
                    print(f"Reset {reset_counter + 1} Estagnado!!!!!!!")
                    # escolhe uma solução aleatória para reiniciar
                    current_gdf, current_cost = random.choice(explored_states)
                    temp = 100.0  
                    no_improvement = 0
                    reset_counter += 1
                else:
                    print("Náx resets")
                    break
            
            # atualiza temp
            temp = max(0.01, temp * cooling_rate)
            
            print(f"Iteração {i}: Custo atual = {current_cost:.4f}, "
                    f"Melhor custo = {best_cost:.4f}, "
                    f"Temp = {temp:.4f}")

        print(f"Custo final: {best_cost:.4f}")
        print(f"Erro de ag. final: {Defrag_Generator.calculate_aggregation_error(best_gdf):.4f}")
        print(f"Erro de redistribuição final: {Stats.error_diff_with_redistribution(best_gdf, initial_areas)[0]:.4f}")
        return best_gdf, tracker, initial_areas, False
