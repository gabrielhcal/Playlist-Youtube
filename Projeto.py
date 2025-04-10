import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import time

CLIENT_ID = 'CLIENT ID'   #Inserir aqui seu client id do Spotify
CLIENT_SECRET = 'CLIENT SECRET'  #Inserir aqui seu client secret do Spotify

client_credentials_manager = SpotifyClientCredentials(client_id=CLIENT_ID, client_secret=CLIENT_SECRET)
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

def get_playlist_data(playlist_id, file_music):
    playlist = sp.playlist_tracks(playlist_id)
    
    with open(file_music, 'w', encoding='utf-8') as f:
        for num, item in enumerate(playlist['items']):
            track = item['track']
            track_name = track['name']
            artist_name = ', '.join(artist['name'] for artist in track['artists'])
            
            line = f"{track_name} - {artist_name}\n"
            f.write(line) 
    
link_playlist = input('Insira o URL da playlist do Spotify: ')
link_playlist_strip = link_playlist.strip()

start = link_playlist_strip.find('playlist/') + len('playlist/')
end = link_playlist_strip.find('?')

playlist_id = link_playlist_strip[start:end] if end != -1 else link_playlist_strip[start:]

print("ID da Playlist:", playlist_id)
file_music = 'playlist.txt'
get_playlist_data(playlist_id, file_music)
print(f"\nOs dados foram salvos no arquivo: {file_music}")

SCOPES = ['https://www.googleapis.com/auth/youtube.force-ssl']
CLIENT_SECRET_FILE = 'CREDENCIAL DO GOOGLE'    #Inserir aqui o doc com a credencial do Google
API_NAME = 'youtube'
API_VERSION = 'v3'

def authenticate_youtube():
    flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRET_FILE, SCOPES)
    creds = flow.run_local_server(port=57084, access_type='offline')
    youtube = build(API_NAME, API_VERSION, credentials=creds)
    return youtube

def create_playlist(youtube, title, description):
    request = youtube.playlists().insert(
        part="snippet,status",
        body={
            "snippet": {
                "title": title,
                "description": description
            },
            "status": {
                "privacyStatus": "private"
            }
        }
    )
    response = request.execute()
    return response['id']

def search_video(youtube, query):
    request = youtube.search().list(
        part="snippet",
        q=query,
        type="video",
        maxResults=1
    )
    response = request.execute()
    video_id = response['items'][0]['id']['videoId']
    return video_id

def add_video_to_playlist(youtube, playlist_id, video_id):
    try:
        request = youtube.playlistItems().insert(
            part="snippet",
            body={
                "snippet": {
                    "playlistId": playlist_id,
                    "resourceId": {
                        "kind": "youtube#video",
                        "videoId": video_id
                    }
                }
            }
        )
        request.execute()
        print(f"Vídeo {video_id} adicionado com sucesso.")
    except HttpError as error:
        if error.resp.status == 409:
            print(f"Erro 409: O serviço está indisponível ou você atingiu o limite de requisições.")
        else:
            print(f"Erro ao adicionar vídeo {video_id}: {error}")
        time.sleep(5)

def read_playlist_file(file_music):
    with open(file_music, 'r', encoding='utf-8') as f:
        songs = f.readlines()
    return [song.strip() for song in songs]

def create_youtube_playlist_from_spotify(file_music, playlist_title, playlist_description):
    youtube = authenticate_youtube()
    
    playlist_id = create_playlist(youtube, playlist_title, playlist_description)
    songs = read_playlist_file(file_music)
    
    for song in songs:
        print(f"Procurando: {song}")
        video_id = search_video(youtube, song)
        add_video_to_playlist(youtube, playlist_id, video_id)
        print(f"Adicionado: {song}")
    print(f"Playlist criada com sucesso! ID: {playlist_id}")

create_youtube_playlist_from_spotify('playlist.txt', 'Minha Playlist', 'Playlist criada a partir do Spotify')