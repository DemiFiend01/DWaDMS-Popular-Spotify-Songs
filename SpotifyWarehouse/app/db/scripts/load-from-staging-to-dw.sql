-- Load artists

INSERT INTO artist (artist) 
SELECT DISTINCT artist FROM full_dataset;

-- Load youtube_channels

INSERT INTO youtube_channel (channel)
SELECT DISTINCT channel FROM full_dataset;

-- load albums

INSERT INTO album (artist_id, album, album_type)
SELECT DISTINCT a.artist_id, f.album, f.album_type 
FROM full_dataset AS f JOIN artist AS a 
ON f.artist = a.artist;

-- load tracks

INSERT INTO track (
    artist_id,
    youtube_channel_id,

    -- Other data
    track,
    streams_spotify,
    views_youtube,
    likes_youtube,
    comments,
    duration_min,
    most_playedon,
    licensed,
    official_video,
    title_youtube,

    -- Spotify metrics
    danceability,
    energy,
    loudness,
    speechiness,
    acousticness,
    liveness,
    valence,
    tempo,
    instrumentalness
)
SELECT 
    a.artist_id,
    y.youtube_id,

    -- Other data
    f.track,
    f.streams_spotify,
    f.views_youtube,
    f.likes_youtube,
    f.comments_youtube,
    f.duration_min,
    f.most_playedon,
    f.licensed,
    f.official_video,
    f.title_youtube,

    -- Spotify metrics
    f.danceability,
    f.energy,
    f.loudness,
    f.speechiness,
    f.acousticness,
    f.liveness,
    f.valence,
    f.tempo,
    f.instrumentalness
FROM 
    full_dataset AS f JOIN artist as a
    ON f.artist = a.artist
    JOIN youtube_channel AS y
    ON f.channel = y.channel;