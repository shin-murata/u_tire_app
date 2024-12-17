from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Width(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    value = db.Column(db.Integer, nullable=False)

class AspectRatio(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    value = db.Column(db.Integer, nullable=False)

class Inch(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    value = db.Column(db.Integer, nullable=False)

class Manufacturer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)

class PlyRating(db.Model):
    __tablename__ = 'ply_rating'  # テーブル名を明示的に指定
    id = db.Column(db.Integer, primary_key=True)
    value = db.Column(db.String, nullable=False)
    is_custom = db.Column(db.Integer, nullable=False)
    added_date = db.Column(db.Date, nullable=False)

class InputPage(db.Model):
    __tablename__ = 'input_page'  # テーブル名を明示的に指定
    
    id = db.Column(db.Integer, primary_key=True)
    registration_date = db.Column(db.Date, nullable=False)
    width = db.Column(db.Integer, db.ForeignKey('width.id'), nullable=False)
    aspect_ratio = db.Column(db.Integer, db.ForeignKey('aspect_ratio.id'), nullable=False)
    inch = db.Column(db.Integer, db.ForeignKey('inch.id'), nullable=False)
    other_details = db.Column(db.String)
    manufacturing_year = db.Column(db.Integer)
    manufacturer = db.Column(db.Integer, db.ForeignKey('manufacturer.id'), nullable=False)
    tread_depth = db.Column(db.Integer)
    uneven_wear = db.Column(db.Integer)
    ply_rating = db.Column(db.Integer, db.ForeignKey('ply_rating.id'), nullable=False)
    price = db.Column(db.Float, nullable=True)  # nullable=Trueに変更
    is_dispatched = db.Column(db.Boolean, default=False, nullable=False)

    # リレーションを定義
    width_ref = db.relationship('Width', backref='input_pages', lazy=True)
    aspect_ratio_ref = db.relationship('AspectRatio', backref='input_pages', lazy=True)
    inch_ref = db.relationship('Inch', backref='input_pages', lazy=True)
    manufacturer_ref = db.relationship('Manufacturer', backref='input_pages', lazy=True)

class HistoryPage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    tire_id = db.Column(db.Integer, db.ForeignKey('input_page.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    action = db.Column(db.String, nullable=False)
    edit_date = db.Column(db.Date, nullable=False)
    details = db.Column(db.String)

class DispatchHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    tire_id = db.Column(db.Integer, db.ForeignKey('input_page.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    dispatch_date = db.Column(db.Date, nullable=False)
    dispatch_note = db.Column(db.String)

class AlertPage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    width = db.Column(db.Integer, db.ForeignKey('width.id'))
    aspect_ratio = db.Column(db.Integer, db.ForeignKey('aspect_ratio.id'))
    inch = db.Column(db.Integer, db.ForeignKey('inch.id'))
    inventory_count = db.Column(db.Integer, nullable=False)
    search_count = db.Column(db.Integer, nullable=False)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    email = db.Column(db.String, nullable=False)
    role = db.Column(db.String, nullable=False)

class SearchPage(db.Model):
    __tablename__ = 'search_page'
    id = db.Column(db.Integer, primary_key=True)
    width = db.Column(db.Integer, db.ForeignKey('width.id'))
    aspect_ratio = db.Column(db.Integer, db.ForeignKey('aspect_ratio.id'))
    inch = db.Column(db.Integer, db.ForeignKey('inch.id'))
    inventory_count = db.Column(db.Integer, nullable=False)
    search_count = db.Column(db.Integer, nullable=False)

class EditPage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    tire_id = db.Column(db.Integer, db.ForeignKey('input_page.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    action = db.Column(db.String, nullable=False)
    edit_date = db.Column(db.Date, nullable=False)
    details = db.Column(db.String)
