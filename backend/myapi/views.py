from myapi.utils.utils import preprocess_geopandas

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
        name = request.POST["distribuition_name"]
        owners_average_land = request.POST["owners_average_land"]
    except KeyError:
        return Response(status=status.HTTP_400_BAD_REQUEST, data={"": "Bad Request"})

    gdf = preprocess_geopandas(gdf, name=name, owners_average_land=owners_average_land)

    return Response(status=status.HTTP_200_OK, data={"": "Alive"})
