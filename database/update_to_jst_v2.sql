BEGIN TRANSACTION;

-- `dispatch_history` の `dispatch_date` を JST に変換
UPDATE dispatch_history
SET dispatch_date = datetime(dispatch_date, '+9 hours');

-- `history_page` の `edit_date` を JST に変換
UPDATE history_page
SET edit_date = datetime(edit_date, '+9 hours');

-- `DispatchHistory` の `dispatch_date` を JST に変換
UPDATE DispatchHistory
SET dispatch_date = datetime(dispatch_date, '+9 hours');

-- `DropdownHistory` の `change_date` を JST に変換
UPDATE DropdownHistory
SET change_date = datetime(change_date, '+9 hours');

-- `EditPage` の `registration_date` を JST に変換
UPDATE EditPage
SET registration_date = datetime(registration_date, '+9 hours');

COMMIT;

