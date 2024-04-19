# Capstone Project Documentation

## Project Overview
The capstone project involves crawling data from Billboard's website to obtain information about the top 10 artists. Using Spotify's API, we extract additional details about these artists, including their albums and tracks. The extracted data is then stored in CSV files and loaded into an Amazon S3 bucket. Finally, dimensional tables are created in Amazon Redshift, and the data is copied from S3 into these tables.

## Process Overview
### Crawling Data from Billboard:
- We crawl Billboard's website to obtain information about the top 10 artists.
- The crawled data includes the names of the top artists.

### Using Spotify API:
- We utilize Spotify's API to search for each artist obtained from Billboard.
- With the Spotify API, we extract the unique artist ID for each artist.

### Extracting Albums and Tracks:
- Using the artist IDs obtained from Spotify, we extract information about the albums of each artist.
- We limit the extraction to the first 10 albums of each artist.
- For each album, we extract information about its tracks.

### Storing Data in CSV Files:
- The extracted data, including information about artists, albums, and tracks, is stored in CSV files.
- Each type of data (artists, albums, tracks) has its own CSV file.

### Loading Data into Amazon S3:
- The CSV files containing the extracted data are uploaded to an Amazon S3 bucket.
- The bucket serves as a centralized storage location for the project's data.

### Creating Dimensional Tables in Redshift:
- Dimensional tables are created in Amazon Redshift to organize and structure the data.
- The schema of the dimensional tables depends on the nature of the data and the analysis requirements.

### Copying Data from S3 to Redshift:
- Using SQL's COPY command, we copy the data from the CSV files stored in Amazon S3 into the corresponding dimensional tables in Amazon Redshift.
- Proper mappings are established between the CSV columns and the columns in the Redshift tables.

## SQL Placeholder Codes
### Create Dimensional Tables
```sql
-- Placeholder SQL for creating dimensional tables in Redshift

-- Create artist dimension table
CREATE TABLE artist_dim (
    artist_id INT PRIMARY KEY,
    artist_name VARCHAR(255),
    followers INT,
    artist_popularity INT,
    artist_genre VARCHAR(255),
    artist_total_albums INT
);

-- Create album dimension table
CREATE TABLE album_dim (
    album_id INT PRIMARY KEY,
    album_name VARCHAR(255),
    album_type VARCHAR(50),
    total_tracks INT,
    album_release_date DATE,
    album_uri VARCHAR(255),
    album_artist_id INT REFERENCES artist_dim(artist_id)
);

-- Create track dimension table
CREATE TABLE track_dim (
    track_id INT PRIMARY KEY,
    track_name VARCHAR(255),
    danceability FLOAT,
    energy FLOAT,
    key INT,
    loudness FLOAT,
    mode INT,
    speachiness FLOAT,
    acousticness FLOAT,
    instrumentalness FLOAT,
    liveness FLOAT,
    valence FLOAT,
    tempo FLOAT,
    time_signature INT,
    duration FLOAT,
    album_id INT REFERENCES album_dim(album_id)
);
```

### Copy Data from S3 to Redshift
```sql
-- Placeholder SQL for copying data from S3 to Redshift

-- Copy data from CSV files in S3 to artist dimension table
COPY artist_dim
FROM 's3://your-bucket/artist_table.csv'
IAM_ROLE 'arn:aws:iam::123456789012:role/your-redshift-role'
CSV
IGNOREHEADER 1;

-- Copy data from CSV files in S3 to album dimension table
COPY album_dim
FROM 's3://your-bucket/album_table.csv'
IAM_ROLE 'arn:aws:iam::123456789012:role/your-redshift-role'
CSV
IGNOREHEADER 1;

-- Copy data from CSV files in S3 to track dimension table
COPY track_dim
FROM 's3://your-bucket/track_table.csv'
IAM_ROLE 'arn:aws:iam::123456789012:role/your-redshift-role'
CSV
IGNOREHEADER 1;
```


### Conclusion
This documentation outlines the process of crawling data from Billboard, extracting additional details from Spotify, storing the data in CSV files, and loading it into Amazon S3. It also includes the creation of dimensional tables in Amazon Redshift and the copying of data from S3 into these tables using SQL commands.
