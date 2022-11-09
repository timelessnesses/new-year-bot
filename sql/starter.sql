CREATE TABLE IF NOT EXISTS config(
    guild_id BIGINT NOT NULL PRIMARY KEY,
    annouce_channel_id BIGINT DEFAULT NULL,
    timezone VARCHAR(255) NOT NULL DEFAULT "UTC"
);

CREATE TABLE IF NOT EXISTS reminder_message(
    id BIGINT NOT NULL PRIMARY KEY,
    guild_id BIGINT NOT NULL,
    channel_id BIGINT DEFAULT 0
);

CREATE TABLE IF NOT EXISTS new_year_message(
    id BIGINT, -- this is optional cus of uhhh we also store how message format is and stuff and yeah plus this is just for deleting purposes
    guild_id BIGINT NOT NULL PRIMARY KEY,
    channel_id BIGINT NOT NULL,
    message_format TEXT,
    ping_role_id BIGINT,
    body_message_format TEXT
);

-- lol