from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, date

db = SQLAlchemy()

class Width(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    value = db.Column(db.Integer, nullable=False)

    # ✅ 登録日時を追加
    # ✅ 以下を追加
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    updated_at = db.Column(db.DateTime, nullable=True)
    updated_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)

class AspectRatio(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    value = db.Column(db.Integer, nullable=False)

    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    updated_at = db.Column(db.DateTime, nullable=True)
    updated_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    
class Inch(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    value = db.Column(db.Integer, nullable=False)

    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    updated_at = db.Column(db.DateTime, nullable=True)
    updated_by = db.Column(db.Integer, db.ForeignKey('users.id'))
class Manufacturer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)

    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    updated_at = db.Column(db.DateTime, nullable=True)
    updated_by = db.Column(db.Integer, db.ForeignKey('users.id'))
class PlyRating(db.Model):
    __tablename__ = 'ply_rating'
    id = db.Column(db.Integer, primary_key=True)
    value = db.Column(db.String, nullable=True)

    # 他と揃えて renamed
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)  # ←追加
    updated_at = db.Column(db.DateTime, nullable=True, onupdate=datetime.utcnow)

    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    updated_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)

    created_user = db.relationship('User', foreign_keys=[created_by], backref='created_ply_ratings')
    updated_user = db.relationship('User', foreign_keys=[updated_by], backref='updated_ply_ratings')

class InputPage(db.Model):
    __tablename__ = 'input_page'  # テーブル名を明示的に指定
    
    id = db.Column(db.Integer, primary_key=True)
    registration_date = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(JST).replace(microsecond=0))
    # ★ ここを追加
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    width = db.Column(db.Integer, db.ForeignKey('width.id'), nullable=True)
    aspect_ratio = db.Column(db.Integer, db.ForeignKey('aspect_ratio.id'), nullable=True)
    inch = db.Column(db.Integer, db.ForeignKey('inch.id'), nullable=True)
    other_details = db.Column(db.String)
    manufacturing_year = db.Column(db.Integer)
    manufacturer = db.Column(db.Integer, db.ForeignKey('manufacturer.id'), nullable=True)
    tread_depth = db.Column(db.Integer)
    uneven_wear = db.Column(db.Integer)
    ply_rating = db.Column(db.Integer, db.ForeignKey('ply_rating.id'), nullable=True)
    price = db.Column(db.Float, nullable=True)  # nullable=Trueに変更
    is_dispatched = db.Column(db.Boolean, default=False, nullable=False)
    last_edited_by = db.Column(db.Integer, nullable=True)
    last_edited_at = db.Column(db.DateTime, nullable=True)


    # リレーションを定義
    width_ref = db.relationship('Width', backref='input_pages', lazy=True)
    aspect_ratio_ref = db.relationship('AspectRatio', backref='input_pages', lazy=True)
    inch_ref = db.relationship('Inch', backref='input_pages', lazy=True)
    manufacturer_ref = db.relationship('Manufacturer', backref='input_pages', lazy=True)
    ply_rating_ref = db.relationship('PlyRating', backref='input_pages', lazy=True)  # 新たに追加

class HistoryPage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    tire_id = db.Column(db.Integer, db.ForeignKey('input_page.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    action = db.Column(db.String, nullable=False)
    edit_date = db.Column(db.DateTime, nullable=False)
    details = db.Column(db.String)

class DispatchHistory(db.Model):
    __tablename__ = "dispatch_history"  # 正しいテーブル名を指定
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)  # ✅ ここが重要
    tire_id = db.Column(db.Integer, db.ForeignKey('input_page.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    dispatch_date = db.Column(db.DateTime, nullable=False)
    dispatch_note = db.Column(db.String)

class AlertPage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    width = db.Column(db.Integer, db.ForeignKey('width.id'))
    aspect_ratio = db.Column(db.Integer, db.ForeignKey('aspect_ratio.id'))
    inch = db.Column(db.Integer, db.ForeignKey('inch.id'))
    inventory_count = db.Column(db.Integer, nullable=False)
    search_count = db.Column(db.Integer, nullable=False)

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
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    action = db.Column(db.String, nullable=False)
    edit_date = db.Column(db.DateTime, nullable=False)
    details = db.Column(db.String)

# Userモデルの定義
class User(UserMixin, db.Model):
    __tablename__ = 'users'  # ✅ 修正: 'user' → 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.Text, nullable=False)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
    
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)  # ✅ 追加！
    
    role = db.relationship('Role', backref=db.backref('users', lazy=True))

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def has_role(self, role_name):
        return self.role and self.role.name == role_name
    
class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    description = db.Column(db.String(255))

class EditHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    tire_id = db.Column(db.Integer, db.ForeignKey('input_page.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    edit_date = db.Column(db.DateTime, default=datetime.utcnow)
    edit_details = db.Column(db.Text)

    def __repr__(self):
        return f"<EditHistory tire_id={self.tire_id} user_id={self.user_id} edit_date={self.edit_date}>"
