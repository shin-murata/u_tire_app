BEGIN TRANSACTION;
CREATE TABLE IF NOT EXISTS "roles" (
	id SERIAL PRIMARY KEY,
	"name"	VARCHAR(50) NOT NULL,
	"description"	VARCHAR(255),
	UNIQUE("name")
);
CREATE TABLE IF NOT EXISTS "users" (
	id SERIAL PRIMARY KEY,
	"username"	VARCHAR(150) NOT NULL,
	"password_hash"	VARCHAR(150) NOT NULL,
	"role_id"	INTEGER,
	UNIQUE("username"),
	FOREIGN KEY("role_id") REFERENCES "roles"("id")
);
CREATE TABLE IF NOT EXISTS "width" (
	id SERIAL PRIMARY KEY,
	"value"	INTEGER NOT NULL
);
CREATE TABLE IF NOT EXISTS "aspect_ratio" (
	id SERIAL PRIMARY KEY,
	"value"	INTEGER NOT NULL
);
CREATE TABLE IF NOT EXISTS "inch" (
	id SERIAL PRIMARY KEY,
	"value"	INTEGER NOT NULL
);
CREATE TABLE IF NOT EXISTS "manufacturer" (
	id SERIAL PRIMARY KEY,
	"name"	VARCHAR NOT NULL
);
CREATE TABLE IF NOT EXISTS "ply_rating" (
	id SERIAL PRIMARY KEY,
	"value"	VARCHAR NOT NULL,
	"is_custom"	INTEGER NOT NULL,
	"added_date"	DATE NOT NULL
);
CREATE TABLE IF NOT EXISTS "alembic_version" (
	"version_num"	VARCHAR(32) NOT NULL,
	CONSTRAINT "alembic_version_pkc" PRIMARY KEY("version_num")
);
CREATE TABLE IF NOT EXISTS "input_page" (
	id SERIAL PRIMARY KEY,
	"width"	INTEGER NOT NULL,
	"aspect_ratio"	INTEGER NOT NULL,
	"inch"	INTEGER NOT NULL,
	"other_details"	TEXT,
	"manufacturing_year"	INTEGER,
	"manufacturer"	INTEGER NOT NULL,
	"tread_depth"	INTEGER,
	"uneven_wear"	INTEGER,
	"ply_rating"	INTEGER NOT NULL,
	"price"	FLOAT,
	"is_dispatched"	BOOLEAN,
	"registration_date"	TIMESTAMP
);
CREATE TABLE IF NOT EXISTS "search_page" (
	id SERIAL PRIMARY KEY,
	"width"	INTEGER,
	"aspect_ratio"	INTEGER,
	"inch"	INTEGER,
	"inventory_count"	INTEGER NOT NULL,
	"search_count"	INTEGER NOT NULL,
	FOREIGN KEY("aspect_ratio") REFERENCES "aspect_ratio"("id"),
	FOREIGN KEY("inch") REFERENCES "inch"("id"),
	FOREIGN KEY("width") REFERENCES "width"("id")
);
CREATE TABLE IF NOT EXISTS "dispatch_history" (
	id SERIAL PRIMARY KEY,
	"tire_id"	INTEGER NOT NULL,
	"user_id"	INTEGER NOT NULL,
	"dispatch_date"	TIMESTAMP NOT NULL,
	"dispatch_note"	VARCHAR,
	FOREIGN KEY("tire_id") REFERENCES "input_page"("id"),
	FOREIGN KEY("user_id") REFERENCES "users"("id")
);
CREATE TABLE IF NOT EXISTS "edit_page" (
	id SERIAL PRIMARY KEY,
	"tire_id"	INTEGER NOT NULL,
	"user_id"	INTEGER NOT NULL,
	"action"	VARCHAR NOT NULL,
	"edit_date"	DATE NOT NULL,
	"details"	VARCHAR,
	FOREIGN KEY("tire_id") REFERENCES "input_page"("id"),
	FOREIGN KEY("user_id") REFERENCES "users"("id")
);
CREATE TABLE IF NOT EXISTS "history_page" (
	id SERIAL PRIMARY KEY,
	"tire_id"	INTEGER NOT NULL,
	"user_id"	INTEGER NOT NULL,
	"action"	VARCHAR NOT NULL,
	"edit_date"	TIMESTAMP NOT NULL,
	"details"	VARCHAR,
	FOREIGN KEY("tire_id") REFERENCES "input_page"("id"),
	FOREIGN KEY("user_id") REFERENCES "users"("id")
);
CREATE TABLE IF NOT EXISTS "alert_page" (
	id SERIAL PRIMARY KEY,
	"width"	INTEGER,
	"aspect_ratio"	INTEGER,
	"inch"	INTEGER,
	"inventory_count"	INTEGER NOT NULL,
	"search_count"	INTEGER NOT NULL,
	FOREIGN KEY("aspect_ratio") REFERENCES "aspect_ratio"("id"),
	FOREIGN KEY("inch") REFERENCES "inch"("id"),
	FOREIGN KEY("width") REFERENCES "width"("id")
);
COMMIT;
