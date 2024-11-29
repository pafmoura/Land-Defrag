from myapi.models import Defrag_Process

from myapi.serializers import Defrag_Process_Serializer

from myapi.utils.classes.defrag_pivot_area_min_aggr import Defrag_Generator_Min_Aggr
from myapi.utils.classes.redistribution_defrag import Redistribute
from myapi.utils.classes.defrag_classes import Defrag_Generator
from myapi.utils.classes.stats import Stats
from myapi.utils.geopandas_wrapper import check_geopackage_status, convert_types, read_geopandas, save_file
from myapi.utils.utils import preprocess_geopandas
from myapi.utils.classes.beam_search_algorithm import MutationalRedistribute

from django.contrib.auth import authenticate
from django.contrib.auth.models import User


from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.authtoken.models import Token

@api_view(["GET"])
def test_connection(_request):
    return Response(status=status.HTTP_200_OK, data={"": "Alive"})


ALGORITHMS = {
    "unico": Defrag_Generator.defrag,
    "Menor Indice de Aggr": Defrag_Generator_Min_Aggr.defrag,
    "pedro": Redistribute.redistribute,  
    "beamsearch": MutationalRedistribute.optimize,
}

# INITIAL_AREAS = {
#     "unico": Defrag_Generator.calculate_initial_areas,
#     "pedro": Redistribute.calculate_initial_areas,
#     "beamsearch": MutationalRedistribute.calculate_initial_areas
# }

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
        defrag_function = ALGORITHMS.get(algorithm_name, None)
        if not defrag_function:
            return Response(
                status=status.HTTP_400_BAD_REQUEST,
                data={"error": f"Algorithm '{algorithm_name}' not found."}
            )


        gdf_new, tk, owners =  defrag_function(gdf=gdf, add_pivots=Defrag_Generator.add_pivots_by_area, limit=50, reset=True)
        save_file(gdf_new, defrag_file_name)
    
        stats = Stats.get_json(gdf, owners, is_using_class_Onwer=True)
        Stats.save(stats, defrag_file_name + ".json")

    return Response(status=status.HTTP_200_OK, data={"gdf": (gdf_new.__geo_interface__), "stats": stats })

@api_view(["GET"])
def logout(request):
    if request.META.get("HTTP_AUTHORIZATION"):
        try:
            token = Token.objects.get( key=request.META.get("HTTP_AUTHORIZATION").split(" ")[1])
            token.delete()
            return Response(status=status.HTTP_200_OK)
        except Token.DoesNotExist:
            pass
    return Response(status=status.HTTP_404_NOT_FOUND)


class LoginView(APIView):
    def post(self, request):
        username = request.data.get("username")
        password = request.data.get("password")
        user = authenticate(username=username, password=password)
        if user:
            token, _ = Token.objects.get_or_create(user=user)
            return Response({"token": token.key})
        else:
            return Response({"error": "Credenciais inválidas"}, status=status.HTTP_400_BAD_REQUEST)
        
@api_view(["GET"])
def get_states_defrag(request):
    if request.META.get("HTTP_AUTHORIZATION"):
        try:
            token = Token.objects.get(key=request.META.get("HTTP_AUTHORIZATION").split(" ")[1])
            user = token.user
            return Response({"name": user.username})
        except Token.DoesNotExist:
            user = get_or_create_default_user()
    
    processes = Defrag_Process.objects.filter(user=user)
    serializer = Defrag_Process_Serializer(processes, many=True)

    return Response({"result": serializer.data})


def get_or_create_default_user():
    return User.objects.get_or_create(username="Convidado", password="123")