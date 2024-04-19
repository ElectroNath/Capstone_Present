# Capstone Project Documentation

## Project Overview
The capstone project involved crawling data from Billboard's website to obtain information about the top 10 artists. Using Spotify's API, we extracted additional details about these artists, including their albums and tracks. The extracted data was then stored in CSV files and loaded into an Amazon S3 bucket. Finally, dimensional tables were created in Amazon Redshift, and the data was copied from S3 into these tables.

## Process Overview

### Crawling Data from Billboard:
- We crawled Billboard's website to obtain information about the top 10 artists.
- The crawled data included the names of the top artists.

### Using Spotify API:
- Spotify's API was utilized to search for each artist obtained from Billboard.
- With the Spotify API, we extracted the unique artist ID for each artist.

### Extracting Albums and Tracks:
- Using the artist IDs obtained from Spotify, we extracted information about the albums of each artist.
- The extraction was limited to the first 10 albums of each artist.
- For each album, information about its tracks was extracted.

### Storing Data in CSV Files:
- The extracted data, including information about artists, albums, and tracks, was stored in CSV files.
- Each type of data (artists, albums, tracks) had its own CSV file.

### Loading Data into Amazon S3:
- The CSV files containing the extracted data were uploaded to an Amazon S3 bucket.
- The bucket served as a centralized storage location for the project's data.

### Creating Dimensional Tables in Redshift:
- Dimensional tables were created in Amazon Redshift to organize and structure the data.
- The schema of the dimensional tables depended on the nature of the data and the analysis requirements.

## Dimensionality of the Data
Dimensional tables in Amazon Redshift were designed to organize and structure the data in a way that facilitated efficient querying and analysis. In this project, dimensional tables were created to represent key entities such as artists, albums, and tracks.

- **Artist Dimension Table**: This table contained information about each artist, including their unique identifier (artist_id), name (artist_name), number of followers, popularity score, genre, and total number of albums.

- **Album Dimension Table**: The album dimension table stored details about each album, such as its unique identifier (album_id), name (album_name), type (album_type), total number of tracks, release date (album_release_date), URI, and the artist ID it belonged to (album_artist_id).

- **Track Dimension Table**: This table held information about each track, including its unique identifier (track_id), name (track_name), various audio features like danceability, energy, key, loudness, mode, speechiness, acousticness, instrumentalness, liveness, valence, tempo, time signature, and duration. It also referenced the album ID it belonged to (album_id).

By organizing the data into dimensional tables, a structured schema was created that enabled efficient querying and analysis based on different attributes of the artists, albums, and tracks. This dimensional modeling approach helped in simplifying complex data relationships and optimizing query performance for analytical purposes.

### Copying Data from S3 to Redshift:
- Using SQL's COPY command, the data was copied from the CSV files stored in Amazon S3 into the corresponding dimensional tables in Amazon Redshift.
- Proper mappings were established between the CSV columns and the columns in the Redshift tables.

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
