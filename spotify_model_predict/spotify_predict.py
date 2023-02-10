import streamlit as st
import pandas as pd
import numpy as np
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import pickle
import json

# lectura archivo pickle
with open('gb_clf.pkl', 'rb') as li:
    model = pickle.load(li)

# Leyendo credenciales de Spotify web API del fichero settings.env
with open('settings.env') as f:
    env_vars = json.loads(f.read())


def main():  

    spotify = spotipy.Spotify(client_credentials_manager=SpotifyClientCredentials(client_id=env_vars['cid'], 
                                                                                client_secret=env_vars['secret'], requests_timeout = 100))

    st.image('https://upload.wikimedia.org/wikipedia/commons/thumb/e/ea/Spotify_logo_vertical_black.jpg/1200px-Spotify_logo_vertical_black.jpg', width=60)
    st.header('Prediciendo Popularidad de una Canción - Spotify')

    search_choices =['Canción', 'Artista']
    search_selected = st.sidebar.selectbox("Seleccionar un opción", search_choices)

    search_keyword = st.text_input(search_selected + " (Introduzca la palabra a buscar)")
    button_clicked = st.button("Buscar")


    search_results = []
    search_tracks = []
    artists = []
    
    if search_keyword is not None and len(str(search_keyword)) > 0:
        if search_selected == 'Canción':
            tracks = spotify.search(q='track:'+ search_keyword,type='track', limit=20)
            tracks_list = tracks['tracks']['items']
            if len(tracks_list) > 0:
                for track in tracks_list:
                    search_results.append(track['name'] + " - " + track['artists'][0]['name'])

       
        elif search_selected == 'Artista':
            artists = spotify.search(q='artist:'+ search_keyword, type='artist', limit=20)
            artists_list = artists['artists']['items']
            if len(artists_list) > 0:
                for artist in artists_list:
                    search_results.append(artist['name'])
            
    selected_track = None
    selected_artist = None

    if search_selected == 'Canción':
        selected_track = st.selectbox("Seleccione una canción: ", search_results)
    elif search_selected == 'Artista':
        selected_artist = st.selectbox("Seleccione un artista: ", search_results) 

    # busquedad por cancion
    if selected_track is not None and len(tracks) > 0:
        tracks_list = tracks['tracks']['items']
        track_id = None

        if len(tracks_list) > 0:
            for track in tracks_list:  
                str_temp = track['name'] + " - " + track['artists'][0]['name']
                if str_temp == selected_track:
                    track_id = track['id']
                    track_album = track['album']['name']
                    img_album = track['album']['images'][0]['url']
                    preview_url = track['preview_url']
        
        if track_id is not None:
            # se extraen caracteristiscas de la cancion
            track_features  = spotify.audio_features(track_id) 
            if track_features[0] is not None:
                df = pd.DataFrame(track_features, index=[0])
                df_features = df.loc[: ,['danceability', 'energy', 'instrumentalness', 'speechiness', 'liveness', 'loudness', 'acousticness', 'valence', 
                            'duration_ms', 'key', 'mode', 'tempo', 'time_signature']]
                df_track_info = pd.json_normalize(spotify.track(track_id))[['explicit', 'popularity','artists','album.release_date']]
                df_track_info['release_year'] = df_track_info['album.release_date'].str[0:4]
                
                df_artists = df_track_info['artists'][0]
                artist_id = pd.json_normalize(df_artists)['id'][0]
                df_artist_info = pd.json_normalize(spotify.artist(artist_id))
                df_artist_followers = df_artist_info[['followers.total']]
                df_artist_followers.columns= ['followers_artist_1']

                df_features_final = pd.concat([df_features, df_track_info[['explicit', 'popularity', 'release_year']], df_artist_followers], axis=1)

                def predict():
                    #llamada a modelo de prediccion
                    predict_model(df_features_final)
                
                with st.container():
                    col1, col2 = st.columns((1,7))
                    with col1:
                        st.image(img_album, width=80)
                    with col2:
                        st.audio(preview_url, format="audio/mp3") 
                       
                st.dataframe(df_features_final)
                st.button('predecir', key=track['id'], on_click=predict)
                
            else:
                st.write("La canción no tiene análisis de audio")      
        else:
            st.write("Por favor seleccione una canción de la lista")

    # busqueda por artista
    elif selected_artist is not None and len(artists) > 0:
        artists_list = artists['artists']['items']
        artist_id = None
        artist_uri = None
        artist_followers = []
        selected_artist_choice = None

        
        if len(artists_list) > 0:
            for artist in artists_list:
                if selected_artist == artist['name']:
                    artist_id = artist['id']
                    artist_uri = artist['uri']
                    artist_followers = artist['followers']['total']
              
        if artist_id is not None:
            # listado de canciones a seleccionar
            top_songs_result = spotify.artist_top_tracks(artist_id)  
            tracks_list = top_songs_result['tracks']
            if len(top_songs_result) > 0:
                for track in tracks_list:
                    search_tracks.append(track['name'] + "+" + track['id'])
            
            selected_track = st.selectbox("Seleccione una canción: ", search_tracks) 

            if (selected_track is not None):
                # busqueda de caracteristicas de cancion seleccionada
                track_id = selected_track.split("+")[1]           
                track = spotify.track(track_id)

                with st.container():
                    col1, col2, col3 = st.columns((4,4,2))
                    col11, col12 = st.columns((10,2))
                    col21, col22 = st.columns((11,1))
                    col31, col32 = st.columns((11,1))
                        
                    col1.image(track['album']['images'][0]['url'], width=80)  
                    col2.write(track['name'])

                    if track['preview_url'] is not None:
                        with col11:   
                            st.audio(track['preview_url'], format="audio/mp3")  
                    with col3:
                        track_features  = spotify.audio_features(track_id) 
                        df = pd.DataFrame(track_features, index=[0])
                        df_features = df.loc[: ,['danceability', 'energy', 'instrumentalness', 'speechiness', 'liveness', 'loudness', 'acousticness', 'valence', 
                        'duration_ms', 'key', 'mode', 'tempo', 'time_signature']]

                        df_track_info = pd.DataFrame(data= {'explicit': [track['explicit']], 
                                                            'popularity': [track['popularity']], 
                                                            'release_date': [track['album']['release_date']]})
                        df_track_info['release_year'] = df_track_info['release_date'].str[0:4]

                        df_track_followers = pd.DataFrame(data=[artist_followers], columns=['followers_artist_1'])
                        df_features_final = pd.concat([df_features, df_track_followers, df_track_info[['explicit', 'popularity', 'release_year']]], axis=1)
                
                        def predict():
                            # llamada a modelo de prediccion
                            predict_model(df_features_final)

                        with col21:
                            st.dataframe(df_features_final) 
                            feature_button_state = st.button('predecir', key=track_id, on_click=predict)


# metodo de llamada al modelo de prediccion   
def predict_model(df):  
    features = prepare_feature(df)

    with st.sidebar.container():
        st.success(classify(model.predict(features))) 

# metodo de traduccion del resultado del modelo   
def classify(num):
    if num == '0':
        return 'Popularidad BAJA'
    elif num == '1':
        return 'Popularidad MEDIA'
    elif num == '2':
        return 'Popularidad ALTA'
    else: return 'Valor no esperado'  

# metodo de preparacion de dataset para la prediccion
def prepare_feature(df):
    
    df_features = df

    df_features = df_features.drop(['popularity'], axis=1) 

    df_features['duration_m'] = round(df_features['duration_ms']/60000, 2)
    df_features = df_features.drop(['duration_ms'], axis=1)

    df_features['key_0.0'] = np.where(df_features['key']== 0, 1, 0)
    df_features['key_1.0'] = np.where(df_features['key']== 1, 1, 0)
    df_features['key_2.0'] = np.where(df_features['key']== 2, 1, 0)
    df_features['key_3.0'] = np.where(df_features['key']== 3, 1, 0)
    df_features['key_4.0'] = np.where(df_features['key']== 4, 1, 0)
    df_features['key_5.0'] = np.where(df_features['key']== 5, 1, 0)
    df_features['key_6.0'] = np.where(df_features['key']== 6, 1, 0)
    df_features['key_7.0'] = np.where(df_features['key']== 7, 1, 0)
    df_features['key_8.0'] = np.where(df_features['key']== 8, 1, 0)
    df_features['key_9.0'] = np.where(df_features['key']== 9, 1, 0)
    df_features['key_10.0'] = np.where(df_features['key']== 10, 1, 0)
    df_features['key_11.0'] = np.where(df_features['key']== 11, 1, 0)
    df_features = df_features.drop(['key'], axis=1) 

    df_features['mode_0.0'] = np.where(df_features['mode']== 0, 1, 0)
    df_features['mode_1.0'] = np.where(df_features['mode']== 1, 1, 0)
    df_features = df_features.drop(['mode'], axis=1) 

    df_features['time_signature_0.0'] = np.where(df_features['time_signature']== 0, 1, 0)
    df_features['time_signature_1.0'] = np.where(df_features['time_signature']== 1, 1, 0)
    df_features['time_signature_3.0'] = np.where(df_features['time_signature']== 3, 1, 0)
    df_features['time_signature_4.0'] = np.where(df_features['time_signature']== 4, 1, 0)
    df_features['time_signature_5.0'] = np.where(df_features['time_signature']== 5, 1, 0)
    df_features = df_features.drop(['time_signature'], axis=1) 

    fields = ['danceability', 'energy', 'instrumentalness', 'speechiness', 'liveness',
       'explicit', 'loudness', 'valence', 'tempo', 'followers_artist_1',
       'release_year', 'key_0.0', 'key_1.0', 'key_2.0', 'key_3.0', 'key_4.0',
       'key_5.0', 'key_6.0', 'key_7.0', 'key_8.0', 'key_9.0', 'key_10.0',
       'key_11.0', 'mode_0.0', 'mode_1.0', 'time_signature_0.0',
       'time_signature_1.0', 'time_signature_3.0', 'time_signature_4.0',
       'time_signature_5.0', 'duration_m']

    return (df_features[fields].to_numpy())

if __name__ == '__main__':
    main()