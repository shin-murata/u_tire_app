
BEGIN TRANSACTION;

-- `dispatch_history` の `dispatch_date` を `DATETIME` に変更
ALTER TABLE dispatch_history RENAME TO dispatch_history_old;

CREATE TABLE dispatch_history (
    id INTEGER PRIMARY KEY,
    tire_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    dispatch_date DATETIME NOT NULL,  -- `DATETIME` に変更
    dispatch_note VARCHAR,
    FOREIGN KEY (tire_id) REFERENCES input_page(id),
    FOREIGN KEY (user_id) REFERENCES user(id)
);

INSERT INTO dispatch_history (id, tire_id, user_id, dispatch_date, dispatch_note)
SELECT id, tire_id, user_id, dispatch_date || ' 00:00:00', dispatch_note FROM dispatch_history_old;

DROP TABLE dispatch_history_old;

-- `history_page` の `edit_date` を `DATETIME` に変更
ALTER TABLE history_page RENAME TO history_page_old;

CREATE TABLE history_page (
    id INTEGER PRIMARY KEY,
    tire_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    action VARCHAR NOT NULL,
    edit_date DATETIME NOT NULL,  -- `DATETIME` に変更
    details VARCHAR,
    FOREIGN KEY (tire_id) REFERENCES input_page(id),
    FOREIGN KEY (user_id) REFERENCES user(id)
);

INSERT INTO history_page (id, tire_id, user_id, action, edit_date, details)
SELECT id, tire_id, user_id, action, edit_date || ' 00:00:00', details FROM history_page_old;

DROP TABLE history_page_old;

COMMIT;
