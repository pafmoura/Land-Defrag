from myapi.utils.classes.defrag_classes import Defrag_Generator
from myapi.utils.geopandas_wrapper import check_geopackage_status, convert_types, read_geopandas, save_file
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
        file_name = request.POST["file_name"]
        file = request.FILES.get("gdf_file")
        name = request.POST["distribuition_name"]
        owners_average_land = int(request.POST["owners_average_land"])
    except KeyError:
        return Response(
            status=status.HTTP_400_BAD_REQUEST, data={"": request.POST["file_name"]}
        )
    
    generated_file_name  = f"{name}/{owners_average_land}/{file_name}"

    if check_geopackage_status(generated_file_name):
        gdf = read_geopandas(generated_file_name)
        convert_types(gdf)
    else:  
        folder = "defaults/" if file is None else "uploads/"
        gdf = read_geopandas(folder + file_name, file)
        save_file(gdf, folder + file_name)
        gdf = preprocess_geopandas(gdf, name=name, owners_average_land=owners_average_land)
        save_file(gdf, generated_file_name)

    return Response(status=status.HTTP_200_OK, data={"gdf": (gdf.__geo_interface__), "generated_file_name": generated_file_name})

@api_view(["POST"])
def defrag(request):
    try:
        algorithm_name = request.POST["algorithm_name"]
        generated_file_name = request.POST["generated_file_name"]
    except KeyError:
        return Response(
            status=status.HTTP_400_BAD_REQUEST, data={"": request.POST["algorithm_name"]}
        )
    
    defrag_file_name = f"{algorithm_name}/"+ generated_file_name
    if check_geopackage_status(defrag_file_name):
        gdf_new = read_geopandas(defrag_file_name)
        convert_types(gdf_new)
    else:
        gdf = read_geopandas(generated_file_name)
        convert_types(gdf)
        gdf_new, tk, _owners =  Defrag_Generator.defrag(gdf, add_pivots=Defrag_Generator.add_pivots_by_area, limit=104, reset=True)
        save_file(gdf_new, defrag_file_name)
    
    return Response(status=status.HTTP_200_OK, data={"gdf": (gdf_new.__geo_interface__), "trackers": "Under maintenance :)"})