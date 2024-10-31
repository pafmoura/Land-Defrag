from myapi.utils.geopandas_wrapper import read_geopandas
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
    try:
        file_name = request.POST["default_file"]
        name = request.POST["distribuition_name"]
        owners_average_land = int(request.POST["owners_average_land"])
    except KeyError:
        return Response(
            status=status.HTTP_400_BAD_REQUEST, data={"": request.POST["default_file"]}
        )

    if file_name:
        gdf = read_geopandas(file_name)
    else:
        pass  # TODO - Get Geopackage

    gdf = preprocess_geopandas(gdf, name=name, owners_average_land=owners_average_land)

    return Response(status=status.HTTP_200_OK, data=(gdf.__geo_interface__))
