from abc import ABC, abstractmethod
import numpy as np


class Population_Generator(ABC):
    def __init__(self, distribuition_name=None, num_rows_geopandas=None):
        self.distribuition_name = distribuition_name
        self.num_rows_geopandas = num_rows_geopandas

    @abstractmethod
    def populate(self):
        pass

    @classmethod
    def create_generator(cls, name, *args, **kwargs):
        np.random.seed(42)
        match name:
            case "Poisson":
                return Poisson_Generator(name, *args, **kwargs)
            case _:
                return Uniform_Generator(name, *args, **kwargs)


class Poisson_Generator(Population_Generator):
    def __init__(
        self, distribuition_name, num_rows_geopandas=None, owners_average_land=None
    ):
        super().__init__(distribuition_name, num_rows_geopandas)
        self.owners_average_land = owners_average_land

    def populate(self):
        """
        Returns a list of integers representing a owner for each land.
        Range of values: [0, infinity] - depending on the owners_average_land's attribute

        Example usage:

        >>> generator = Population_Generator.create_generator(
        ...     name="Poisson", num_rows_geopandas=100, owners_average_land=10
        ... )
        >>> generator.populate()
        [0, 1, 4, 1, 0, ...]
        """
        return np.random.poisson(
            lam=self.owners_average_land, size=self.num_rows_geopandas
        )


class Uniform_Generator(Population_Generator):

    def __init__(
        self, distribuition_name, num_rows_geopandas=None, owners_average_land=None
    ):
        super().__init__(distribuition_name, num_rows_geopandas)
        self.owners_average_land = owners_average_land

    def populate(self):
        """
        Returns a list of integers representing a owner for each land.
        Range of values: [0, num_owners)

        Example usage:

        >>> generator = Population_Generator.create_generator(
        ...     name="Uniform", num_rows_geopandas=100, owners_average_land=10
        ... )
        >>> generator.populate()
        [0, 1, 4, 1, 0, ...]
        """
        num_owners = (self.num_rows_geopandas // self.owners_average_land) - 1
        return np.round(
            np.random.uniform(low=0, high=num_owners, size=self.num_rows_geopandas)
        ).astype(int)
