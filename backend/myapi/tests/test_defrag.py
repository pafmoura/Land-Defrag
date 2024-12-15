from django.test import TestCase
from myapi.utils.classes.redistribution_mutations import MutationalRedistribute
from myapi.utils.classes.defrag_pivot_area_min_aggr import Swap, Traker
from myapi.utils.classes.defrag_pivot_area_min_aggr import Owner
from myapi.utils.classes.defrag_pivot_area_min_aggr import Defrag_Generator_Min_Aggr
from myapi.utils.classes.redistribution_defrag import Redistribute
from myapi.utils.geopandas_wrapper import check_geopackage_status, convert_types, read_geopandas, read_stats, save_file
from myapi.utils.utils import preprocess_geopandas
import time

class TestTraker(TestCase):

    def setUp(self):
        self.swap = Swap(3, 4, 1, 2) #IDs 3 e 4 para Owners 1 e 2
        self.traker = Traker()

    def test_swap(self):
        self.traker.add_swap(self.swap)
        self.assertIn(self.swap, self.traker.get_swaps(), 'Swap not properly indexed.')

    def test_error(self):
        self.traker.add_error("test")
        print(self.traker.errors)
        self.assertIn("test", self.traker.errors, 'Error not properly indexed.')


class TestOwnerAndAggregation(TestCase):

    def setUp(self):
        gdf = read_geopandas("test/test_geopackage.gpkg")
        save_file(gdf, "test/" + "test_geopackage")
        self.gdf = preprocess_geopandas(gdf, name="uniform", owners_average_land=1)
        save_file(gdf, "test/test_defrag_gdf")

        self.owners = Defrag_Generator_Min_Aggr.create_owners(self.gdf, Traker())
        #save_file(self.owners[0].get_terrains(self.gdf), "test/test_owner_terrain")

    def test_owners(self):
        self.assertTrue(self.owners, 'Owners not properly initialized.')

    def test_owner_terrains(self):
        self.assertFalse(self.owners[0].get_terrains(self.gdf).empty, 'Owner has no terrains.')
        #self.assertEqual(read_geopandas("test/test_owner_terrain"), self.owners[0].get_terrains(self.gdf), 'Owner has no terrains.')

    def test_owner_border_ids(self):
        self.assertTrue(self.owners[0].get_border_ids(self.gdf), 'Owner border IDs not assigned.')

    def test_aggregation_error(self):
        self.assertEqual(Defrag_Generator_Min_Aggr.base_aggregation_error(self.gdf), 0, 'Base aggregation error is not zero.')

    #def test_defrag(self):
    #    self.assertTrue(Defrag_Generator_Min_Aggr.defrag(self.gdf), 'Error in defrag function.')

    #def test_owner_pivots(self):
    #    self.assertIsNotNone(Defrag_Generator_Min_Aggr.add_pivots_by_area(self.owners, self.gdf), 'Pivots not being correctly assigned.')

    #def test_owner_neighbors(self):
    #    self.assertTrue(self.owners[0].get_neighbors(self.gdf), 'Owner neighbors not properly initialized.') 

class TestRedistribute(TestCase):

    def setUp(self):
        gdf = read_geopandas("test/test_geopackage.gpkg")
        save_file(gdf, "test/" + "test_geopackage2")
        self.gdf = preprocess_geopandas(gdf, name="uniform", owners_average_land=1)
        save_file(gdf, "test/test_defrag2_gdf")

    def test_initial_areas(self):
        self.assertTrue(Redistribute.calculate_initial_areas(self.gdf), 'Initial areas not properly intialized.')

   # def test_redistribute_areas(self):
    #    startTime = time.time() * 1000
   #     Redistribute.redistribute_areas(self.gdf, Redistribute.calculate_initial_areas(self.gdf), Traker(), 7000)
   #     endTime = time.time() * 1000
  #      self.assertLessEqual(endTime-startTime, 3, 'Area redistribution took longer than the alloted time period.') # Time in miliseconds

    def test_adjust_terrain(self):
            owner_id = self.gdf["OWNER_ID"].unique()[0]
            candidate_ids = self.gdf.loc[self.gdf["OWNER_ID"].isnull(), Redistribute.OBJECTID].values
            area_change = 100
            Redistribute.adjust_terrain(owner_id, candidate_ids, area_change, self.gdf)
            current_area = self.gdf.loc[self.gdf["OWNER_ID"] == owner_id, "Shape_Area"].sum()
            self.assertGreaterEqual(current_area, 100, "Area should increase by at least the required amount.")

    def test_find_available_terrains(self):
        owner_id = self.gdf["OWNER_ID"].unique()[0]
        visited_terrains = set()
        available_terrains = Redistribute.find_available_terrains(owner_id, visited_terrains, self.gdf)
        self.assertIsInstance(available_terrains, list, "Available terrains should be a list.")
        self.assertTrue(all(isinstance(t, int) for t in available_terrains), "Terrain IDs should be integers.")

    def test_buy_terrains(self):
        owner_id = self.gdf["OWNER_ID"].unique()[0]
        initial_areas = Redistribute.calculate_initial_areas(self.gdf)
        area_needed = 200
        Redistribute.buy_terrains(owner_id, area_needed, initial_areas, self.gdf, threshold=50)
        current_area = self.gdf.loc[self.gdf["OWNER_ID"] == owner_id, "Shape_Area"].sum()
        self.assertGreaterEqual(current_area, initial_areas[owner_id], "Owner's area should meet or exceed the target.")

    def test_sell_terrains(self):
        owner_id = self.gdf["OWNER_ID"].unique()[0]
        initial_areas = Redistribute.calculate_initial_areas(self.gdf)
        area_to_reduce = 100
        Redistribute.sell_terrains(owner_id, area_to_reduce, initial_areas, self.gdf, threshold=50)
        current_area = self.gdf.loc[self.gdf["OWNER_ID"] == owner_id, "Shape_Area"].sum()
        self.assertLessEqual(current_area, initial_areas[owner_id] - area_to_reduce, "Owner's area should decrease as required.")

    def test_no_available_terrains(self):
        owner_id = self.gdf["OWNER_ID"].unique()[0]
        visited_terrains = set(self.gdf[Redistribute.OBJECTID].values)
        available_terrains = Redistribute.find_available_terrains(owner_id, visited_terrains, self.gdf)
        self.assertEqual(len(available_terrains), 0, "No terrains should be available when all are visited.")


class TestMutationalRedistribute(TestCase):

    def setUp(self):
        gdf = read_geopandas("test/test_geopackage.gpkg")
        save_file(gdf, "test/test_geopackage_mutational")
        self.gdf = preprocess_geopandas(gdf, name="uniform", owners_average_land=1)
        self.initial_areas = MutationalRedistribute.calculate_initial_areas(self.gdf)

    def test_calculate_cost(self):
        cost = MutationalRedistribute.calculate_cost(self.gdf, self.initial_areas)
        self.assertIsInstance(cost, (int, float), "Cost should be a numeric value.")
        self.assertGreaterEqual(cost, 0, "Cost should be non-negative.")

    def test_swap_mutation(self):
        gdf_copy = self.gdf.copy()
        MutationalRedistribute.swap_mutation(gdf_copy, self.initial_areas)
        self.assertFalse(gdf_copy.equals(self.gdf), "The GeoDataFrame should be modified after swap mutation.")

    def test_multiple_swap_mutation(self):
        gdf_copy = self.gdf.copy()
        MutationalRedistribute.multiple_swap_mutation(gdf_copy, self.initial_areas)
        self.assertFalse(gdf_copy.equals(self.gdf), "The GeoDataFrame should be modified after multiple swap mutation.")

    def test_cluster_expansion_mutation(self):
        gdf_copy = self.gdf.copy()
        MutationalRedistribute.cluster_expansion_mutation(gdf_copy, self.initial_areas)
        self.assertFalse(gdf_copy.equals(self.gdf), "The GeoDataFrame should be modified after cluster expansion mutation.")

    def test_mutate(self):
        mutated_gdf = MutationalRedistribute.mutate(self.gdf, self.initial_areas)
        self.assertFalse(mutated_gdf.equals(self.gdf), "The GeoDataFrame should be modified after mutation.")

    def test_optimize(self):
        tracker = Traker()
        optimized_gdf, _, _, _ = MutationalRedistribute.optimize(self.gdf, tracker, max_iters=10, alpha=0.5, beta=0.5)
        self.assertFalse(optimized_gdf.equals(self.gdf), "The GeoDataFrame should be modified after optimization.")
        self.assertIsNotNone(tracker, "Tracker should not be None after optimization.")

    def test_no_available_terrains_after_mutation(self):
        visited_terrains = set(self.gdf[MutationalRedistribute.OBJECTID].values)
        available_terrains = MutationalRedistribute.find_available_terrains(
            self.gdf["OWNER_ID"].unique()[0], visited_terrains, self.gdf
        )
        self.assertEqual(len(available_terrains), 0, "No terrains should be available when all are visited.")
