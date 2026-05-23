/* 
 * Click nbfs://nbhost/SystemFileSystem/Templates/Licenses/license-default.txt to change this license
 * Click nbfs://nbhost/SystemFileSystem/Templates/Other/SQLTemplate.sql to edit this template
 */
/**
 * Author:  Student
 * Created: 11 maj 2026
 */

 /*Deprecated version. Newer in dw-schema-new.sql*/

CREATE TABLE IF NOT EXISTS artist (
    artist_id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    artist TEXT CONSTRAINT art_constr CHECK ((char_length(artist) >=1) AND (char_length(artist) < 255)) NOT NULL
);
CREATE TABLE IF NOT EXISTS album (
    album_id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    artist_id bigint REFERENCES artist (artist_id) ON DELETE CASCADE NOT NULL,
    album TEXT CONSTRAINT album_constr CHECK ((char_length(album) >=1) AND (char_length(album) < 255)) NOT NULL,
    album_type TEXT CONSTRAINT al_type_constr CHECK (album_type IN ('single', 'compilation', 'album')) NOT NULL
);
CREATE TABLE IF NOT EXISTS youtube_channel (
    youtube_id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    channel TEXT CONSTRAINT ch_constr CHECK ((char_length(channel) >=1) AND (char_length(channel) < 255)) NOT NULL
);
CREATE TABLE IF NOT EXISTS streams_range (
    streams_range_id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    range int8range NOT NULL,
    start_val int NOT NULL,
    end_val int NOT NULL,
    nice_name TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS views_range (
    views_range_id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    range int8range NOT NULL,
    start_val int NOT NULL,
    end_val int NOT NULL,
    nice_name TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS comments_range (
    comments_range_id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    range int8range NOT NULL,
    start_val int NOT NULL,
    end_val int NOT NULL,
    nice_name TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS likes_range (
    likes_range_id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    range int8range NOT NULL,
    start_val int NOT NULL,
    end_val int NOT NULL,
    nice_name TEXT NOT NULL
);

CREATE OR REPLACE FUNCTION float4_diff(x float4, y float4) RETURNS float8 AS
'SELECT (x - y)::float8' LANGUAGE sql IMMUTABLE;

DROP TYPE IF EXISTS float4range CASCADE;

CREATE TYPE float4range AS RANGE (
    subtype = float4,
    subtype_diff = float4_diff --,
   -- start_val float NOT NULL,
   -- end_val float NOT NULL,
   -- nice_name TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS danceability_range (
    danceability_range_id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    danceability_range_type float4range NOT NULL,
    start_val float NOT NULL,
    end_val float NOT NULL,
    nice_name TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS energy_range (
    energy_range_id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    energy_range float4range,
    start_val float NOT NULL,
    end_val float NOT NULL,
    nice_name TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS loudness_range (
    loudness_range_id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    loudness_type float4range NOT NULL,
    start_val float NOT NULL,
    end_val float NOT NULL,
    nice_name TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS speechiness_range (
    speechiness_range_id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    speechiness_range float4range,
    start_val float NOT NULL,
    end_val float NOT NULL,
    nice_name TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS acousticness_range (
    acousticness_range_id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    acousticness_type float4range NOT NULL,
    start_val float NOT NULL,
    end_val float NOT NULL,
    nice_name TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS liveness_range (
    liveness_range_id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    liveness_range float4range,
    start_val float NOT NULL,
    end_val float NOT NULL,
    nice_name TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS valence_range (
    valence_range_id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    valence_type float4range NOT NULL,
    start_val float NOT NULL,
    end_val float NOT NULL,
    nice_name TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS tempo_range (
    tempo_range_id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    tempo_range float4range,
    start_val float NOT NULL,
    end_val float NOT NULL,
    nice_name TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS acousticness_range (
    acousticness_range_id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    acousticness_range float4range,
    start_val float NOT NULL,
    end_val float NOT NULL,
    nice_name TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS instrumentalness_range (
    instrumentalness_range_id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    instrumentalness_range float4range,
    start_val float NOT NULL,
    end_val float NOT NULL,
    nice_name TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS energyliveness_range (
    energyliveness_range_id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    energyliveness_range float4range,
    start_val float NOT NULL,
    end_val float NOT NULL,
    nice_name TEXT NOT NULL
);

-- GOD OBJECT
CREATE TABLE IF NOT EXISTS track (
    -- PRIMARY KEY
    track_id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    -- Youtube stats
    artist_id bigint REFERENCES artist (artist_id) ON DELETE CASCADE NOT NULL,
    streams_spotify_range bigint REFERENCES streams_range (streams_range_id) NOT NULL,
    views_youtube_range bigint REFERENCES views_range (views_range_id) NOT NULL,
    likes_youtube_range bigint REFERENCES likes_range (likes_range_id) NOT NULL,
    comments_youtube_range bigint REFERENCES comments_range (comments_range_id) NOT NULL,

    -- Spotify metrics ranges
    danceability_range_id bigint REFERENCES danceability_range (danceability_range_id) ON DELETE CASCADE NOT NULL,
    energy_range_id bigint REFERENCES energy_range (energy_range_id) ON DELETE CASCADE NOT NULL,
    loudness_range_id bigint REFERENCES loudness_range (loudness_range_id) ON DELETE CASCADE NOT NULL,
    speechiness_range_id bigint REFERENCES speechiness_range (speechiness_range_id) ON DELETE CASCADE NOT NULL,
    acousticness_range_id bigint REFERENCES acousticness_range (acousticness_range_id) ON DELETE CASCADE NOT NULL,
    liveness_range_id bigint REFERENCES liveness_range (liveness_range_id) ON DELETE CASCADE NOT NULL,
    valence_range_id bigint REFERENCES valence_range (valence_range_id) ON DELETE CASCADE NOT NULL,
    tempo_range_id bigint REFERENCES tempo_range (tempo_range_id) ON DELETE CASCADE NOT NULL,

    -- Other data
    track TEXT CONSTRAINT text_constr CHECK ((char_length(track) >= 1) AND (char_length(track) < 255)) NOT NULL,
    streams_spotify bigint NOT NULL,
    views_youtube bigint NOT NULL,
    likes_youtube bigint NOT NULL,
    comments bigint NOT NULL,
    tempo float4 NOT NULL,
    duration_min int4 NOT NULL,
    most_playedon TEXT CONSTRAINT played_on_constr CHECK (most_playedon IN ('Youtube','Spotify')) NOT NULL,
    licensed BOOL NOT NULL,
    official_video BOOL NOT NULL,
    title_youtube TEXT CHECK (char_length(title_youtube) >= 1) NOT NULL

    -- Spotify metrics
    danceability float4 NOT NULL,
    energy float4 NOT NULL,
    loudness float4 NOT NULL,
    speechiness float4 NOT NULL,
    acousticness float4 NOT NULL,
    liveness float4 NOT NULL,
    valence float4 NOT NULL,
    tempo float4 NOT NULL,
    instrumentalness float4 NOT NULL
);

