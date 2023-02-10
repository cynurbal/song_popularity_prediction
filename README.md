# Song Popularity Prediction

Predicción de la popularidad de una canción utilizando características de audio de Spotify Data.

Las características de las canciones se extraerán de la [API de Spotify](https://developer.spotify.com/documentation/web-api/)

Para el análisis, se identificarán características comunes entre las canciones más populares que pueden ser la entrada para predecir la popularidad de una canción


### Cuenta  Spotify

Desde mi cuenta de Spotify he registrado una aplización para poder utilizar su API web (https://developer.spotify.com/documentation/general/guides/app-settings/):

Los notebooks que se conectan a la API de Spotify necesitan leer el fichero *settings.env* que contiene en Client ID y el Cliente Secret necesarios para la autentificación

El fichero *settings.env* no se ha se ha subido a github, pero lo encontrareis en la carpeta del proyecto compartida. 

Este fichero debe colocarse en la ruta raíz del proyecto y en la carpeta spotify_model_predict


### Guía de ejecución

Para replicar el proyecto, ejecute los siguientes **jupyter notebooks** en el orden especificado.

0. **[Requisitos de instalación](https://github.com/cynurbal/song_popularity_prediction/blob/main/0-instalar.ipynb)**

Instalacion de librerías necesarias para el proyecto (spotipy, streamlit)

1. **[Extracción de canciones top](https://github.com/cynurbal/song_popularity_prediction/blob/main/1-extract_top_song_spotify.ipynb)**

Obtención de canciones dentro del Top Semanal Global (https://charts.spotify.com/charts/view/regional-global-weekly/latest)

2. **[Extracción de canciones no top](https://github.com/cynurbal/song_popularity_prediction/blob/main/2-extract_no_top_song_spotify.ipynb)**

Otención de canciones random dentro del mercado global

3. **[Extracción de caracteristicas de canciones](https://github.com/cynurbal/song_popularity_prediction/blob/main/3-extract_features_song_spotify.ipynb)**

Acceso a la API de Spotify para extraer información de la canción, características de audio, información de los artistas

4. **[Preparación de los datos](https://github.com/cynurbal/song_popularity_prediction/blob/main/4-featuring_engineering.ipynb)**

Análisis exploratorio de los datos y transformaciones sobre los campos

5. **[Modelado](https://github.com/cynurbal/song_popularity_prediction/blob/main/5-modeling.ipynb)**

Análisis de modelos de aprendizaje automatizado y evaluación de métricas. Generación de pickle del modelo

6. **[Aplicación de usuario](https://github.com/cynurbal/song_popularity_prediction/blob/main/spotify_model_predict/spotify_predict.py)**

Aplicación usuario desarollada en Streamlit

Para ejecutar la aplicación deberá ejecutar el siguiente comando en su terminal desde la carpeta spotify_model_predict

```
streamlit run spotify_predict.py
```