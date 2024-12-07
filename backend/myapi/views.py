from multiprocessing import Process
from myapi.models import Defrag_Process, Utilizador

from myapi.serializers import Defrag_Process_Serializer

from myapi.utils.classes.defrag_pivot_area_min_aggr import Defrag_Generator_Min_Aggr
from myapi.utils.classes.redistribution_defrag import Redistribute
from myapi.utils.classes.defrag_classes import Defrag_Generator
from myapi.utils.classes.stats import Stats
from myapi.utils.geopandas_wrapper import check_geopackage_status, convert_types, read_geopandas, read_stats, save_file
from myapi.utils.utils import defrag_save, preprocess_geopandas
from myapi.utils.classes.beam_search_algorithm import MutationalRedistribute

from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required

from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.authtoken.models import Token


from rest_framework.response import Response
from rest_framework import status



@api_view(["GET"])
def test_connection(_request):
    return Response(status=status.HTTP_200_OK, data={"": "Alive"})

ALGORITHMS = {
    "Menor Indice de Aggr": Defrag_Generator_Min_Aggr.defrag,
    "pedro": Redistribute.redistribute,  
    "beamsearch": MutationalRedistribute.optimize,
}


@api_view(["POST"])
def simulate(request):
    try:
        user = check_user(request)
    except Exception:
        return Response({"message": "Not logged in"}, status=status.HTTP_401_UNAUTHORIZED)

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
        user = check_user(request)
    except Exception:
        return Response({"message": "Not logged in"}, status=status.HTTP_401_UNAUTHORIZED)
    
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

        user = get_user(request)
        new_defrag = Defrag_Process.objects.create(
              user=user,
              generated_file_name=defrag_file_name,
              is_completed=False)

        new_defrag.save()

        # process = Process(target=defrag_save, args=(gdf, defrag_function, defrag_file_name, new_defrag))
        # process.start()

        # TODO Temporário
        defrag_save(gdf, defrag_function, defrag_file_name, new_defrag)
    

    return Response(status=status.HTTP_200_OK, data={"message": "Process Initialized" })

@api_view(["POST"])
def logout(request):
    try:
        user = check_user(request)
    except Exception:
        return Response({"message": "Not logged in"}, status=status.HTTP_401_UNAUTHORIZED)
    
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

        if not username and not password:
            try:
                user = User.objects.get(username="Convidado")
            except User.DoesNotExist:
                user = create_default_user()
            username = "Convidado"
            password = "123"

        user = authenticate(username=username, password=password)

        if user:
            token, _ = Token.objects.get_or_create(user=user)
            return Response({"token": token.key})
        else:
            return Response({"error": "Credenciais inválidas"}, status=status.HTTP_400_BAD_REQUEST)
        
@api_view(["GET"])
def get_states_defrag(request):
    try:
        user = check_user(request)
    except Exception:
        return Response({"message": "Not logged in"}, status=status.HTTP_401_UNAUTHORIZED)

    generated_file_name = request.GET.get('generated_file_name', None)

    if not generated_file_name:
        processes = Defrag_Process.objects.filter(user=user)
        serializer = Defrag_Process_Serializer(processes, many=True)
        return Response({"result": serializer.data})
    
    process = Defrag_Process.objects.filter(user=user, generated_file_name=generated_file_name)
    if process.exists():
        gdf_new = read_geopandas(generated_file_name)
        stats_new = read_stats(generated_file_name + ".json")
        return Response({"gdf": gdf_new.__geo_interface__, "stats": stats_new}, status=status.HTTP_200_OK)
    else:
        return Response({"gdf":{}}, status=status.HTTP_404_NOT_FOUND)

def get_user(request):
    if request.META.get("HTTP_AUTHORIZATION"):
        token = Token.objects.get(key=request.META.get("HTTP_AUTHORIZATION").split(" ")[1])
        user = token.user
          
    return Utilizador.objects.get(user=user)

def check_user(request):
    user = get_user(request)
    if not user:
        raise Exception(user)
    return user

def create_default_user():
    user = User.objects.create(username="Convidado")
    user.set_password("123")
    user.save()

    utilizador = Utilizador.objects.create(user=user)
    utilizador.save()
    return utilizador