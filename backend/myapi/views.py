from myapi.utils.classes.populate_classes import Population_Generator

import geopandas as gpd

from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response


@api_view(["GET"])
def test_connection(_request):

    return Response(status=status.HTTP_200_OK, data={"": "Alive"})


@api_view(["POST"])
def simulate(request):
    # TODO - Buscar ficheiro
    gdf = gpd.read_file(
        "path", layer="Parcelas_RAM"
    )  # Dummy Geopandas, não mudar nome de variável

    try:
        name = request.POST["defrag_algorithm"]
        owners_average_land = request.POST["owners_average_land"]
    except KeyError:
        return Response(status=status.HTTP_400_BAD_REQUEST, data={"": "Bad Request"})

    generator = Population_Generator.create_generator(
        name=name,
        num_rows_geopandas=len(gdf),
        owners_average_land=owners_average_land,
    )

    gdf["OWNER_ID"] = generator.populate()

    return Response(status=status.HTTP_200_OK, data={"": "Alive"})
