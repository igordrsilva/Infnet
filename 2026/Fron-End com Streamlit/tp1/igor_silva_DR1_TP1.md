# Teste de performance 1
#### Desenvolvimento Front-End com Python (com Streamlit)

## Preparar ambiente para desenvolvimento local de Streamlit com Python
#### Exercício 1: Motivação para usar Streamlit
Descreva, em um texto de 200 palavras, a motivação para usar a biblioteca Streamlit no contexto da Ciência de Dados. Inclua exemplos de casos de uso onde Streamlit pode ser vantajoso.

**Resposta:**

O Streamlit revolucionou a forma como cientistas de dados realizam suas entregas. Anteriormente, para desenvolver uma aplicação front-end e compartilhar uma análise, era preciso um conhecimento intermediário/avançado em HTML e CSS para conseguir desenvolver algo visualmente atraente. O Streamlit possibilitou que, ainda utilizando Python, fosse possível desenvolver uma aplicação web que exibisse todos os gráficos e análises, facilitando apresentações e entregas de projetos.

Podemos listar alguns exemplos de utilização, os quais o Streamlit facilitou:
* Apresentações de POCs
* Exploração de dados
* Dashboards dinâmicos
* Apresentações de KPIs
* Aplicações de Machine Learning

#### Exercício 2: Características da biblioteca Streamlit
Liste e explique pelo menos cinco características principais da biblioteca Streamlit que a tornam adequada para o desenvolvimento de aplicações de Ciência de Dados.

**Resposta:**

1. Desenvolvimento em Python
2. Componentes como variáveis
3. Execução top-down
4. Integração nativa com dados
5. Cache integrado

#### Exercício 3: Preparar ambiente de desenvolvimento
Crie um ambiente virtual utilizando virtualenv ou pipenv, e instale as dependências necessárias para desenvolver uma aplicação Streamlit. Documente cada etapa do processo e descreva as vantagens de utilizar um ambiente virtual para o desenvolvimento de software.

**Resposta:**

1. Criamos as pastas do projeto para o TP1 e o arqui:  `app.py`
2. Criamos o ambiente vitual:  `python3 -m venv .venv`
3. Ativação do ambiente virtual (Mac):  `source .venv/bin/activate`
4. Atualização do pacote pip:  `pip install --upgrade pip`
5. Instalação das dependências:  `pip install pandas streamlit kagglehub`
6. Criação do arquive requirements:  `pip freeze > requirements.txt`
7. Desativar o ambiente virtual:  `deactivate`

![Exercício 3: Preparar ambiente de desenvolvimento](https://github.com/igordrsilva/Infnet/blob/main/2026/Fron-End%20com%20Streamlit/tp1/files/ex3.png)

#### Exercício 4: Instalação do Streamlit
Utilizando o ambiente virtual criado no exercício anterior, instale a biblioteca Streamlit usando pip. Em seguida, crie um pequeno script em Python que exiba a mensagem "Hello, Streamlit!" utilizando a função st.write(). Documente cada etapa do processo.

**Resposta:**

Streamlit instalado na questão anterior.

```
import streamlit as st # importação do pacote streamlit com alias st
st.write("Hello, Streamlit!") # st.write() com o texto solicitado
```

Para rodar:
1. Abra o terminal
2. Navegar até a pasta da aplicação
3. Ativar o ambiente virtual:  `source .venv/bin/activate`
4. Rodar:  `streamlit run app.py`

![Exercício 4: Instalação do Streamlit](https://github.com/igordrsilva/Infnet/blob/main/2026/Fron-End%20com%20Streamlit/tp1/files/ex4.png)

## Criação de uma Aplicação Streamlit com os Dados
A partir deste ponto, você criará uma única aplicação Streamlit utilizando a base de dados "Most Streamed Spotify Songs 2024". Cada exercício deve ser uma adição incremental à sua aplicação.


#### Exercício 5: Títulos e textos formatados
Crie uma aplicação Streamlit que exiba um título, um cabeçalho, um subcabeçalho e um parágrafo de texto utilizando as funções st.title(), st.header(), st.subheader() e st.text(). Utilize a linguagem de marcação markdown para adicionar um link e um texto em negrito no parágrafo. Inclua printscreens desta etapa.

**Resposta:**

```
import streamlit as st

st.title("Teste de performance 1 (title)")
st.header("Exercício 5 (header)")
st.subheader("Títulos e textos formatados (subheader)")
st.text("Hello, Streamlit! (text)")
st.markdown("Aqui vai um texto [link](https://www.google.com/?hl=pt_BR)! (markdown)")
st.markdown("Aqui vai um texto em **negrito**! (markdown)")
```

![Exercício 5: Títulos e textos formatados](https://github.com/igordrsilva/Infnet/blob/main/2026/Fron-End%20com%20Streamlit/tp1/files/ex5.png)

#### Exercício 6: Exibir DataFrame com pandas
Carregue o dataset "Most Streamed Spotify Songs 2024" utilizando a biblioteca pandas. Exiba o DataFrame completo em sua aplicação Streamlit usando as funções st.dataframe() e st.table(). Documente as diferenças entre as duas funções. Inclua printscreens desta etapa.

**Resposta:**

```
import streamlit as st # importação do pacote streamlit com alias st
import pandas as pd # importação do pacote pandas com alias pd
import kagglehub

# Carregando o dataset "Most Streamed Spotify Songs 2024" do Kaggle
path = kagglehub.dataset_download("nelgiriyewithana/most-streamed-spotify-songs-2024")
dataset_path = path + "/Most Streamed Spotify Songs 2024.csv"

# Lendo o arquivo CSV usando pandas
df = pd.read_csv(dataset_path, encoding='iso-8859-1')

# Exibindo o DataFrame completo usando st.dataframe()
st.write("Exibindo o DataFrame completo usando st.dataframe():")
st.dataframe(df)
```

![Exercício 6: Exibir DataFrame com pandas](https://github.com/igordrsilva/Infnet/blob/main/2026/Fron-End%20com%20Streamlit/tp1/files/ex6.png)

#### Exercício 7: Exibir métricas
Selecione três músicas do dataset e adicione à sua aplicação Streamlit a exibição do nome da música, o artista e o número de streams utilizando a função st.metric(). Explique como esta função pode ser útil em dashboards de dados. Inclua printscreens desta etapa.

**Resposta:**

```
import streamlit as st # importação do pacote streamlit com alias st
import pandas as pd # importação do pacote pandas com alias pd
import kagglehub

# Carregando o dataset "Most Streamed Spotify Songs 2024" do Kaggle
path = kagglehub.dataset_download("nelgiriyewithana/most-streamed-spotify-songs-2024")
dataset_path = path + "/Most Streamed Spotify Songs 2024.csv"

# Lendo o arquivo CSV usando pandas
df = pd.read_csv(dataset_path, encoding='iso-8859-1')

if not df.empty:
    for i, row in df.head(3).reset_index(drop=True).iterrows():
        col1, col2, col3, col4 = st.columns([1, 3, 3, 3])
        col1.write(f"{i+1}")
        col2.write(f"Música: {row['Track']}")
        col3.write(f"Artista: {row['Artist']}")
        col4.metric("Número de Streams", row['Spotify Streams'])
```

A função `st.metric()` é indicada para dashboards, pois foi projetada pra exibir e destacar valores de KPIs e indicadores, além de ter o parâmetro delta, que possibilita a comparação entre valores.

![Exercício 7: Exibir métricas](https://github.com/igordrsilva/Infnet/blob/main/2026/Fron-End%20com%20Streamlit/tp1/files/ex7.png)

#### Exercício 8: Utilizar a função write()
Na sua aplicação Streamlit, utilize a função st.write() para exibir um DataFrame, um texto markdown e uma lista. Demonstre a versatilidade da função st.write() ao lidar com diferentes tipos de dados. Inclua printscreens desta etapa.

**Resposta:**

```
import streamlit as st # importação do pacote streamlit com alias st
import pandas as pd # importação do pacote pandas com alias pd
import kagglehub

# Carregando o dataset "Most Streamed Spotify Songs 2024" do Kaggle
path = kagglehub.dataset_download("nelgiriyewithana/most-streamed-spotify-songs-2024")
dataset_path = path + "/Most Streamed Spotify Songs 2024.csv"

# Lendo o arquivo CSV usando pandas
df = pd.read_csv(dataset_path, encoding='iso-8859-1')

st.write(df.head())
st.write('''
## Preparar ambiente para desenvolvimento local de Streamlit com Python
#### Exercício 1: Motivação para usar Streamlit
Descreva, em um texto de 200 palavras, a motivação para usar a biblioteca Streamlit no contexto da Ciência de Dados. Inclua exemplos de casos de uso onde Streamlit pode ser vantajoso.

**Resposta:**

O Streamlit revolucionou a forma como cientistas de dados realizam suas entregas.''')

st.write('''
1. Criamos as pastas do projeto para o TP1 e o arqui:  `app.py`
2. Criamos o ambiente vitual:  `python3 -m venv .venv`
3. Ativação do ambiente virtual (Mac):  `source .venv/bin/activate`
4. Atualização do pacote pip:  `pip install --upgrade pip`
5. Instalação das dependências:  `pip install pandas streamlit kagglehub`
6. Criação do arquive requirements:  `pip freeze > requirements.txt`
7. Desativar o ambiente virtual:  `deactivate`''')
```

![Exercício 8: Utilizar a função write()](https://github.com/igordrsilva/Infnet/blob/main/2026/Fron-End%20com%20Streamlit/tp1/files/ex8.png)

#### Exercício 9: Comandos Magic
Utilize comandos Magic para apresentar conteúdo na sua aplicação Streamlit. Crie um script que exiba um título, uma lista e um DataFrame apenas escrevendo diretamente no script sem usar funções explícitas do Streamlit. Inclua printscreens desta etapa.

**Resposta:**
```
 Markdown
'''
# Título do Aplicativo
Este é um texto em **negrito** usando comandos mágicos.
'''

# Variável
x = 42
'O valor da variável x é:', x

# DataFrame
df = pd.DataFrame({'coluna_a': [1, 2, 3], 'coluna_b': [4, 5, 6]})
df

# Gráfico do Matplotlib
arr = np.random.normal(1, 1, size=100)
fig, ax = plt.subplots()
ax.hist(arr, bins=20)
fig
```

![Exercício 9: Comandos Magic](https://github.com/igordrsilva/Infnet/blob/main/2026/Fron-End%20com%20Streamlit/tp1/files/ex9.png)

#### Exercício 10: Incorporar multimídia
Adicione à sua aplicação Streamlit a exibição de uma imagem, um vídeo e um áudio. Utilize as funções st.image(), st.video() e st.audio() para incorporar esses elementos multimídia na sua aplicação. Inclua printscreens desta etapa.

**Resposta:**
```
st.write('Imagem')
st.image("https://picsum.photos/400/300", width='stretch')

st.write('Vídeo')
st.video("https://samplelib.com/mp4/sample-5s.mp4")

st.write('Áudio')
st.audio("https://samplelib.com/mp3/sample-3s.mp3")
```

![Exercício 10: Incorporar multimídia](https://github.com/igordrsilva/Infnet/blob/main/2026/Fron-End%20com%20Streamlit/tp1/files/ex10.png)

#### Exercício 11: Utilizar animações e emojis
Adicione uma animação (GIF) e alguns emojis na sua aplicação Streamlit. Utilize as funções apropriadas para garantir que esses elementos sejam exibidos corretamente. Inclua printscreens desta etapa.

**Resposta:**
```
st.write("Animações")
st.button("Faça nevar!",on_click=lambda: st.snow())

st.write("Emojis")
st.button("Mostrar Emojis", on_click=lambda: st.balloons())

st.set_page_config(
    page_title="Animações e Emojis",
    page_icon=":snowflake:"
)
```

![Exercício 11-1: Utilizar animações e emojis](https://github.com/igordrsilva/Infnet/blob/main/2026/Fron-End%20com%20Streamlit/tp1/files/ex11-1.png)
![Exercício 11-2: Utilizar animações e emojis](https://github.com/igordrsilva/Infnet/blob/main/2026/Fron-End%20com%20Streamlit/tp1/files/ex11-2.png)
![Exercício 11-3: Utilizar animações e emojis](https://github.com/igordrsilva/Infnet/blob/main/2026/Fron-End%20com%20Streamlit/tp1/files/ex11-3.png)

#### Exercício 12: Combinar elementos em uma aplicação
Finalize sua aplicação Streamlit combinando todos os elementos textuais aprendidos (título, cabeçalho, subcabeçalho, texto formatado, DataFrame, métricas, multimídia e comandos Magic). Utilize o dataset "Most Streamed Spotify Songs 2024" para alimentar os dados da aplicação. A aplicação deve ser informativa e visualmente atraente. Inclua printscreens desta etapa.

**Resposta:**
```
path = kagglehub.dataset_download("nelgiriyewithana/most-streamed-spotify-songs-2024")
dataset_path = path + "/Most Streamed Spotify Songs 2024.csv"

st.title("TP1 - Desenvolvimento front-end com Streamlit")

st.header("Análise das músicas mais transmitidas no Spotify em 2024")
st.subheader("Explorando o dataset 'Most Streamed Spotify Songs 2024'")

st.text("Este aplicativo Streamlit apresenta uma análise das músicas mais transmitidas no Spotify em 2024. Utilizando o dataset fornecido, podemos explorar informações sobre os artistas, gêneros musicais e popularidade das músicas.")

st.markdown("O _dataset_ contém informações sobre as músicas mais transmitidas no _Spotify_ em 2024, incluindo o **nome da música**, **artista**, **gênero musical**, **número de streams** e **popularidade**. A seguir, apresentamos uma visão geral dos dados.")

st.write("Visualizando as primeiras linhas do dataset:")
df = pd.read_csv(dataset_path, encoding='latin-1')
st.dataframe(df.head())

st.write(f"Play the top 1 song: {df.iloc[0]['Track']} by {df.iloc[0]['Artist']}")
audio_file = open('files/million_dollar_baby-tommy_richman.mp3', 'rb')
audio_bytes = audio_file.read()
st.audio(audio_bytes, format='audio/mp3')

st.write("Métricas do dataset:")
col1, col2, col3 = st.columns([1, 1, 2])
col1.metric("Número de músicas", df.shape[0])
col2.metric("Número de artistas", df['Artist'].nunique())
col3.metric("Artista mais popular no Spotify", df.groupby('Artist')['Spotify Streams'].sum().idxmax())

"## FAQ - Perguntas Frequentes"
artista_popular = df['Artist'].value_counts().idxmax()

"Quantas músicas o artista mais popular tem no Spotify?"
df[df['Artist'] == artista_popular]['Track'].count(), 'música(s)'

"Somados todas as músicas, quantos plays o artista mais popular tem?"
df[df['Artist'] == artista_popular]['Spotify Streams'].str.replace(',', '').astype(int).sum(), 'plays'
```

![Exercício 12-1: Combinar elementos em uma aplicação](https://github.com/igordrsilva/Infnet/blob/main/2026/Fron-End%20com%20Streamlit/tp1/images/ex12-1.png)

![Exercício 12-2: Combinar elementos em uma aplicação](https://github.com/igordrsilva/Infnet/blob/main/2026/Fron-End%20com%20Streamlit/tp1/images/ex12-2.png)