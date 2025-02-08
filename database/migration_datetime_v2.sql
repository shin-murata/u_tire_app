
BEGIN TRANSACTION;

-- `DispatchHistory` の `dispatch_date` を `DATETIME` に変更
ALTER TABLE DispatchHistory RENAME TO DispatchHistory_old;

CREATE TABLE DispatchHistory (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tire_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    dispatch_date DATETIME NOT NULL,
    dispatch_note TEXT,
    FOREIGN KEY (tire_id) REFERENCES InputPage(id),
    FOREIGN KEY (user_id) REFERENCES User(id)
);

INSERT INTO DispatchHistory (id, tire_id, user_id, dispatch_date, dispatch_note)
SELECT id, tire_id, user_id, dispatch_date || ' 00:00:00', dispatch_note FROM DispatchHistory_old;

DROP TABLE DispatchHistory_old;

-- `DropdownHistory` の `change_date` を `DATETIME` に変更
ALTER TABLE DropdownHistory RENAME TO DropdownHistory_old;

CREATE TABLE DropdownHistory (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    entity_id INTEGER NOT NULL,
    entity_type TEXT NOT NULL,
    user_id INTEGER NOT NULL,
    change_date DATETIME NOT NULL,
    action TEXT NOT NULL,
    old_value TEXT,
    new_value TEXT,
    FOREIGN KEY (user_id) REFERENCES User(id)
);

INSERT INTO DropdownHistory (id, entity_id, entity_type, user_id, change_date, action, old_value, new_value)
SELECT id, entity_id, entity_type, user_id, change_date || ' 00:00:00', action, old_value, new_value FROM DropdownHistory_old;

DROP TABLE DropdownHistory_old;

-- `EditPage` の `registration_date` を `DATETIME` に変更
ALTER TABLE EditPage RENAME TO EditPage_old;

CREATE TABLE EditPage (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    registration_date DATETIME NOT NULL,
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
    FOREIGN KEY (aspect_ratio) REFERENCES AspectRatio(id),
    FOREIGN KEY (inch) REFERENCES Inch(id),
    FOREIGN KEY (manufacturer) REFERENCES Manufacturer(id),
    FOREIGN KEY (ply_rating) REFERENCES PlyRating(id),
    FOREIGN KEY (width) REFERENCES Width(id)
);

INSERT INTO EditPage (id, registration_date, width, aspect_ratio, inch, other_details, manufacturing_year, manufacturer, tread_depth, uneven_wear, ply_rating, price)
SELECT id, registration_date || ' 00:00:00', width, aspect_ratio, inch, other_details, manufacturing_year, manufacturer, tread_depth, uneven_wear, ply_rating, price FROM EditPage_old;

DROP TABLE EditPage_old;

COMMIT;
