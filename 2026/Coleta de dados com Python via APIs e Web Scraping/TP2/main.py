from src.data import get_dolar_value, get_weather

if __name__ == '__main__':
    dolar_value = get_dolar_value()
    print(f'Valor atual do dolar: ${dolar_value}')

    # Cidade escolhida: Frankfurt - Alemanha
    weather = get_weather('50.1155', '8.6842')
    print(f'Clima: ${weather}')