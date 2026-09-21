import os
import dotenv
import pandas as pd
import requests

dotenv.load_dotenv()

API_VACINACAO = os.getenv("API_VACINACAO")

def get_raw_data() -> None:
    offset = 0
    limit = 1000
    all_records = []

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "application/json"
    }

    while True:
        try:
            response = requests.get(
                API_VACINACAO,
                params={
                    "limit": limit,
                    "offset": offset
                },
                headers=headers,
                timeout=30
            )
            response.raise_for_status()
            
            data = response.json()
            records = data['doses_aplicadas_pni']
            
            if not records:
                print(f"Extração concluída! Total de registros coletados: {len(all_records)}")
                break
                
            all_records.extend(records)
            
            offset += limit
            
        except requests.exceptions.ConnectionError as ce:
            print(f"Erro de conexão ao acessar o ano 2025 (O servidor pode estar fora do ar): {ce}")
            break
        except requests.exceptions.HTTPError as he:
            print(f"Erro HTTP no ano 2025: {he}")
            break
        except Exception as e:
            print(f"Erro inesperado no ano 2025: {e}")
            break

    pd.DataFrame(all_records).to_csv('data/raw/data.csv')