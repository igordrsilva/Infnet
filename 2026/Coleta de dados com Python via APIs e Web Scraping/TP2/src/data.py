import requests
import os
import dotenv

dotenv.load_dotenv()

API_DOLAR = os.getenv('API_DOLAR')
API_WEATHER = os.getenv('API_WEATHER')

WEATHER_CODES = {
    0: "Céu limpo",
    1: "Principalmente limpo",
    2: "Parcialmente nublado",
    3: "Nublado",
    45: "Nevoeiro / Neblina",
    48: "Nevoeiro com geada",
    51: "Chuva leve",
    61: "Chuva fraca",
    63: "Chuva moderada",
    65: "Chuva forte",
    71: "Neve fraca",
    73: "Neve moderada",
    75: "Neve forte",
    80: "Pancadas de chuva leves",
    81: "Pancadas de chuva moderadas",
    82: "Pancadas de chuva violentas",
    95: "Trovoada leve ou moderada",
}


# 1. Cotação do dolar do dia atual
def get_dolar_value() -> str:
    try:
        response = requests.get(API_DOLAR)
        response.raise_for_status()
        data = response.json()
        dolar_value = data["USDBRL"]["ask"]
        return dolar_value
    except Exception as e:
        return f"An error happened: {e}"


# 2. Condições climáticas na cidade do fornecedor
def get_weather(latitude:str, longitude:str) -> dict|str:
    try:
        response = requests.get(f'{API_WEATHER}?latitude={latitude}&longitude={longitude}&hourly=temperature_2m,weather_code')
        response.raise_for_status()
        data = response.json()
        current_code = data["hourly"]["weather_code"][0]
        current_temp = data["hourly"]["temperature_2m"][0]
        weather_desc = WEATHER_CODES.get(current_code, "Condição desconhecida")
        return {"temperature": f"{current_temp}°C", "weather": weather_desc}
    except Exception as e:
        return f"An error happened: {e}"


# 3. Enviar dados para Google Forms
def send_data_to_forms():
    pass