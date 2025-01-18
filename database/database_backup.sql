PRAGMA foreign_keys=OFF;
BEGIN TRANSACTION;
CREATE TABLE AspectRatio (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    value INTEGER NOT NULL
);
CREATE TABLE PlyRating (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    value TEXT NOT NULL,
    is_custom INTEGER NOT NULL CHECK(is_custom IN (0, 1)),
    added_date DATE NOT NULL
);
CREATE TABLE SearchPage (
    width INTEGER,
    aspect_ratio INTEGER,
    inch INTEGER,
    FOREIGN KEY (width) REFERENCES Width(id),
    FOREIGN KEY (aspect_ratio) REFERENCES AspectRatio(id),
    FOREIGN KEY (inch) REFERENCES Inch(id)
);
CREATE TABLE EditPage (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    registration_date DATE NOT NULL,
    width INTEGER NOT NULL,
    aspect_ratio INTEGER NOT NULL,
    inch INTEGER NOT NULL,
    other_details TEXT,
    manufacturing_year INTEGER,
    manufacturer TEXT NOT NULL,
    tread_depth INTEGER,
    uneven_wear INTEGER,
    ply_rating INTEGER NOT NULL,
    price REAL NOT NULL,
    FOREIGN KEY (width) REFERENCES Width(id),
    FOREIGN KEY (aspect_ratio) REFERENCES AspectRatio(id),
    FOREIGN KEY (inch) REFERENCES Inch(id),
    FOREIGN KEY (manufacturer) REFERENCES Manufacturer(id),
    FOREIGN KEY (ply_rating) REFERENCES PlyRating(id)
);
CREATE TABLE HistoryPage (
    tire_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    action TEXT NOT NULL,
    edit_date DATE NOT NULL,
    details TEXT,
    FOREIGN KEY (tire_id) REFERENCES InputPage(id),
    FOREIGN KEY (user_id) REFERENCES User(id)
);
CREATE TABLE InstructionPage (
    dispatch_id INTEGER PRIMARY KEY AUTOINCREMENT,
    width INTEGER NOT NULL,
    aspect_ratio INTEGER NOT NULL,
    inch INTEGER NOT NULL,
    manufacturer TEXT NOT NULL,
    manufacturing_year INTEGER,
    tread_depth INTEGER,
    FOREIGN KEY (width) REFERENCES Width(id),
    FOREIGN KEY (aspect_ratio) REFERENCES AspectRatio(id),
    FOREIGN KEY (inch) REFERENCES Inch(id),
    FOREIGN KEY (manufacturer) REFERENCES Manufacturer(id)
);
CREATE TABLE DispatchHistory (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tire_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    dispatch_date DATE NOT NULL,
    dispatch_note TEXT,
    FOREIGN KEY (tire_id) REFERENCES InputPage(id),
    FOREIGN KEY (user_id) REFERENCES User(id)
);
CREATE TABLE AlertPage (
    width INTEGER,
    aspect_ratio INTEGER,
    inch INTEGER,
    inventory_count INTEGER NOT NULL,
    search_count INTEGER NOT NULL,
    FOREIGN KEY (width) REFERENCES Width(id),
    FOREIGN KEY (aspect_ratio) REFERENCES AspectRatio(id),
    FOREIGN KEY (inch) REFERENCES Inch(id)
);
CREATE TABLE DropdownHistory (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    entity_id INTEGER NOT NULL,
    entity_type TEXT NOT NULL,
    user_id INTEGER NOT NULL,
    change_date DATE NOT NULL,
    action TEXT NOT NULL,
    old_value TEXT,
    new_value TEXT,
    FOREIGN KEY (user_id) REFERENCES User(id)
);
CREATE TABLE DropdownManagement (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    entity_type TEXT NOT NULL,
    entity_value INTEGER NOT NULL,
    FOREIGN KEY (entity_value) REFERENCES Width(id) -- 適宜修正
);
CREATE TABLE width (
	id INTEGER NOT NULL, 
	value INTEGER NOT NULL, 
	PRIMARY KEY (id)
);
INSERT INTO width VALUES(1,135);
INSERT INTO width VALUES(2,145);
INSERT INTO width VALUES(3,155);
INSERT INTO width VALUES(4,165);
INSERT INTO width VALUES(5,175);
INSERT INTO width VALUES(6,185);
INSERT INTO width VALUES(7,195);
INSERT INTO width VALUES(8,205);
INSERT INTO width VALUES(9,215);
INSERT INTO width VALUES(10,225);
INSERT INTO width VALUES(11,235);
CREATE TABLE aspect_ratio (
	id INTEGER NOT NULL, 
	value INTEGER NOT NULL, 
	PRIMARY KEY (id)
);
INSERT INTO aspect_ratio VALUES(0,'');
INSERT INTO aspect_ratio VALUES(1,40);
INSERT INTO aspect_ratio VALUES(2,45);
INSERT INTO aspect_ratio VALUES(3,50);
INSERT INTO aspect_ratio VALUES(4,55);
INSERT INTO aspect_ratio VALUES(5,60);
INSERT INTO aspect_ratio VALUES(6,65);
INSERT INTO aspect_ratio VALUES(7,70);
INSERT INTO aspect_ratio VALUES(8,80);
CREATE TABLE inch (
	id INTEGER NOT NULL, 
	value INTEGER NOT NULL, 
	PRIMARY KEY (id)
);
INSERT INTO inch VALUES(1,10);
INSERT INTO inch VALUES(2,12);
INSERT INTO inch VALUES(3,13);
INSERT INTO inch VALUES(4,14);
INSERT INTO inch VALUES(5,15);
INSERT INTO inch VALUES(6,16);
INSERT INTO inch VALUES(8,18);
INSERT INTO inch VALUES(9,19);
INSERT INTO inch VALUES(10,20);
INSERT INTO inch VALUES(17,21);
CREATE TABLE manufacturer (
	id INTEGER NOT NULL, 
	name VARCHAR NOT NULL, 
	PRIMARY KEY (id)
);
INSERT INTO manufacturer VALUES(1,'ブリヂストン');
INSERT INTO manufacturer VALUES(2,'ダンロップ');
INSERT INTO manufacturer VALUES(3,'ヨコハマ');
INSERT INTO manufacturer VALUES(4,'トーヨータイヤ');
INSERT INTO manufacturer VALUES(5,'ニットータイヤ');
INSERT INTO manufacturer VALUES(6,'ミシュラン');
INSERT INTO manufacturer VALUES(7,'グッドイヤー');
INSERT INTO manufacturer VALUES(8,'ピレリ');
INSERT INTO manufacturer VALUES(9,'コンチネンタル');
INSERT INTO manufacturer VALUES(10,'ダンロップ');
CREATE TABLE ply_rating (
	id INTEGER NOT NULL, 
	value VARCHAR NOT NULL, 
	is_custom INTEGER NOT NULL, 
	added_date DATE NOT NULL, 
	PRIMARY KEY (id)
);
INSERT INTO ply_rating VALUES(1,'S',0,'2024-12-01');
INSERT INTO ply_rating VALUES(2,'v',0,'2024-12-01');
INSERT INTO ply_rating VALUES(3,'6P',0,'2024-12-01');
INSERT INTO ply_rating VALUES(4,'8P',0,'2024-12-01');
INSERT INTO ply_rating VALUES(5,'',0,'2024-12-01');
CREATE TABLE alert_page (
	id INTEGER NOT NULL, 
	width INTEGER, 
	aspect_ratio INTEGER, 
	inch INTEGER, 
	inventory_count INTEGER NOT NULL, 
	search_count INTEGER NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(width) REFERENCES width (id), 
	FOREIGN KEY(aspect_ratio) REFERENCES aspect_ratio (id), 
	FOREIGN KEY(inch) REFERENCES inch (id)
);
CREATE TABLE search_page (
	id INTEGER NOT NULL, 
	width INTEGER, 
	aspect_ratio INTEGER, 
	inch INTEGER, 
	inventory_count INTEGER NOT NULL, 
	search_count INTEGER NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(width) REFERENCES width (id), 
	FOREIGN KEY(aspect_ratio) REFERENCES aspect_ratio (id), 
	FOREIGN KEY(inch) REFERENCES inch (id)
);
CREATE TABLE history_page (
	id INTEGER NOT NULL, 
	tire_id INTEGER NOT NULL, 
	user_id INTEGER NOT NULL, 
	action VARCHAR NOT NULL, 
	edit_date DATE NOT NULL, 
	details VARCHAR, 
	PRIMARY KEY (id), 
	FOREIGN KEY(tire_id) REFERENCES input_page (id), 
	FOREIGN KEY(user_id) REFERENCES user (id)
);
CREATE TABLE dispatch_history (
	id INTEGER NOT NULL, 
	tire_id INTEGER NOT NULL, 
	user_id INTEGER NOT NULL, 
	dispatch_date DATE NOT NULL, 
	dispatch_note VARCHAR, 
	PRIMARY KEY (id), 
	FOREIGN KEY(tire_id) REFERENCES input_page (id), 
	FOREIGN KEY(user_id) REFERENCES user (id)
);
INSERT INTO dispatch_history VALUES(1,46,1,'2024-12-22','販売による出庫');
INSERT INTO dispatch_history VALUES(2,47,1,'2024-12-22','販売による出庫');
INSERT INTO dispatch_history VALUES(3,48,1,'2024-12-22','販売による出庫');
INSERT INTO dispatch_history VALUES(4,49,1,'2024-12-22','販売による出庫');
INSERT INTO dispatch_history VALUES(5,59,1,'2024-12-22','販売による出庫');
INSERT INTO dispatch_history VALUES(6,60,1,'2024-12-22','販売による出庫');
INSERT INTO dispatch_history VALUES(7,50,1,'2024-12-22','販売による出庫');
INSERT INTO dispatch_history VALUES(8,51,1,'2024-12-22','販売による出庫');
INSERT INTO dispatch_history VALUES(9,52,1,'2024-12-22','販売による出庫');
INSERT INTO dispatch_history VALUES(10,53,1,'2024-12-22','販売による出庫');
INSERT INTO dispatch_history VALUES(11,54,1,'2024-12-22','販売による出庫');
INSERT INTO dispatch_history VALUES(12,55,1,'2024-12-24','販売による出庫');
INSERT INTO dispatch_history VALUES(13,56,1,'2024-12-24','販売による出庫');
INSERT INTO dispatch_history VALUES(14,62,1,'2024-12-24','販売による出庫');
INSERT INTO dispatch_history VALUES(15,70,1,'2024-12-24','販売による出庫');
INSERT INTO dispatch_history VALUES(16,71,1,'2024-12-24','販売による出庫');
INSERT INTO dispatch_history VALUES(17,57,1,'2024-12-26','販売による出庫');
INSERT INTO dispatch_history VALUES(18,72,1,'2024-12-26','販売による出庫');
INSERT INTO dispatch_history VALUES(19,69,1,'2024-12-26','販売による出庫');
INSERT INTO dispatch_history VALUES(20,63,1,'2024-12-26','販売による出庫');
INSERT INTO dispatch_history VALUES(21,61,1,'2024-12-27','販売による出庫');
INSERT INTO dispatch_history VALUES(22,64,1,'2024-12-27','販売による出庫');
INSERT INTO dispatch_history VALUES(23,67,1,'2024-12-27','販売による出庫');
INSERT INTO dispatch_history VALUES(24,58,1,'2024-12-27','販売による出庫');
INSERT INTO dispatch_history VALUES(25,73,1,'2024-12-27','販売による出庫');
INSERT INTO dispatch_history VALUES(26,65,1,'2024-12-27','販売による出庫');
INSERT INTO dispatch_history VALUES(27,68,1,'2024-12-27','販売による出庫');
INSERT INTO dispatch_history VALUES(28,66,1,'2024-12-27','販売による出庫');
INSERT INTO dispatch_history VALUES(29,74,1,'2024-12-27','販売による出庫');
INSERT INTO dispatch_history VALUES(30,75,1,'2024-12-27','販売による出庫');
INSERT INTO dispatch_history VALUES(31,76,1,'2024-12-27','販売による出庫');
INSERT INTO dispatch_history VALUES(32,77,1,'2024-12-28',NULL);
INSERT INTO dispatch_history VALUES(33,78,1,'2024-12-28',NULL);
INSERT INTO dispatch_history VALUES(34,79,1,'2024-12-28',NULL);
INSERT INTO dispatch_history VALUES(35,80,1,'2024-12-28',NULL);
INSERT INTO dispatch_history VALUES(36,81,1,'2024-12-28',NULL);
INSERT INTO dispatch_history VALUES(37,82,1,'2024-12-28',NULL);
INSERT INTO dispatch_history VALUES(38,83,1,'2024-12-28',NULL);
INSERT INTO dispatch_history VALUES(39,84,1,'2024-12-28',NULL);
INSERT INTO dispatch_history VALUES(40,85,1,'2024-12-29',NULL);
INSERT INTO dispatch_history VALUES(41,86,1,'2024-12-29',NULL);
INSERT INTO dispatch_history VALUES(42,87,1,'2024-12-29',NULL);
INSERT INTO dispatch_history VALUES(43,88,1,'2024-12-29',NULL);
INSERT INTO dispatch_history VALUES(44,89,1,'2024-12-29',NULL);
INSERT INTO dispatch_history VALUES(45,90,1,'2024-12-29',NULL);
INSERT INTO dispatch_history VALUES(46,76,1,'2024-12-29',NULL);
INSERT INTO dispatch_history VALUES(47,80,1,'2024-12-29',NULL);
INSERT INTO dispatch_history VALUES(48,77,1,'2024-12-31',NULL);
INSERT INTO dispatch_history VALUES(49,78,1,'2025-01-01',NULL);
INSERT INTO dispatch_history VALUES(50,79,1,'2025-01-01',NULL);
INSERT INTO dispatch_history VALUES(51,81,1,'2025-01-01',NULL);
INSERT INTO dispatch_history VALUES(52,82,1,'2025-01-01',NULL);
INSERT INTO dispatch_history VALUES(53,83,1,'2025-01-01',NULL);
INSERT INTO dispatch_history VALUES(54,84,1,'2025-01-01',NULL);
INSERT INTO dispatch_history VALUES(55,91,1,'2025-01-01',NULL);
INSERT INTO dispatch_history VALUES(56,92,1,'2025-01-02',NULL);
INSERT INTO dispatch_history VALUES(57,93,1,'2025-01-03',NULL);
CREATE TABLE edit_page (
	id INTEGER NOT NULL, 
	tire_id INTEGER NOT NULL, 
	user_id INTEGER NOT NULL, 
	action VARCHAR NOT NULL, 
	edit_date DATE NOT NULL, 
	details VARCHAR, 
	PRIMARY KEY (id), 
	FOREIGN KEY(tire_id) REFERENCES input_page (id), 
	FOREIGN KEY(user_id) REFERENCES user (id)
);
CREATE TABLE alembic_version (
	version_num VARCHAR(32) NOT NULL, 
	CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num)
);
CREATE TABLE IF NOT EXISTS "input_page" (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    registration_date DATE NOT NULL,
    width INTEGER NOT NULL,
    aspect_ratio INTEGER NOT NULL,
    inch INTEGER NOT NULL,
    other_details TEXT,
    manufacturing_year INTEGER,
    manufacturer INTEGER NOT NULL,
    tread_depth INTEGER,
    uneven_wear INTEGER,
    ply_rating INTEGER NOT NULL,
    price FLOAT NULL,  -- ここを NULL許容 に変更
    is_dispatched BOOLEAN
);
INSERT INTO input_page VALUES(42,'2024-12-20',2,9,2,'',23,1,9,0,3,2000.0,0);
INSERT INTO input_page VALUES(43,'2024-12-21',6,6,5,'',22,4,9,0,5,NULL,0);
INSERT INTO input_page VALUES(44,'2024-12-21',6,6,5,'',23,3,9,0,5,NULL,0);
INSERT INTO input_page VALUES(45,'2024-12-21',6,6,5,'もうしんどい',23,3,9,0,5,NULL,0);
INSERT INTO input_page VALUES(46,'2024-12-21',1,1,1,'',22,6,9,0,1,NULL,1);
INSERT INTO input_page VALUES(47,'2024-12-21',1,1,1,'時間がかかる',22,6,9,0,1,3000.0,1);
INSERT INTO input_page VALUES(48,'2024-12-21',1,1,1,'',22,6,9,0,1,NULL,1);
INSERT INTO input_page VALUES(49,'2024-12-21',1,1,1,'',22,8,9,0,1,NULL,1);
INSERT INTO input_page VALUES(50,'2024-12-21',1,1,1,'',22,9,8,0,1,NULL,1);
INSERT INTO input_page VALUES(51,'2024-12-21',1,1,1,'',22,9,9,0,1,NULL,1);
INSERT INTO input_page VALUES(52,'2024-12-21',1,1,1,'',22,9,9,0,1,NULL,1);
INSERT INTO input_page VALUES(53,'2024-12-21',1,1,1,'',23,9,9,0,1,NULL,1);
INSERT INTO input_page VALUES(54,'2024-12-21',1,1,1,'',23,7,9,0,1,NULL,1);
INSERT INTO input_page VALUES(55,'2024-12-21',1,1,1,'',24,1,9,0,1,NULL,1);
INSERT INTO input_page VALUES(56,'2024-12-21',1,1,1,'',24,1,9,0,1,NULL,1);
INSERT INTO input_page VALUES(57,'2024-12-21',1,1,1,'',24,1,9,0,1,NULL,1);
INSERT INTO input_page VALUES(58,'2024-12-21',1,1,1,'',23,6,9,0,1,NULL,1);
INSERT INTO input_page VALUES(59,'2024-12-21',11,8,17,'注意！！',22,5,9,0,4,3000.0,1);
INSERT INTO input_page VALUES(60,'2024-12-21',11,8,17,'補修あり',22,5,9,0,4,3000.0,1);
INSERT INTO input_page VALUES(61,'2024-12-22',1,1,1,'',24,8,9,0,1,3000.0,1);
INSERT INTO input_page VALUES(62,'2024-12-22',1,1,1,'',24,8,9,1,1,3000.0,1);
INSERT INTO input_page VALUES(63,'2024-12-22',1,1,1,'',24,8,9,1,1,3000.0,1);
INSERT INTO input_page VALUES(64,'2024-12-22',1,1,1,'',24,8,7,2,1,3000.0,1);
INSERT INTO input_page VALUES(65,'2024-12-22',1,1,1,'テスト用',22,2,9,2,4,NULL,1);
INSERT INTO input_page VALUES(66,'2024-12-22',1,1,1,'プライ検索用',22,5,8,1,4,NULL,1);
INSERT INTO input_page VALUES(67,'2024-12-22',1,1,1,'プライ検索用',22,6,9,0,4,NULL,1);
INSERT INTO input_page VALUES(68,'2024-12-22',1,1,1,'プライ検索用',24,8,9,0,4,NULL,1);
INSERT INTO input_page VALUES(69,'2024-12-23',1,1,1,'',22,6,10,0,1,NULL,1);
INSERT INTO input_page VALUES(70,'2024-12-23',1,1,1,'',22,6,10,0,1,3000.0,1);
INSERT INTO input_page VALUES(71,'2024-12-23',1,1,1,'',22,6,10,0,1,3000.0,1);
INSERT INTO input_page VALUES(72,'2024-12-23',1,1,1,'',22,6,10,0,1,3000.0,1);
INSERT INTO input_page VALUES(73,'2024-12-23',1,1,1,'',22,6,10,0,1,3000.0,1);
INSERT INTO input_page VALUES(74,'2024-12-27',1,1,1,'',24,2,9,0,1,NULL,1);
INSERT INTO input_page VALUES(75,'2024-12-27',1,1,1,'',24,2,9,0,1,NULL,1);
INSERT INTO input_page VALUES(76,'2024-12-27',1,1,1,'',24,1,9,0,1,NULL,1);
INSERT INTO input_page VALUES(77,'2024-12-27',1,1,1,'',24,1,9,0,1,NULL,1);
INSERT INTO input_page VALUES(78,'2024-12-27',1,1,1,'',24,6,9,0,1,NULL,1);
INSERT INTO input_page VALUES(79,'2024-12-27',1,1,1,'',24,8,9,0,1,NULL,1);
INSERT INTO input_page VALUES(80,'2024-12-27',1,1,1,'',24,8,9,0,1,NULL,1);
INSERT INTO input_page VALUES(81,'2024-12-28',1,1,1,'',24,1,9,0,1,3000.0,1);
INSERT INTO input_page VALUES(82,'2024-12-28',1,1,1,'',24,1,9,0,1,3000.0,1);
INSERT INTO input_page VALUES(83,'2024-12-28',1,1,1,'',22,1,9,0,1,3000.0,1);
INSERT INTO input_page VALUES(84,'2024-12-28',1,1,1,'',24,7,9,0,1,3000.0,1);
INSERT INTO input_page VALUES(85,'2024-12-28',1,1,1,'',22,6,9,0,1,3000.0,1);
INSERT INTO input_page VALUES(86,'2024-12-28',1,1,1,'',24,6,9,0,1,3000.0,1);
INSERT INTO input_page VALUES(87,'2024-12-28',1,1,1,'',25,5,9,0,1,3000.0,1);
INSERT INTO input_page VALUES(88,'2024-12-28',1,1,1,'',24,6,9,0,1,3000.0,1);
INSERT INTO input_page VALUES(89,'2024-12-28',1,1,1,'',24,6,9,0,1,3000.0,1);
INSERT INTO input_page VALUES(90,'2024-12-28',1,1,1,'',24,9,9,0,1,3000.0,1);
INSERT INTO input_page VALUES(91,'2024-12-31',1,1,1,'',2023,4,10,0,0,NULL,1);
INSERT INTO input_page VALUES(92,'2024-12-31',1,1,1,'',2022,1,10,0,0,NULL,1);
INSERT INTO input_page VALUES(93,'2024-12-31',1,1,1,'',2022,2,10,0,0,NULL,1);
INSERT INTO input_page VALUES(94,'2025-01-02',1,1,1,'',2022,1,10,0,0,NULL,0);
INSERT INTO input_page VALUES(95,'2025-01-02',1,1,1,'',2022,1,10,0,0,NULL,0);
INSERT INTO input_page VALUES(96,'2025-01-02',1,1,1,'',2022,3,9,0,0,NULL,0);
INSERT INTO input_page VALUES(97,'2025-01-02',1,1,1,'',2023,4,9,0,0,NULL,0);
INSERT INTO input_page VALUES(98,'2025-01-02',1,1,1,'',2022,4,10,0,0,NULL,0);
INSERT INTO input_page VALUES(99,'2025-01-02',1,1,1,'',2023,4,8,0,0,NULL,0);
INSERT INTO input_page VALUES(100,'2025-01-02',1,1,1,'',2024,3,9,0,0,NULL,0);
INSERT INTO input_page VALUES(101,'2025-01-02',1,1,1,'',2023,2,8,1,0,NULL,0);
INSERT INTO input_page VALUES(102,'2025-01-02',1,1,1,'',2022,3,8,0,0,NULL,0);
INSERT INTO input_page VALUES(103,'2025-01-02',1,1,1,'',2024,2,9,0,0,NULL,0);
INSERT INTO input_page VALUES(104,'2025-01-02',1,1,1,'',2023,5,9,0,0,NULL,0);
INSERT INTO input_page VALUES(105,'2025-01-02',1,1,1,'',2023,6,10,0,0,NULL,0);
INSERT INTO input_page VALUES(106,'2025-01-02',1,1,1,'',2023,5,9,0,0,NULL,0);
INSERT INTO input_page VALUES(107,'2025-01-02',1,1,1,'',2022,1,10,0,0,NULL,0);
INSERT INTO input_page VALUES(108,'2025-01-03',1,1,1,'',0,1,10,0,0,NULL,0);
INSERT INTO input_page VALUES(109,'2025-01-03',1,1,1,'',NULL,2,10,0,0,NULL,0);
CREATE TABLE roles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(50) UNIQUE NOT NULL
);
CREATE TABLE IF NOT EXISTS "User" (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    role_id INTEGER,
    FOREIGN KEY(role_id) REFERENCES roles(id)
);
DELETE FROM sqlite_sequence;
INSERT INTO sqlite_sequence VALUES('input_page',109);
INSERT INTO sqlite_sequence VALUES('User',0);
COMMIT;
