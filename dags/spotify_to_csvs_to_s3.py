try:
  
  import os
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
BUCKET = '10alytics-capstone-project'




# Authenticating my Spotify App API with neccesary auth args for the credentials codeflow
print('Authenticating User...\n\n')
client_credentials_manager = SpotifyClientCredentials(client_id=CLIENT_ID, client_secret=CLIENT_SECRET)
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)




# Creating the placholder dictionary
data = {
    'Track_Name': [], 'Track_Id': [], 'Popularity': [],
    'Danceabiltiy': [], 'Energy': [], 'Key': [], 'Loudness': [], 'Mode': [],
    'Speachiness': [], 'Acousticness': [],
    'Instrumentalness': [], 'Liveness': [], 'Valence': [], 'Tempo': [],
    'Time_Signature': [], 'Duration': [], 'Album_Name': [], 'Album_Id': [],
    'Album_Type': [], 'Album_Tracks_Count': [],
    'Album_Date': [], 'Artist_Name': [], 'Artist_Id': [],
    'Artist_Genres': [], 'Artist_Popularity': [],
    'Artist_Album_Count': [], 'Artist_Followers': []
}



# [START spotify to csv extraction function]
def Spotify_to_CSV(data):
    # Get the top tracks of the year 2024 in the United States
    print(f'The extract function has been executed and this is data in the next line')
    print('Initiating the Endpoint...')
    top_tracks = sp.search(q='year:2024', type='track', limit=50, market='US')
    tracks = top_tracks['tracks']['items']

    # Loop through multiple pages to get more results (if necessary)
    print('Extracting other available tracks')
    while top_tracks['tracks']['next']:
        top_tracks = sp.next(top_tracks['tracks'])
        tracks.extend(top_tracks['tracks']['items'])

    # Organizing the extracted information 
    for index, track in enumerate(tracks[:10]):
        print(f'Adding the values of index {index} into the appropriate Keys...')
        data['Track_Name'].append(track['name'])
        data['Track_Id'].append(track['id'])
        data['Popularity'].append(track['popularity'])
        track_features = sp.audio_features(track['uri'])
        if track_features[0] is not None and len(track_features) > 0:
            data['Danceabiltiy'].append(track_features[0]['danceability'])
            data['Energy'].append(track_features[0]['energy'])
            data['Key'].append(track_features[0]['key'])
            data['Loudness'].append(track_features[0]['loudness'])
            data['Mode'].append(track_features[0]['mode'])
            data['Speachiness'].append(track_features[0]['speechiness'])
            data['Acousticness'].append(track_features[0]['acousticness'])
            data['Instrumentalness'].append(track_features[0]['instrumentalness'])
            data['Liveness'].append(track_features[0]['liveness'])
            data['Valence'].append(track_features[0]['valence'])
            data['Tempo'].append(track_features[0]['tempo'])
            data['Time_Signature'].append(track_features[0]['time_signature'])
            data['Duration'].append(track_features[0]['duration_ms']/60000)
        else:
            # Append None or any placeholder value for audio features
            data['Danceabiltiy'].append(None)
            data['Energy'].append(None)
            data['Key'].append(None)
            data['Loudness'].append(None)
            data['Mode'].append(None)
            data['Speachiness'].append(None)
            data['Acousticness'].append(None)
            data['Instrumentalness'].append(None)
            data['Liveness'].append(None)
            data['Valence'].append(None)
            data['Tempo'].append(None)
            data['Time_Signature'].append(None)
            data['Duration'].append(None)   
        data['Album_Name'].append(track['album']['name'])
        data['Album_Id'].append(track['album']['id'])
        data['Album_Type'].append(track['album']['album_type'])
        data['Album_Tracks_Count'].append(track['album']['total_tracks'])
        data['Album_Date'].append(track['album']['release_date'])
        data['Artist_Name'].append(track['artists'][0]['name'])
        data['Artist_Id'].append(track['artists'][0]['id'])
        data['Artist_Genres'].append(sp.artist(track['artists'][0]['id'])['genres'])
        data['Artist_Popularity'].append(sp.artist(track['artists'][0]['id'])['popularity'])
        data['Artist_Album_Count'].append(sp.artist_albums(track['artists'][0]['id'])['total'])
        data['Artist_Followers'].append(sp.artist(track['artists'][0]['id'])['followers']['total'])
    
    print('Done Extracting...')
    
    data = pd.DataFrame(data)
    return data.to_csv('csv_data/spotify_track_data.csv', index = False)
# [END spotify to csv extraction function] 




# [Start s3Upload task]
def upload_csv_to_s3(csv_filenames):
    print(str(csv_filenames) + 'are the files to be uploaded')
    s3_hook = S3Hook("aws_conn")
    project_name = "10alytics_Capstone_Project"
    date_prefix = datetime.now().strftime("%Y-%m-%d")  # Current date as YYYY-MM-DD
    s3_prefix = f"{project_name}/{date_prefix}"
    print('created a prefix')

    for csv_filename in csv_filenames:
        print(csv_filename + 'is the files to be worked on now')
        s3_key = f"{s3_prefix}/{csv_filename.split('/')[-1]}"
        print(s3_key + '   and hooking the load function')
        s3_hook.load_file(
            filename=csv_filename,
            key=s3_key,
            bucket_name=BUCKET,
            replace=True,  # Replace existing file if it exists
        )
        print(f"CSV file '{csv_filename}' uploaded to S3 bucket: s3://{BUCKET}/{s3_key}")
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
    'retries': 5,
    'retry_delay': timedelta(minutes=2)
}

  
with DAG(
  dag_id="spotify_to_s3_extraction",
  default_args = default_args,
  start_date= datetime(2024, 3, 24), # or pendulum.datetime(2024, 3, 17, tz=”UTC”), 
  schedule_interval="@daily",
  catchup=False,
  tags = ['spotify', 'sptify_s3', 's3']
  ) as dag:
    
# [Start spotify extract task]
  extract_spotify2csv_task = PythonOperator(
    task_id="sptoify_to_csv",
    python_callable=Spotify_to_CSV, 
    op_kwargs = {'data': data}
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
extract_spotify2csv_task >> upload_csv_to_s3_task
