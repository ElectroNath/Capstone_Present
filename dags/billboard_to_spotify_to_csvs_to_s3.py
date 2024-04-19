try:
  
  import os
  import re
  import requests
  import spotipy
  import pandas as pd
  from pprint import pprint
  from dotenv import load_dotenv
  from datetime import timedelta, datetime
  from spotipy.oauth2 import SpotifyClientCredentials
  
  from airflow import DAG
  from airflow.hooks.S3_hook import S3Hook
  from airflow.operators.python import PythonOperator
  from airflow.operators.python_operator import PythonOperator

  # Load environment variables from .env file
  load_dotenv()
  
except Exception as e: print(f'Error: {e}')


CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
BUCKET = '10alytics-cap-bucket'
TOP_10_ARTISTS = []



# Authenticating my Spotify App API with neccesary auth args for the credentials codeflow
print('Authenticating User...\n\n')
client_credentials_manager = SpotifyClientCredentials(client_id=CLIENT_ID, client_secret=CLIENT_SECRET)
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)




# Creating the placholder dictionary
tracks_data = {
    'track_name': [], 'track_id': [],
    'danceabiltiy': [], 'energy': [], 'key': [],
    'loudness': [], 'mode': [],'speachiness': [],
    'acousticness': [], 'instrumentalness': [], 'liveness': [],
    'valence': [], 'tempo': [], 'time_signature': [],
    'duration': [], 'album_name': [], 'album_id': []
}

artist_data = {'artist_id': [], 'followers': [],
               'artist_name': [], 'artist_popularity': [],
               'artist_genre': [], 'artist_total_albums': []
              }

album_data = {'album_type': [], 'total_tracks': [],
               'album_id': [], 'album_name': [],
               'album_release_date': [], 'album_uri': [],
               'album_artist_id': [], 'album_artist_name': []
            }



# [START crawling function series]
def page_content(url):
    r = requests.get(url)
    html_text = r.text
    html_text = re.sub("\s+", " ", html_text)
    return html_text


def get_top_artist(**kwargs):
    print('getting top artist')
    html_content = page_content('https://www.billboard.com/charts/artist-100/')
    list_regex = re.compile(r'<h3\s+id=\"title-of-a-story\"\s+class=\"c-title\s+a-no-trucate[^\"]*\">(.*?)<\/h3>')
    artist_list = re.findall(list_regex, html_content)
    print('TOP ARTISTS CRAWLED')
    kwargs['ti'].xcom_push(key='artist_list', value=artist_list[:10])
    # return artist_list
# [END crawling function series]



# [START spotify to csv extraction function]
def Spotify_to_CSV(data, **kwargs):
    
    # Get the list of top artistnames as from xcom
    top_artists = kwargs['ti'].xcom_pull(key='artist_list', task_ids='top_10_billboard_artist')
    print("GOT THE TOP ARTISTS DAT FROM XCOM")
    
    
    # GET THE ARTIST IDS & DATA
    print('GETTING ARTISTS BIO DATA')
    for artist in top_artists:
        s_artist = sp.search(q=artist, type='artist', limit=1)
        artist_id = s_artist['artists']['items'][0]['id']
        art = s_artist['artists']['items'][0]
        TOP_10_ARTISTS.append(artist_id)
        artist_data['artist_id'].append(artist_id)
        artist_data['followers'].append(art['followers']['total'])
        artist_data['artist_name'].append(art['name'])
        artist_data['artist_popularity'].append(art['popularity'])
        artist_data['artist_genre'].append(art['genres'])
        artist_name = art['name']
        
        
        # GET ALBUMS OF ARTISTS
        print('GETTING ARTISTS ALBUMS DATA')
        artist_albm = sp.artist_albums(artist_id)
        # quickly adding an extra information to artist_data
        artist_data['artist_total_albums'].append(artist_albm['total'])
        total_albums = artist_albm['total']
        
        print(f'{artist_name} has appeared on a total of {total_albums} albums')
        
        # back to getting albumsinformation
        all_albums = artist_albm['items']
        print(' Now stagging the albums ...')
        while artist_albm['next']:
            artist_albm = sp.next(artist_albm)
            all_albums.extend(artist_albm['items'])
            
        print(f' {artist_name} albums stagged ...', '\n\n')
        
        print(f' transforming {artist_name} albums data ...', '\n\n')

        for index, album in enumerate(all_albums[:10]):
            album_data['album_type'].append(album['album_type'])
            album_data['total_tracks'].append(album['total_tracks'])
            album_data['album_id'].append(album['id'])
            album_data['album_name'].append(album['name'])
            album_data['album_release_date'].append(album['release_date'])
            album_data['album_uri'].append(album['uri'])
            album_data['album_artist_id'].append(album['artists'][0]['id'])
            album_data['album_artist_name'].append(album['artists'][0]['name'])
            album_name = album['name']
            
            
            
            # GET TRACKS OF ALBUM
            print('GETTING ALBUMS TRACKS DATA')
            album_tracks = sp.album_tracks(album['id'])
            all_tracks = album_tracks['items']
            
            print(' Now stagging the tracks ...')
            while album_tracks['next']:
                album_tracks=sp.next(album_tracks)
                all_tracks.extend(album_tracks['items'])
            
            print(f' {album_name} tracks stagged ...', '\n\n')
            
            print(f' transforming {album_name} tracks data ...', '\n\n')
            
            for index, track in enumerate(all_tracks[:10]):
                tracks_data['track_name'].append(track['name'])
                tracks_data['track_id'].append(track['id'])
                # print('i am here')
                track_features = sp.audio_features(track['uri'])
                # print('actually here')
            
                if track_features[0] is not None and len(track_features) > 0:
                    tracks_data['danceabiltiy'].append(track_features[0]['danceability'])
                    tracks_data['energy'].append(track_features[0]['energy'])
                    tracks_data['key'].append(track_features[0]['key'])
                    tracks_data['loudness'].append(track_features[0]['loudness'])
                    tracks_data['mode'].append(track_features[0]['mode'])
                    tracks_data['speachiness'].append(track_features[0]['speechiness'])
                    tracks_data['acousticness'].append(track_features[0]['acousticness'])
                    tracks_data['instrumentalness'].append(track_features[0]['instrumentalness'])
                    tracks_data['liveness'].append(track_features[0]['liveness'])
                    tracks_data['valence'].append(track_features[0]['valence'])
                    tracks_data['tempo'].append(track_features[0]['tempo'])
                    tracks_data['time_signature'].append(track_features[0]['time_signature'])
                    tracks_data['duration'].append(track_features[0]['duration_ms']/60000)
                else:
                    # Append None or any placeholder value for audio features
                    tracks_data['danceabiltiy'].append(None)
                    tracks_data['energy'].append(None)
                    tracks_data['key'].append(None)
                    tracks_data['loudness'].append(None)
                    tracks_data['mode'].append(None)
                    tracks_data['speachiness'].append(None)
                    tracks_data['acousticness'].append(None)
                    tracks_data['instrumentalness'].append(None)
                    tracks_data['liveness'].append(None)
                    tracks_data['valence'].append(None)
                    tracks_data['tempo'].append(None)
                    tracks_data['time_signature'].append(None)
                    tracks_data['duration'].append(None)
                    
                tracks_data['album_name'].append(album['name'])
                tracks_data['album_id'].append(album['id'])
        
        print(f'DONE WITH {artist_name} NOW MOVING TO NEXT ARTIST')
    
    

       
    artist_df = pd.DataFrame(album_data)
    artist_df.to_csv('csv_data/albums_table.csv', index = False)
    print("COVERTED ARTISTS DATA TO CSV")
    
    album_df = pd.DataFrame(artist_data)
    album_df.to_csv('csv_data/artists_table.csv', index = False)
    print("COVERTED ALBUMS DATA TO CSV")
    
    tracks_df = pd.DataFrame(tracks_data)
    tracks_df.to_csv('csv_data/track_table.csv', index = False)
    print("COVERTED TRACKS DATA TO CSV")




# [Start s3Upload task]
# def upload_csv_to_s3(csv_filenames):
#     print(str(csv_filenames) + 'are the files to be uploaded')
#     s3_hook = S3Hook("aws_conn")
#     project_name = "10alytics_Capstone_Project"
#     date_prefix = datetime.now().strftime("%Y-%m-%d")  # Current date as YYYY-MM-DD
#     s3_prefix = f"{project_name}/{date_prefix}"
#     print('created a prefix')

#     for csv_filename in csv_filenames:
#         print(csv_filename + 'is the files to be worked on now')
#         s3_key = f"{s3_prefix}/{csv_filename.split('/')[-1]}"
#         print(s3_key + '   and hooking the load function')
#         s3_hook.load_file(
#             filename=csv_filename,
#             key=s3_key,
#             bucket_name=BUCKET,
#             replace=True,  # Replace existing file if it exists
#         )
#         print(f"CSV file '{csv_filename}' uploaded to S3 bucket: s3://{BUCKET}/{s3_key}")
# [End s3Upload task]




# [start directory task]
def get_files_in_directory(directory):
    """
    Get all files in a directory.
    Args:
    - directory (str): Path to the directory.
    Returns:
    - files (list): List of file names in the directory.
    """
    files = []
    for file in os.listdir(directory):
        file_path = os.path.join(directory, file)
        print(file_path, '\n\n')
        print(file)
        if os.path.isfile(file_path):
            files.append(file_path)
    return files
    # # Push the list to XCom
    # kwargs['ti'].xcom_push(key='files_list', value=files)
# [End directory task]




# [Start s3Upload task]
# Function to upload CSV files to S3 bucket
def upload_csv_to_s3(bucket_name, csv_filenames):
    project_name = "10alyticsCapstone"
    date_prefix = datetime.now().strftime("%Y-%m-%d")  # Current date as YYYY-MM-DD
    s3_prefix = f"{project_name}/{date_prefix}"
    print('created a prefix')
    s3_hook = S3Hook("aws_conn")
    for csv_filename in csv_filenames:
        s3_key = f"{s3_prefix}/{csv_filename.split('/')[-1]}"
        s3_hook.load_file(
            filename=csv_filename,
            key=s3_key,
            bucket_name=bucket_name,
            replace=True,  # Replace existing file if it exists
        )
        print(f"CSV file '{csv_filename}' uploaded to S3 bucket: s3://{bucket_name}/{s3_key}")
# [End s3Upload task]



default_args = {
    'owner': 'Nathaniel Solomon',
    'depends_on_past': False,
    'start_date': datetime(2024, 3, 28),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 5,
    'retry_delay': timedelta(minutes=5)
}

  
with DAG(
  dag_id="billboard_to_spotify_to_s3_extractionV1",
  default_args = default_args,
  schedule_interval="@daily",
  catchup=False,
  tags = ['spotify', 'sptify_s3', 's3', 'billboard']
  ) as dag:


# [Start billboard extract task]
  get_top_10_artist = PythonOperator(
    task_id="top_10_billboard_artist",
    python_callable=get_top_artist, 
    # op_kwargs = {}
    provide_context=True
  )
# [End billboard extract task]



# [Start spotify extract task]
  extract_spotify2csv_task = PythonOperator(
    task_id="sptoify_to_csv",
    python_callable=Spotify_to_CSV, 
    op_kwargs = {'data': tracks_data},
    provide_context=True
  )
# [End spotify extract task]




  upload_csv_to_s3_task = PythonOperator(
      task_id="upload_csv_to_s3",
      python_callable=upload_csv_to_s3,
    #   op_kwargs={"csv_filenames": ['csv_data/spotify_track_data.csv'], 'bucket_name':BUCKET,
    #              },
      op_kwargs={"csv_filenames": get_files_in_directory('csv_data/'), 'bucket_name':BUCKET,
                 },
      provide_context=True
  )
# [End s3 upload task]




# Set task dependencies
get_top_10_artist >> extract_spotify2csv_task >> upload_csv_to_s3_task
