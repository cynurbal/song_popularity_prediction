import streamlit as st
import pandas as pd
import numpy as np
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import polarplot
import pickle

#variable entorno
cid ="7b90adf482154140bb2ff823fddff587"
secret = "7b03b5d482a84fd08aa92a9051c8e8e8"

# extraer archivo pickle
with open('gb_clf.pkl', 'rb') as li:
    gb_clf = pickle.load(li)

def main():  

    spotify = spotipy.Spotify(client_credentials_manager=SpotifyClientCredentials(client_id=cid, 
                                                                                client_secret=secret, requests_timeout = 100))

    st.image('https://upload.wikimedia.org/wikipedia/commons/thumb/e/ea/Spotify_logo_vertical_black.jpg/1200px-Spotify_logo_vertical_black.jpg', width=60)
    st.header('Prediciendo Popularidad de una Canción - Spotify')

    search_choices =['Canción', 'Artista']
    search_selected = st.sidebar.selectbox("Seleccionar un opción", search_choices)

    search_keyword = st.text_input(search_selected + " (Introduzca la palabra a buscar)")
    button_clicked = st.button("Buscar")


    search_results = []
    artists = []
    
    if search_keyword is not None and len(str(search_keyword)) > 0:
        if search_selected == 'Canción':
            #st.write("Inicia la búsqueda de canciones")
            tracks = spotify.search(q='track:'+ search_keyword,type='track', limit=20)
            tracks_list = tracks['tracks']['items']
            if len(tracks_list) > 0:
                for track in tracks_list:
                    search_results.append(track['name'] + " - " + track['artists'][0]['name'])

       
        elif search_selected == 'Artista':
            #st.write("Inicia la búsqueda de artistas")
            artists = spotify.search(q='artist:'+ search_keyword, type='artist', limit=20)
            artists_list = artists['artists']['items']
            if len(artists_list) > 0:
                for artist in artists_list:
                    search_results.append(artist['name'])
            
    selected_album = None
    selected_artist = None

    if search_selected == 'Canción':
        selected_track = st.selectbox("Seleccione una canción: ", search_results)
    elif search_selected == 'Artista':
        selected_artist = st.selectbox("Seleccione un artista: ", search_results)
    elif search_selected == 'Album':
        selected_album = st.selectbox("Select your album: ", search_results)        

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
            track_features  = spotify.audio_features(track_id) 
            if track_features[0] is not None:
                df = pd.DataFrame(track_features, index=[0])
                df_features = df.loc[: ,['danceability', 'energy', 'instrumentalness', 'speechiness', 'liveness', 'loudness', 'acousticness', 'valence', 
                            'duration_ms', 'key', 'mode', 'tempo', 'time_signature']]
                df_track_info = pd.json_normalize(spotify.track(track_id))[['explicit', 'popularity']]
                df_track_followers = pd.DataFrame(data=artist_followers, columns=['followers_artist_1'])
                df_features_final = pd.concat([df_features, df_track_followers, df_track_info], axis=1)
                with st.container():
                    col1, col2 = st.columns((1,7))
                    with col1:
                        st.image(img_album, width=80)
                    with col2:
                        st.audio(preview_url, format="audio/mp3") 
                st.dataframe(df_features)
            else:
                st.write("La canción no tiene análisis de audio")      
        else:
            st.write("Por favor seleccione una canción de la lista")

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
                    artist_followers.append(artist['followers']['total'])
        
        if artist_id is not None:
            artist_uri = 'spotify:artist:' + artist_id
            top_songs_result = spotify.artist_top_tracks(artist_id)    
            df_features_final =  None

            for track in top_songs_result['tracks']:
                with st.container():
                    col1, col2, col3 = st.columns((4,4,2))
                    col11, col12 = st.columns((10,2))
                    col21, col22 = st.columns((11,1))
                    col31, col32 = st.columns((11,1))
                    #col1.write(track['id'])
                    col1.image(track['album']['images'][0]['url'], width=80)  
                    col2.write(track['name'])
                    if track['preview_url'] is not None:
                        #col11.write(track['preview_url'])  
                        #col11.image(track['album']['images'][0]['url'], width=80)  
                        with col11:   
                            st.audio(track['preview_url'], format="audio/mp3")  
                    with col3:
                        def feature_requested():
                            track_features  = spotify.audio_features(track['id']) 
                            df = pd.DataFrame(track_features, index=[0])
                            df_features = df.loc[: ,['danceability', 'energy', 'instrumentalness', 'speechiness', 'liveness', 'loudness', 'acousticness', 'valence', 
                            'duration_ms', 'key', 'mode', 'tempo', 'time_signature']]
                            track_info = spotify.track(track['id'])
                            df_track_info = pd.json_normalize(track_info)[['explicit', 'popularity']]
                            df_track_followers = pd.DataFrame(data=artist_followers, columns=['followers_artist_1'])
                            df_features_final = pd.concat([df_features, df_track_followers, df_track_info], axis=1)
                            with col21:
                                st.dataframe(df_features_final)
                            return df_features_final
                        df_features_final[track['id']] = feature_requested()                       

                        #with col31:
                        #    polarplot.feature_plot(df_features)
                            #feature_button_state = st.button('Predecir', key=track['id'], on_click=predict)
            st.button('predecir', key=track['id'], on_click=predict(df_features_final[track['id']]))
                                                   
                    #    feature_button_state = st.button('Track Audio Features', key=track['id'], on_click=feature_requested)



    def features():
        data ={
            'danceability': [0.878],
            'energy': [0.575],
            'instrumentalness': [0.00000],
            'speechiness': [0.2840],
            'liveness': [0.2730],
            'explicit': [True],
            'loudness': [-8732],
            'valence': [0.3990],
            'tempo': [144918],
            'popularity_artist_1': [86],
            'key_0.0': [0],
            'key_1.0': [0],
            'key_2.0': [0],
            'key_3.0': [0],
            'key_4.0': [0],
            'key_5.0': [0],
            'key_6.0': [0],
            'key_7.0': [0],
            'key_8.0': [0],
            'key_9.0': [1],
            'key_10.0': [0],
            'key_11.0': [0],
            'mode_0.0': [0],
            'mode_1.0': [1],
            'time_signature_0.0': [0],
            'time_signature_1.0': [0],
            'time_signature_3.0': [0],
            'time_signature_4.0': [1],
            'time_signature_5.0': [0],
            'duration_m': [3086883]
            }
        features = pd.DataFrame(data, index=[0])
        #st.success(gb_clf.predict(df))
        return features


    
    #if st.button('RUN'):
   
def predict(df_features_final):
    print('************* entra predict')
    df_features = prepare_feature(df_features_final)

    with st.sidebar.container():
        st.success(gb_clf.predict(df_features_final))     

def prepare_feature(df_features_final):
    df_features = df_features_final

    df_features['duration_m'] = round(df_features['duration_ms']/60000, 2)
    df_features = df_features.drop(['duration_ms'], axis=1)

    df_features['key'] = df_features['key'].astype('category')
    df_features['mode'] = df_features['mode'].astype('category')
    df_features['time_signature'] = df_features['time_signature'].astype('category')

    df_features = pd.get_dummies(df_features)

    print(df_features.columns)

    return df_features

if __name__ == '__main__':
    main()