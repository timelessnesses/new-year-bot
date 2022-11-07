CREATE TABLE IF NOT EXISTS config(
    guild_id BIGINT NOT NULL PRIMARY KEY,
    annouce_channel_id BIGINT NOT NULL,
    timezone VARCHAR(255) NOT NULL
);
-- lol