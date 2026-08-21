from src.data import get_dolar_value, get_weather, send_data_to_forms

if __name__ == '__main__':
    dolar_value = get_dolar_value()

    weather = get_weather('50.1155', '8.6842') # Cidade escolhida: Frankfurt - Alemanha
    temperature = weather['temperature']
    weather = weather['weather']

    send_data_to_forms(dolar_value, temperature, weather)
    print('-'*30)
    print('Feito! Enviado as informações ao equipe de compras.')