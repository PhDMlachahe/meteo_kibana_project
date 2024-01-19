import json
import requests
import datetime

# Dictionnaire de villes françaises
cities = {
    "Paris": {"latitude": 48.8566, "longitude": 2.3522},
    "Lyon": {"latitude": 45.7640, "longitude": 4.8357},
    "Marseille": {"latitude": 43.2965, "longitude": 5.3698},
    "Nice": {"latitude": 43.7102, "longitude": 7.2620},
    "Roubaix": {"latitude": 50.6942, "longitude": 3.1746},
    "Strasbourg": {"latitude": 48.5734, "longitude": 7.7521},
    "Lille" : {"latitude": 50.6293, "longitude": 3.0573},
    "Rennes": {"latitude": 48.1173, "longitude": -1.6778},
    "Grenoble": {"latitude": 45.1885, "longitude": 5.7245},
    "Eaubonne": {"latitude": 48.9908, "longitude": 2.2778},
    "Vitry-sur-Seine": {"latitude": 48.7876, "longitude": 2.3922},
    "Champigny-sur-Marne": {"latitude": 48.8176, "longitude": 2.5152},
    "Armentieres": {"latitude": 50.6892, "longitude": 2.8806},
}

# Dictionnaire des codes météorologiques
weather_codes = {
    0: "Clear ☀️",
    1: "Clear ☀️",
    2: "Partly Cloudy 🌤",
    3: "Cloudy ☁️",
    45: "Foggy 🌫",
    48: "Foggy 🌫",
    51: "Drizzle 🌦",
    53: "Drizzle 🌦",
    55: "Drizzle 🌦",
    56: "Freezing Drizzle 🧊🌧",
    57: "Freezing Drizzle 🧊🌧",
    61: "Rain 🌧",
    63: "Rain 🌧",
    65: "Rain 🌧",
    66: "Freezing Rain 🌧❄️",
    67: "Freezing Rain 🌧❄️",
    71: "Snow ❄️",
    73: "Snow ❄️",
    75: "Snow ❄️",
    77: "Snow Grains ❄️",
    80: "Showers 🌧",
    81: "Showers 🌧",
    82: "Showers 🌧",
    85: "Snow Showers ❄️",
    86: "Snow Showers ❄️",
    95: "Thunderstorm ⛈",
    96: "Thunderstorm ⛈",
    99: "Thunderstorm ⛈"
}

# Fonction pour convertir le code en string
def get_weather_code_description(weather_code):
    if weather_code in weather_codes:
        return weather_codes[weather_code]
    else:
        return None

def get_weather_data(city_name, start_date, end_date):
    # Récupérer la latitude et la longitude de la ville
    latitude = cities[city_name]["latitude"]
    longitude = cities[city_name]["longitude"]

    # Construire l'URL de l'API
    url = f"https://api.open-meteo.com/v1/forecast?latitude={latitude}&longitude={longitude}&hourly=temperature_2m,relative_humidity_2m,apparent_temperature,precipitation_probability,precipitation,weather_code,surface_pressure,wind_speed_10m&timezone=Europe%2FBerlin&start_date={start_date}&end_date={end_date}"

    # Envoyer une requête GET à l'API
    response = requests.get(url)

    # Vérifier si la requête a réussi
    if response.status_code == 200:
        # Ajouter le nom de la ville aux données JSON
        data = response.json()
        data['city'] = city_name
        return data
    else:
        # Retourner une erreur si la requête a échoué
        return f"Error: Unable to fetch data, status code {response.status_code}"

# Function to transform the JSON data into JSON lines
def transform_json_to_json_lines(json_data):
    hourly_data = json_data["hourly"]
    city_name = json_data["city"]
    latitude = cities[city_name]["latitude"]
    longitude = cities[city_name]["longitude"]
    json_lines = []

    for i in range(len(hourly_data["time"])):
        line = {
            "city": city_name,
            "location": {"lat": latitude, "lon": longitude},
            "time": hourly_data["time"][i],
            "temperature_2m": hourly_data["temperature_2m"][i],
            "relative_humidity_2m": hourly_data["relative_humidity_2m"][i],
            "apparent_temperature": hourly_data["apparent_temperature"][i],
            "precipitation_probability": hourly_data["precipitation_probability"][i],
            "precipitation": hourly_data["precipitation"][i],
            "weather_emoji": get_weather_code_description(hourly_data["weather_code"][i]),
            "surface_pressure": hourly_data["surface_pressure"][i],
            "wind_speed_10m": hourly_data["wind_speed_10m"][i]
        }
        json_lines.append(json.dumps(line))

    return json_lines

# Paramètres de date pour la requête
# Définir la date de début à forecast_days jours avant aujourd'hui
forecast_days = 400
start_date = datetime.date.today() - datetime.timedelta(days=forecast_days)

# La date de fin est la date d'aujourd'hui
end_date = datetime.date.today()

# Liste pour conserver toutes les lignes JSON de toutes les villes
all_json_lines = []

# Itérer sur chaque ville et collecter les données météorologiques
for city_name in cities:
    weather_data = get_weather_data(city_name, start_date, end_date)
    transformed_json_lines = transform_json_to_json_lines(weather_data)
    all_json_lines.extend(transformed_json_lines)

# Saving the transformed data to a file # Sauvegarder dans le dossier du projet Kibana
with open("C:/Users/MLACHAHE/Downloads/elk-demo-master/data/data_weather.json", 'w') as file:
    for line in all_json_lines:
        file.write(line + "\n")

# Confirming that the data is saved
print("Data saved to data_weather.json")
