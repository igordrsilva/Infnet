import pandas as pd

df = pd.read_json('Aulas/2026-08-03/clientes_delivery.json')

dados_puros = df.to_dict(orient='records')

# Agora o json_normalize funciona perfeitamente
df_flat = pd.json_normalize(
    dados_puros,
    record_path=["pedidos"],
    meta=[
        "id_cliente", 
        "nome", 
        "cidade", 
        ["endereco", "rua"], 
        ["endereco", "numero"], 
        ["endereco", "cep"]
    ]
).explode("itens").reset_index(drop=True)

df_flat = df_flat.rename(columns=lambda x: x.split(".")[-1] if "endereco." in x else x)
df_flat["valor_total"] = df_flat["valor_total"].apply(lambda x: x.replace(",", ".").strip()).astype(float)

print(df_flat.head())