/* 
 * Click nbfs://nbhost/SystemFileSystem/Templates/Licenses/license-default.txt to change this license
 * Click nbfs://nbhost/SystemFileSystem/Templates/Other/SQLTemplate.sql to edit this template
 */
/**
 * Author:  Student
 * Created: 11 maj 2026
 */

-- 1
CREATE TABLE IF NOT EXISTS artist (
    artist_id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    artist TEXT CONSTRAINT art_constr CHECK ((char_length(artist) >=1) AND (char_length(artist) < 255)) NOT NULL
);

-- 3
CREATE TABLE IF NOT EXISTS album (
    album_id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    album TEXT CONSTRAINT album_constr CHECK ((char_length(album) >=1) AND (char_length(album) < 255)) NOT NULL,
    album_type TEXT CONSTRAINT al_type_constr CHECK (album_type IN ('single', 'compilation', 'album')) NOT NULL
);

-- 2
CREATE TABLE IF NOT EXISTS youtube_channel (
    youtube_id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    channel TEXT CONSTRAINT ch_constr CHECK ((char_length(channel) >=1) AND (char_length(channel) < 255)) NOT NULL
);

-- 4
-- GOD OBJECT
CREATE TABLE IF NOT EXISTS facts (
    -- 
    track_id bigint GENERATED ALWAYS AS IDENTITY,

    -- Foreign keys
    artist_id bigint REFERENCES artist (artist_id) ON DELETE CASCADE NOT NULL,
    youtube_channel_id bigint REFERENCES youtube_channel (youtube_id) ON DELETE CASCADE NOT NULL,
    album_id bigint REFERENCES album (album_id) ON DELETE CASCADE NOT NULL,

    -- Other data
    track TEXT CONSTRAINT text_constr CHECK ((char_length(track) >= 1) AND (char_length(track) < 255)) NOT NULL,
    streams_spotify bigint NOT NULL,
    views_youtube bigint NOT NULL,
    likes_youtube bigint NOT NULL,
    comments bigint NOT NULL,
    duration_min int4 NOT NULL,
    most_playedon TEXT CONSTRAINT played_on_constr CHECK (most_playedon IN ('Youtube','Spotify')) NOT NULL,
    licensed BOOL NOT NULL,
    official_video BOOL NOT NULL,
    title_youtube TEXT CHECK (char_length(title_youtube) >= 1) NOT NULL,

    -- Spotify metrics
    danceability float4 NOT NULL,
    energy float4 NOT NULL,
    loudness float4 NOT NULL,
    speechiness float4 NOT NULL,
    acousticness float4 NOT NULL,
    liveness float4 NOT NULL,
    valence float4 NOT NULL,
    tempo float4 NOT NULL,
    instrumentalness float4 NOT NULL,

    PRIMARY KEY (track_id, streams_spotify)
) PARTITION BY RANGE (streams_spotify);

CREATE TABLE facts_streams_0_1M PARTITION OF facts
FOR VALUES FROM (0) TO (1000000);

CREATE TABLE facts_streams_1M_100M PARTITION OF facts
FOR VALUES FROM (1000000) TO (100000000);

CREATE TABLE facts_streams_100_500M PARTITION OF facts
FOR VALUES FROM (100000000) TO (500000000);

CREATE TABLE facts_streams_500M_1B PARTITION OF facts
FOR VALUES FROM (500000000) TO (1000000000);

CREATE TABLE facts_streams_1B_10B PARTITION OF facts
FOR VALUES FROM (1000000000) TO (10000000000);

CREATE INDEX idx_streams_spotify ON facts (streams_spotify);
CREATE INDEX idx_views_youtube ON facts   (views_youtube);
CREATE INDEX idx_likes_youtube ON facts   (likes_youtube);
CREATE INDEX idx_comments ON facts        (comments);
CREATE INDEX idx_duration_min ON facts    (duration_min);
CREATE INDEX idx_most_playedon ON facts   (most_playedon);
CREATE INDEX idx_licensed ON facts        (licensed);
CREATE INDEX idx_official_video ON facts  (official_video);
CREATE INDEX idx_title_youtube ON facts   (title_youtube);

CREATE INDEX idx_danceability ON facts     (danceability);
CREATE INDEX idx_energy ON facts           (energy);
CREATE INDEX idx_loudness ON facts         (loudness);
CREATE INDEX idx_speechiness ON facts      (speechiness);
CREATE INDEX idx_acousticness ON facts     (acousticness);
CREATE INDEX idx_liveness ON facts         (liveness);
CREATE INDEX idx_valence ON facts          (valence);
CREATE INDEX idx_tempo ON facts            (tempo);
CREATE INDEX idx_instrumentalness ON facts (instrumentalness);