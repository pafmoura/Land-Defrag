from django.test import TestCase
from myapi.utils.classes.defrag_pivot_area_min_aggr import Swap
from myapi.utils.classes.defrag_pivot_area_min_aggr import Traker
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

    def test_redistribute_areas(self):
        startTime = time.time() * 1000
        Redistribute.redistribute_areas(self.gdf, Redistribute.calculate_initial_areas(self.gdf), Traker(), 7000)
        endTime = time.time() * 1000
        self.assertLessEqual(endTime-startTime, 3, 'Area redistribution took longer than the alloted time period.') # Time in miliseconds
