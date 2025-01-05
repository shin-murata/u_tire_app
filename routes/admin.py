from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required
from utils import role_required  # utils.pyからrole_requiredをインポート
from models import User, Role, Width, AspectRatio, Inch, Manufacturer, PlyRating, db, InputPage  # InputPage モデルが定義されている場所からインポート

# Blueprintの定義
admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

# モデルマッピング
MODEL_MAP = {
    'width': {'model': Width, 'field': 'value'},
    'aspect_ratio': {'model': AspectRatio, 'field': 'value'},
    'inch': {'model': Inch, 'field': 'value'},
    'manufacturer': {'model': Manufacturer, 'field': 'name'},
    'ply_rating': {'model': PlyRating, 'field': 'value'}
}

# 管理画面
@admin_bp.route('/manage', methods=['GET', 'POST'])
@role_required('admin')  # 管理者権限を要求
def manage():
    manufacturers = Manufacturer.query.all()
    print("Manufacturers:", [m.name for m in manufacturers])  # デバッグ: 各メーカーの名前を表示

    # 管理画面のデータを取得
    data = {
        key: {'entries': config['model'].query.all(), 'field': config['field']}
        for key, config in MODEL_MAP.items()
    }
    print("Data passed to template:", data)  # デバッグ: データ構造を出力
    return render_template(
        'admin/manage.html', 
        data=data, 
        roles=Role.query.all(), 
        users=User.query.all(), 
        getattr=getattr
    )
    
# その他の汎用ルート（例: 追加、更新、削除）
@admin_bp.route('/add/<string:model_name>', methods=['POST'])
def add_data(model_name):
    config = MODEL_MAP.get(model_name)
    if not config:
        flash(f"Invalid model name: {model_name}", "danger")
        return redirect(url_for('admin.manage'))

    model = config['model']
    field_name = config['field']

    # 新しいエントリを追加
    try:
        new_entry = model(**{field_name: request.form['value']})
        db.session.add(new_entry)
        db.session.commit()
        flash(f"{model_name.capitalize()} added successfully!", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"Error adding {model_name}: {e}", "danger")
    return redirect(url_for('admin.manage'))

@admin_bp.route('/update/<string:model_name>/<int:id>', methods=['POST'])
def update_data(model_name, id):
    config = MODEL_MAP.get(model_name)
    if not config:
        flash(f"Invalid model name: {model_name}", "danger")
        return redirect(url_for('admin.manage'))

    model = config['model']
    field_name = config['field']

    # データの更新
    try:
        entry = model.query.get_or_404(id)
        if model_name == 'manufacturers':
            entry.name = request.form['value']  # Manufacturer の場合は name フィールドを更新
        else:
            entry.value = request.form['value']  # その他のモデルは value フィールドを更新
        db.session.commit()
        flash(f"{model_name.capitalize()} updated successfully!", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"Error updating {model_name}: {e}", "danger")
    return redirect(url_for('admin.manage'))

@admin_bp.route('/delete/<string:model_name>/<int:id>', methods=['POST'])
def delete_data(model_name, id):
    # デバッグログ
    print(f"Attempting to delete model: {model_name}, id: {id}")
    # MODEL_MAPで対応するモデルを取得
    config = MODEL_MAP.get(model_name)
    if not config:  # MODEL_MAPにキーがない場合の処理
        flash(f"Invalid model name: {model_name}", "danger")
        return redirect(url_for('admin.manage'))
    
    model = config.get('model')  # モデルを取得
    if not model:  # モデルが見つからない場合の処理
        flash(f"Model not found for: {model_name}", "danger")
        return redirect(url_for('admin.manage'))
    
    # データの削除
    try:
        # デバッグ: 削除対象のデータを確認
        print(f"Attempting to delete model: {model_name}, id: {id}")
        entry = model.query.get_or_404(id)
        print(f"Attempting to delete: {entry}")

        # 関連データのチェック
        related_records = []  # ここに関連するテーブルをチェックして結果を格納
        if model_name == 'width':
            related_records = db.session.query(InputPage).filter_by(width=id).all()
        elif model_name == 'aspect_ratio':
            related_records = db.session.query(InputPage).filter_by(aspect_ratio=id).all()
        elif model_name == 'inch':
            related_records = db.session.query(InputPage).filter_by(inch=id).all()
        elif model_name == 'manufacturer':
            related_records = db.session.query(InputPage).filter_by(manufacturer=id).all()
        elif model_name == 'ply_rating':  # 追加
            related_records = db.session.query(InputPage).filter_by(ply_rating=id).all()


        # 関連データが存在する場合、削除を許可しない
        if related_records:
            flash(f"Cannot delete {model_name} with ID {id} because it is referenced in other records.", "danger")
            print(f"Related records found: {related_records}")
            return redirect(url_for('admin.manage'))

        # レコードの削除
        db.session.delete(entry)
        db.session.commit()
        flash(f"{model_name.capitalize()} deleted successfully!", "success")
    except Exception as e:
        db.session.rollback()
        print(f"Error deleting {model_name}: {e}")
        flash(f"Error deleting {model_name}: {e}", "danger")
    return redirect(url_for('admin.manage'))

@admin_bp.route('/add_user', methods=['POST'])
def add_user():
    username = request.form['username']
    password = request.form['password']
    role_id = request.form['role_id']
    new_user = User(username=username, role_id=role_id)
    new_user.set_password(password)
    db.session.add(new_user)
    db.session.commit()
    flash('User added successfully!')
    return redirect(url_for('admin.manage'))

@admin_bp.route('/delete_user/<int:id>', methods=['POST'])
def delete_user(id):
    user = User.query.get_or_404(id)
    db.session.delete(user)
    db.session.commit()
    flash('User deleted successfully!')
    return redirect(url_for('admin.manage'))

