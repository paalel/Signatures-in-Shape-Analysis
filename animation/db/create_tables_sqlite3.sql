CREATE TABLE IF NOT EXISTS subject 
(
 subject_id INTEGER PRIMARY KEY AUTOINCREMENT,
 file_name VARCHAR (50) NOT NULL,
 file_path VARCHAR (355) UNIQUE NOT NULL,
 file_type VARCHAR (50) NOT NULL,
 description TEXT
);

CREATE TABLE IF NOT EXISTS animation
(
 animation_id INTEGER PRIMARY KEY AUTOINCREMENT,
 subject_id INTEGER,
 file_name VARCHAR (50) NOT NULL,
 file_path VARCHAR (355) UNIQUE NOT NULL,
 file_type VARCHAR (50) NOT NULL,
 description TEXT,
 FOREIGN KEY (subject_id) REFERENCES subject (subject_id)
);

CREATE TABLE IF NOT EXISTS similarity 
(
 distance REAL NOT NULL,
 dp_distance REAL NOT NULL,
 signature_distance REAL NOT NULL,
 size1 INTEGER,
 size2 INTEGER,
 animation_id1 INTEGER,
 animation_id2 INTEGER,
 FOREIGN KEY (animation_id1) REFERENCES animation (animation_id),
 FOREIGN KEY (animation_id2) REFERENCES animation (animation_id),
 PRIMARY KEY(animation_id1, animation_id2)
);

