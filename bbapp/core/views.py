from django.http import HttpResponse
import requests
from django.shortcuts import render
from datetime import datetime
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
import time

# Create your views here.
def home(request):
    # buscar datos del personaje
    session = requests.Session()
    retry = Retry(connect=2, backoff_factor=1)
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('http://', adapter)
    session.mount('https://', adapter)

    if 'episodio' in request.GET:
        lista_episodios = request.GET.copy()
        lista_episodios = lista_episodios.pop('episodio')
        id_episodio = None
        for elem in lista_episodios:
            if elem != "None":
                id_episodio = elem
        url = "https://tarea-1-breaking-bad.herokuapp.com/api/episodes/{dato}".format(dato=id_episodio)
        r = session.get(url).json()[0]

        # Pasar date a date bonito
        date_time_str = r["air_date"].replace("T", " ").replace(".000Z", "")
        date_time_obj = datetime.strptime(date_time_str, '%Y-%m-%d %H:%M:%S').strftime('%B %d, %Y at %H:%M')


        episode_description = dict()
        episode_description["Name"] = r["title"]
        episode_description["Season"] = str(r["season"])
        episode_description["Air_Date"] = date_time_obj
        episode_description["characters"] = r["characters"]

        context = {"episode_description": episode_description}
        print("contexto: ", context)
        return render(request, 'core/episode.html', context)
    elif "character_search" in request.GET:
        dato_ingresado = request.GET.get('character_search').replace(' ', '+')
        url = "https://tarea-1-breaking-bad.herokuapp.com/api/characters?name={dato}".format(dato=dato_ingresado)
        # me va a devolver una lista de respuestas
        r = session.get(url).json()
        resultados = []
        print(r)

        for result in r:
            resultados.append(result["name"])

        search_description = dict()
        search_description["results"] = resultados
        search_description["input"] = request.GET.get('character_search')

        context = {"search_description": search_description}
        return render(request, 'core/search.html', context)

    elif 'character' in request.GET:
        dato_ingresado = request.GET.get('character').replace(' ', '+')
        url = "https://tarea-1-breaking-bad.herokuapp.com/api/characters?name={dato}".format(dato=dato_ingresado)
        url_frases = "https://tarea-1-breaking-bad.herokuapp.com/api/quote?author={dato}".format(dato=dato_ingresado)
        r =  session.get(url).json()[0]
        # time.sleep(3)
        r_frase = session.get(url_frases).json()
        frases = []

        for frase_dict in r_frase:
            frases.append(frase_dict["quote"])


        ##[{"char_id":1,"name":"Walter White","occupation":["High School Chemistry Teacher","Meth King Pin"],
        # "img":"https://images.amcnetworks.com/amc.com/wp-content/uploads/2015/04/cast_bb_700x1000_walter-white-lg.jpg",
        # "status":"Presumed dead","nickname":"Heisenberg","appearance":[1,2,3,4,5],"portrayed":"Bryan Cranston","category":"Breaking Bad",
        # "better_call_saul_appearance":[]}]

        character_description = dict()
        character_description["Name"] = str(r["name"])
        character_description["Occupation"] = r["occupation"]
        character_description["Status"] = str(r["status"])
        character_description["Nicknames"] = str(r["nickname"])
        character_description["appearance"] = r["appearance"]
        character_description["bcs_appearance"] = r["better_call_saul_appearance"]
        character_description["Portrayed"] = str(r["portrayed"])
        character_description["img"] = r["img"]
        character_description["quotes"] = frases

        print("aquí va la descripción", character_description)

        # print(r.text)

        #    pass
        # return render(request, 'core/home.html')
        context = {"character_description": character_description}
        print("contexto: ", context)
        return render(request, 'core/character.html', context)

    elif 'season' in request.GET:
            dict_request = request.GET.copy()
            season = dict_request.pop('season')[0]
            serie = dict_request.pop('serie')[0]
            #season:  ['2']   serie: ['bb']
            print("season:  ", season, "  serie: ", serie)

            season_description = dict()
            season_description["season"] = season
            if serie == "bb":
                season_description["Serie"] = "Breaking Bad"
                episodios= "https://tarea-1-breaking-bad.herokuapp.com/api/episodes?series=Breaking+Bad"
            else:
                season_description["Serie"] = "Better Call Saul"
                episodios= "https://tarea-1-breaking-bad.herokuapp.com/api/episodes?series=Better+Call+Saul"

            r = session.get(episodios).json()
            temporadas = ["1", "2", "3", "4", "5"]
            all_ep = []

            for diccionario in r:
                # considerando que vienen ordenados los episodios:
                # si la temporada del episodio es igual a "1"
                if diccionario["season"] == season:
                    all_ep.append(diccionario)

            season_description["episodes"] = all_ep
            context = {"season_description": season_description}
            return render(request, 'core/season.html', context)

    else:
        # obtener todos los episodios diferenciados por la temporada
        episodios_bb = "https://tarea-1-breaking-bad.herokuapp.com/api/episodes?series=Breaking+Bad"
        episodios_bcs = "https://tarea-1-breaking-bad.herokuapp.com/api/episodes?series=Better+Call+Saul"

        r = session.get(episodios_bb).json()
        # time.sleep(5)
        r_2 = session.get(episodios_bcs).json()

        temporadas = ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10"]
        all_ep_bb = []
        all_ep_bcs = []
        # all_ep_bb será un diccionario de tipo {"temporadas": n_temporadas, "contenido": lista_episodios}

        for temporada in temporadas:
            contenido_temporada = dict()
            contenido_temporada["name"] = temporada
            episodios_por_temporada = []
            for diccionario in r:
                # considerando que vienen ordenados los episodios:
                # si la temporada del episodio es igual a "1"
                if diccionario["season"] == temporada:
                    episodios_por_temporada.append(diccionario)
            contenido_temporada["episodes"] = episodios_por_temporada
            if episodios_por_temporada == []:
                pass
            else:
                all_ep_bb.append(contenido_temporada)

        for temporada in temporadas:
            contenido_temporada = dict()
            contenido_temporada["name"] = temporada
            episodios_por_temporada = []
            for diccionario in r_2:
                # considerando que vienen ordenados los episodios:
                # si la temporada del episodio es igual a "1"
                if diccionario["season"] == temporada:
                    episodios_por_temporada.append(diccionario)
            contenido_temporada["episodes"] = episodios_por_temporada
            if episodios_por_temporada == []:
                pass
            else:
                all_ep_bcs.append(contenido_temporada)

        all_shows = dict()
        all_shows["bb"] = all_ep_bb
        all_shows["bcs"] = all_ep_bcs

        context = {"all_ep_bb": all_shows}
        return render(request, 'core/home.html', context)

def character_view(request):
    print("llegué a character view con el siguiente request: ")
    print(request)

    character_name = request.GET.get('character').replace(' ', '+')
    url = "https://tarea-1-breaking-bad.herokuapp.com/api/characters?name={dato}".format(dato=character_name)
    r = requests.get(url).json()[0]

    character_description = dict()

    character_description["Name"] = str(r["name"])
    character_description["Occupation"] = r["occupation"]
    character_description["Status"] = str(r["status"])
    character_description["Nicknames"] = str(r["nickname"])
    character_description["appearance"] = r["appearance"]
    character_description["bcs_appearance"] = r["better_call_saul_appearance"]
    character_description["Portrayed"] = str(r["portrayed"])
    character_description["img"] = r["img"]

    context = {"character_description": character_description}
    return render(request, 'core/character.html', context)


def episode_view(request):
    dato_ingresado = request.GET
    print(request.GET)
    print(type(dato_ingresado))
    print(dato_ingresado.get("episodio"))
    return render(request, 'core/episode.html')


"""elif 'season' in request.GET:
        dict_request = request.GET.copy()
        season = dict_request.pop('season')
        serie = dict_request.pop('serie')
        print("season:  ", season, "  serie: ", serie)

        season_description = dict()

        context = {"season_description": season_description}
        return render(request, 'core/episode.html', context)"""
