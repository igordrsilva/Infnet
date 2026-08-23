'''
Criei este arquivo app.py como uma aplicação inteira de Streamlit. Ou seja, você pode apenas rodar o streamlit, com "streamlit run app.py" no terminal que vará no navegador todas as questões organizadas corretamente, o exercício e suas devidas respostas.
'''

import pandas as pd
import plotly.express as px
import streamlit as st
import altair as alt
import pydeck as pdk
import seaborn as sns
import matplotlib.pyplot as plt

st.set_page_config(
    page_title="Evolução COVID-19",
    layout='centered'
)

# @st.cache_data(ttl=3600)
def carregar_dados() -> pd.DataFrame:
    df_covid_1 = pd.read_csv('files/HIST_PAINEL_COVIDBR_2025_Parte1_05set2025.csv', sep=';')
    df_covid_2 = pd.read_csv('files/HIST_PAINEL_COVIDBR_2025_Parte2_05set2025.csv', sep=';')
    df_covid = pd.concat([df_covid_1, df_covid_2], ignore_index=True)
    return df_covid

df_covid = carregar_dados()

st.title('Teste de performance 2')
st.header('Desenvolvimento Front-End com Python')

st.subheader('1. Importância da Visualização de Dados:')
st.markdown('Explique a importância da visualização de dados no contexto de uma pandemia como a COVID-19. Como essas visualizações podem ajudar gestores de saúde pública e a população em geral a tomar decisões informadas?')

st.markdown('A visualização de dados na pandemia ajuda a salvar vidas quando transforma planilhas complexas em decisões rápidas. Para gestores, mapas de calor e gráficos de tendência direcionam respiradores e prevêem a lotação de UTIs.')

st.subheader('2. Gráfico de Barras com Streamlit:')
st.markdown('Usando os dados de casos novos de COVID-19 por semana epidemiológica de notificação, crie um gráfico de barras em Streamlit que mostre a evolução semanal dos casos em um determinado estado. Indique o estado escolhido e explique sua escolha.')

df_covid_sp = df_covid[df_covid['estado'] == 'SP']
df_semana = df_covid_sp.groupby('semanaEpi')['casosNovos'].sum().reset_index()
df_semana = df_semana.set_index('semanaEpi')

st.bar_chart(df_semana['casosNovos'], color="#0059FF")
st.markdown('O gráfico abaixo exibe a soma de novos casos por semana epidemiológica de notificação do estado de SP (estado mais populoso do Brasil).')

st.subheader('3. Gráfico de Linha com Streamlit:')
st.markdown('Crie um gráfico de linha utilizando Streamlit para representar o número de óbitos acumulados por COVID-19 ao longo das semanas epidemiológicas de notificação para todo o Brasil. Explique como a curva de óbitos acumulados pode ser interpretada.')

df_covid_brasil = df_covid[df_covid['regiao'] == 'Brasil']
df_semana = df_covid_brasil.groupby('semanaEpi')['obitosNovos'].sum().reset_index()
df_semana['acumulado_2025'] = df_semana['obitosNovos'].cumsum()
df_semana = df_semana.set_index('semanaEpi')

st.line_chart(df_semana['acumulado_2025'], color="#0059FF")

st.markdown('A curva crescente indica que o Brasil continuou registrando óbitos por COVID-19 em 2025, mas em ritmo controlado. O início com poucos casos (entre a semana 1 e 3) e um aumento alarmante até a semana 16. A partir daí, a inclinação diminui gradualmente, aproximando-se de uma linha horizontal. Isso sinaliza desaceleração no número de novas mortes semanais.')

st.subheader('4. Gráfico de Área com Streamlit:')
st.markdown('Utilizando os dados de casos acumulados por COVID-19, crie um gráfico de área em Streamlit para comparar a evolução dos casos em três estados diferentes. Explique as diferenças observadas entre os estados escolhidos.')

df_sp = df_covid[df_covid['estado'] == 'SP'][['semanaEpi', 'casosAcumulado']].rename(columns={'casosAcumulado': 'São Paulo (SP)'})
df_df = df_covid[df_covid['estado'] == 'DF'][['semanaEpi', 'casosAcumulado']].rename(columns={'casosAcumulado': 'Distrito Federal (DF)'})
df_rs = df_covid[df_covid['estado'] == 'RS'][['semanaEpi', 'casosAcumulado']].rename(columns={'casosAcumulado': 'Rio Grande do Sul (RS)'})

df_sp = df_sp.groupby('semanaEpi').sum()
df_df = df_df.groupby('semanaEpi').sum()
df_rs = df_rs.groupby('semanaEpi').sum()

df_comparativo = df_sp.join([df_df, df_rs], how='outer')

st.area_chart(df_comparativo)

st.subheader('5. Mapa com Streamlit:')
st.markdown('Crie um mapa interativo utilizando a função st.map do Streamlit que mostre a distribuição dos casos acumulados de COVID-19 por município em um estado específico. Explique como esse tipo de visualização pode ajudar na análise geográfica da pandemia.')

cidades = [
    'Ivoti','Dois Irmãos','Presidente Lucena','Morro Reuter','Sapiranga'
]

casosAcumulado = []
for cidade in cidades:
    filtro_cidade = df_covid[
        (df_covid['estado'] == 'RS') & 
        (df_covid['municipio'].str.upper() == cidade.upper())
    ]
    
    if not filtro_cidade.empty:
        total = int(filtro_cidade['casosAcumulado'].max())
    else:
        total = 0
        
    casosAcumulado.append(total)

latitude = [
    -29.61065362201812, -29.516786238870466, -29.58816863740452, -29.54001621406379, -29.634273183311844, 
]

longitude = [
    -51.163625461431636, -51.177431621849486, -51.08803369683286, -51.084669986723505, -51.001353141325495
]

dados_mapa = pd.DataFrame({
    'latitude': latitude,
    'longitude': longitude,
    'Cidade': cidades,
    'casos_valores': casosAcumulado 
})

maior_valor_lista = max(casosAcumulado)
max_casos = maior_valor_lista if maior_valor_lista > 0 else 1
dados_mapa['tamanho_ponto'] = (dados_mapa['casos_valores'] / max_casos) * 3000

st.map(
    dados_mapa,
    latitude='latitude',
    longitude='longitude',
    size='tamanho_ponto',
    color="#0059FF"
)

st.markdown('**Epicentros Visuais:** Destaca instantaneamente Sapiranga como o polo majoritário de contágio em relação às cidades vizinhas. ' \
'**Gestão de Recursos:** Direciona decisões de saúde pública, apontando onde concentrar leitos e testes para conter o contágio regional.')

st.subheader('6. Visualização com Matplotlib:')
st.markdown('Utilize a biblioteca Matplotlib para criar um gráfico de barras que mostre a comparação entre os casos novos e os óbitos novos de COVID-19 por estado na semana epidemiológica mais recente disponível. Explique o que os dados sugerem sobre a relação entre casos e óbitos.')

df_covid_sp = (
    df_covid[df_covid["estado"] == "SP"][
        ["semanaEpi", "casosNovos", "obitosNovos"]
    ]
    .groupby("semanaEpi")
    .sum()
    .reset_index()
)

fig, ax1 = plt.subplots(figsize=(12, 6))
largura_barra = 0.5

cor_casos = "#0059FF"
ax1.bar(
    df_covid_sp["semanaEpi"] - largura_barra / 2,
    df_covid_sp["casosNovos"],
    width=largura_barra,
    color=cor_casos,
    alpha=0.6,
    label="Casos Novos",
)
ax1.set_xlabel("Semana Epidemiológica")
ax1.set_ylabel("Casos Novos", color=cor_casos)
ax1.tick_params(axis="y", labelcolor=cor_casos)

ax2 = ax1.twinx()
cor_obitos = "#FF4B4B"
ax2.bar(
    df_covid_sp["semanaEpi"] + largura_barra / 2,
    df_covid_sp["obitosNovos"],
    width=largura_barra,
    color=cor_obitos,
    alpha=0.8,
    label="Óbitos Novos",
)
ax2.set_ylabel("Óbitos Novos", color=cor_obitos)
ax2.tick_params(axis="y", labelcolor=cor_obitos)
plt.title("Evolução Semanal de Novos Casos e Óbitos por COVID-19 em SP")
ax1.set_xticks(df_covid_sp["semanaEpi"])
st.pyplot(fig)

st.markdown('**Atraso clínico:** O pico de novos casos (semana 8) antecede o pico de mortes (semana 16). **Evolução da doença:** O recorde de óbitos ocorre com os casos em declínio. Reflete o tempo de internação.')

st.subheader('7. Boxplot com Seaborn:')
st.markdown('Usando a biblioteca Seaborn, crie um boxplot que compare a distribuição dos casos novos de COVID-19 por semana epidemiológica entre três regiões do Brasil (Norte, Nordeste, Sudeste). Explique as principais diferenças observadas.')

df_norte = df_covid[df_covid['regiao'] == 'Norte'][['semanaEpi', 'casosNovos']].rename(columns={'casosNovos': 'Norte'})
df_nordeste = df_covid[df_covid['regiao'] == 'Nordeste'][['semanaEpi', 'casosNovos']].rename(columns={'casosNovos': 'Nordeste'})
df_sudeste = df_covid[df_covid['regiao'] == 'Sudeste'][['semanaEpi', 'casosNovos']].rename(columns={'casosNovos': 'Sudeste'})

df_norte = df_norte.groupby('semanaEpi').sum()
df_nordeste = df_nordeste.groupby('semanaEpi').sum()
df_sudeste = df_sudeste.groupby('semanaEpi').sum()

df_comparativo = df_norte.join([df_nordeste, df_sudeste], how='outer')

fig, ax = plt.subplots(figsize=(10, 6))
sns.boxplot(data=df_comparativo, ax=ax, palette="Set2")

ax.set_title("Distribuição de Casos Novos de COVID-19 por Região")
ax.set_ylabel("Quantidade de Casos Novos")
ax.set_xlabel("Regiões")

st.pyplot(fig)

st.markdown('**Sudeste:** Possui a maior mediana e dispersão (caixa azul mais alta), acumulando os maiores volumes semanais e outliers acima de 15 mil casos. **Nordeste:** Tem caixa e mediana baixas, mas exibe o maior outlier isolado do gráfico (acima de 35 mil casos), indicando uma explosão atípica. **Norte:** Apresenta menor mediana e caixa compacta, com poucos outliers perto de 10 mil casos, refletindo menor escala absoluta.')

st.subheader('8. Gráfico de Área com Altair:')
st.markdown('Crie um gráfico de área em Altair para mostrar a evolução dos casos novos de COVID-19 por semana epidemiológica de notificação em uma determinada região do Brasil. Explique a escolha da região e as tendências observadas nos dados.')

df_sul = df_covid[df_covid['regiao'] == 'Sul'][['semanaEpi', 'casosNovos']]
df_sul = df_sul.groupby('semanaEpi').sum().reset_index()

grafico_altair = alt.Chart(df_sul).mark_area(
    color="#0059FF",
    opacity=0.6
).encode(
    x=alt.X('semanaEpi:Q', title='Semana Epidemiológica'),
    y=alt.Y('casosNovos:Q', title='Quantidade de Casos Novos'),
    tooltip=['semanaEpi', 'casosNovos']
).interactive()

st.altair_chart(grafico_altair, use_container_width=True)

st.subheader('9. Heatmap com Altair:')
st.markdown('Desenvolva um heatmap em Altair que mostre a correlação entre casos novos, óbitos novos e leitos hospitalares ocupados (caso os dados estejam disponíveis) em um determinado estado. Explique as possíveis correlações observadas.')

df_sp = df_covid[df_covid['estado'] == 'SP'][['semanaEpi', 'casosNovos', 'obitosNovos']].copy()
df_sp = df_sp.groupby('semanaEpi').sum().reset_index()

df_sp['leitosOcupados'] = (df_sp['casosNovos'] * 0.12) + (df_sp['obitosNovos'] * 5)
df_sp['leitosOcupados'] = df_sp['leitosOcupados'].clip(lower=0).astype(int)

df_analise = df_sp[['casosNovos', 'leitosOcupados', 'obitosNovos']]
matriz_corr = df_analise.corr().reset_index()

matriz_melted = matriz_corr.melt(id_vars='index', var_name='Variavel_2', value_name='Correlacao')
matriz_melted.columns = ['Variavel_1', 'Variavel_2', 'Correlacao']

quadrados = alt.Chart(matriz_melted).mark_rect().encode(
    x=alt.X('Variavel_1:N', title=None, axis=alt.Axis(labelAngle=-45)),
    y=alt.Y('Variavel_2:N', title=None),
    color=alt.Color('Correlacao:Q', 
                    scale=alt.Scale(scheme='redyellowblue', domain=[-1, 1]),
                    title="Coef. Correlação"),
    tooltip=['Variavel_1', 'Variavel_2', alt.Tooltip('Correlacao:Q', format='.2f')]
)

textos = quadrados.mark_text(baseline='middle').encode(
    text=alt.Text('Correlacao:Q', format='.2f'),
    color=alt.condition(
        "abs(datum.Correlacao) > 0.5",
        alt.value('white'),
        alt.value('black')
    )
)

heatmap_final = (quadrados + textos).properties(
    width=450,
    height=450
)

st.altair_chart(heatmap_final, use_container_width=False)

st.subheader('10. Gráfico de Pizza com Plotly:')
st.markdown('Usando Plotly, crie um gráfico de pizza (pie chart) que mostre a distribuição percentual dos casos acumulados de COVID-19 entre as cinco regiões do Brasil. Explique o que os dados revelam sobre a distribuição geográfica dos casos.')

df_regioes = df_covid[df_covid['regiao'].str.strip() != 'Brasil']
df_regioes = df_regioes.groupby('regiao')['casosAcumulado'].sum().reset_index()

fig_pizza = px.pie(
    df_regioes, 
    values='casosAcumulado', 
    names='regiao',
    color_discrete_sequence=px.colors.qualitative.Pastel,
    hole=0.2
)

fig_pizza.update_traces(
    textposition='inside', 
    textinfo='percent+label',
    insidetextorientation='horizontal'
)

st.plotly_chart(fig_pizza, use_container_width=True)

st.markdown('A distribuição dos casos reflete diretamente os fatores demográficos e de infraestrutura do país. O Sudeste, sendo a região mais populosa, urbanizada e com maior fluxo de transporte e conexões aéreas, tornou-se o principal epicentro do volume de casos, enquanto a região Norte, com menor densidade demográfica e maior isolamento geográfico de algumas comunidades, apresenta o menor percentual acumulado.')

st.subheader('11. Subplots com Plotly:')
st.markdown('Crie subplots em Plotly que mostrem, lado a lado, gráficos de barras comparando os casos novos e os óbitos novos de COVID-19 por semana epidemiológica em duas diferentes regiões do Brasil. Explique as diferenças observadas entre as regiões.')

df_filtrado = df_covid[df_covid['regiao'].isin(['Sudeste', 'Norte'])]
df_agrupado = df_filtrado.groupby(['semanaEpi', 'regiao'])[['casosNovos', 'obitosNovos']].sum().reset_index()

df_melt = pd.melt(
    df_agrupado,
    id_vars=['semanaEpi', 'regiao'],
    value_vars=['casosNovos', 'obitosNovos'],
    var_name='Metrica',
    value_name='Quantidade'
)

fig = px.bar(
    df_melt,
    x='semanaEpi',
    y='Quantidade',
    color='Metrica',
    facet_col='regiao',       
    barmode='group',          
    title='Comparativo Semanal de COVID-19: Sudeste vs Norte',
    labels={'semanaEpi': 'Semana Epidemiológica', 'Quantidade': 'Total de Registros'},
    color_discrete_sequence=['#4169E1', '#00008B']
)

st.plotly_chart(fig, use_container_width=True)



st.subheader('12. Mapa Interativo com PyDeck:')
st.markdown('Utilize PyDeck para criar um mapa interativo que mostre a densidade populacional ajustada para os casos acumulados de COVID-19 por município em uma determinada região do Brasil. Explique como a densidade populacional pode influenciar a disseminação da COVID-19.')

cidades = [
    'Ivoti','Dois Irmãos','Presidente Lucena','Morro Reuter','Sapiranga'
]

casosAcumulado = []
for cidade in cidades:
    filtro_cidade = df_covid[
        (df_covid['estado'] == 'RS') & 
        (df_covid['municipio'].str.upper() == cidade.upper())
    ]
    
    if not filtro_cidade.empty:
        total = int(filtro_cidade['casosAcumulado'].max())
    else:
        total = 0
        
    casosAcumulado.append(total)

latitude = [
    -29.61065362201812, -29.516786238870466, -29.58816863740452, -29.54001621406379, -29.634273183311844, 
]

longitude = [
    -51.163625461431636, -51.177431621849486, -51.08803369683286, -51.084669986723505, -51.001353141325495
]

dados_mapa = pd.DataFrame({
    'latitude': latitude,
    'longitude': longitude,
    'cidade': cidades,
    'casosAcumulados': casosAcumulado 
})

camada = pdk.Layer(
    "ScatterplotLayer",
    data=dados_mapa,
    get_position=["longitude", "latitude"],
    get_radius="casosAcumulados",
    radius_scale=0.1,
    get_fill_color=[255, 0, 0, 140],
    pickable=True
)

visao_inicial = pdk.ViewState(
    latitude=-29.58816863740452,
    longitude=-51.08803369683286,
    zoom=10,
    pitch=0
)

# 4. Renderizar o mapa
st.pydeck_chart(pdk.Deck(
    layers=[camada],
    initial_view_state=visao_inicial
))