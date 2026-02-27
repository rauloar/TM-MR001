BEGIN TRANSACTION;
CREATE TABLE IF NOT EXISTS "attendance_log" (
	"id"	INTEGER NOT NULL,
	"employee_id"	INTEGER,
	"raw_identifier"	VARCHAR(15),
	"date"	DATE,
	"time"	TIME,
	"mark_type"	INTEGER,
	"flags"	VARCHAR(7),
	"source_file"	VARCHAR,
	"created_at"	DATETIME,
	PRIMARY KEY("id"),
	UNIQUE("raw_identifier","date","time","mark_type"),
	FOREIGN KEY("employee_id") REFERENCES "users"("id")
);
CREATE TABLE IF NOT EXISTS "auth_user" (
	"id"	INTEGER NOT NULL,
	"username"	VARCHAR NOT NULL,
	"password_hash"	VARCHAR NOT NULL,
	"is_active"	BOOLEAN,
	"created_at"	DATETIME,
	PRIMARY KEY("id"),
	UNIQUE("username")
);
CREATE TABLE IF NOT EXISTS "users" (
	"id"	INTEGER NOT NULL,
	"identifier"	VARCHAR(15) NOT NULL,
	"first_name"	VARCHAR,
	"last_name"	VARCHAR,
	"is_active"	BOOLEAN,
	PRIMARY KEY("id"),
	UNIQUE("identifier")
);
COMMIT;
