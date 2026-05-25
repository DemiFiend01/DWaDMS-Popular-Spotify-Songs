DROP INDEX IF EXISTS idx_streams_spotify;
DROP INDEX IF EXISTS idx_views_youtube;
DROP INDEX IF EXISTS idx_likes_youtube;
DROP INDEX IF EXISTS idx_comments;
DROP INDEX IF EXISTS idx_duration_min;
DROP INDEX IF EXISTS idx_most_playedon;
DROP INDEX IF EXISTS idx_duration_min;
DROP INDEX IF EXISTS idx_most_playedon;
DROP INDEX IF EXISTS idx_licensed;
DROP INDEX IF EXISTS idx_official_video;
DROP INDEX IF EXISTS idx_title_youtube;

DROP INDEX IF EXISTS idx_danceability;
DROP INDEX IF EXISTS idx_energy;
DROP INDEX IF EXISTS idx_loudness;
DROP INDEX IF EXISTS idx_speechiness;
DROP INDEX IF EXISTS idx_acousticness;
DROP INDEX IF EXISTS idx_liveness;
DROP INDEX IF EXISTS idx_valence;
DROP INDEX IF EXISTS idx_tempo;
DROP INDEX IF EXISTS idx_instrumentalness;

DROP TABLE IF EXISTS facts_streams_1B_10B;
DROP TABLE IF EXISTS facts_streams_500M_1B;
DROP TABLE IF EXISTS facts_streams_100_500M;
DROP TABLE IF EXISTS facts_streams_1M_100M;
DROP TABLE IF EXISTS facts_streams_0_1M;

DROP TABLE IF EXISTS facts;
DROP TABLE IF EXISTS youtube_channel;
DROP TABLE IF EXISTS album;
DROP TABLE IF EXISTS artist;
