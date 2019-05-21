CREATE EXTENSION IF NOT EXISTS pgcrypto;

DROP TABLE IF EXISTS photo_thumbnails;
DROP TABLE IF EXISTS photos;
DROP TYPE IF EXISTS photo_status;

CREATE TYPE photo_status as enum('pending', 'completed', 'processing', 'failed');
CREATE TABLE photos (
    uuid uuid DEFAULT gen_random_uuid() PRIMARY KEY,
    url text NOT NULL,
    status photo_status DEFAULT 'pending' NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);

CREATE TABLE photo_thumbnails (
    uuid uuid DEFAULT gen_random_uuid() PRIMARY KEY,
    photo_uuid uuid REFERENCES photos(uuid) NOT NULL,
    width smallint NOT NULL,
    height smallint NOT NULL,
    url text NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);
