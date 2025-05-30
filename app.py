from flask import Blueprint, Flask, render_template, request, redirect, url_for,  jsonify, flash, session, Response, g
from flask_migrate import Migrate  # Flask-Migrate をインポート
from models import db, Width, AspectRatio, Inch, Manufacturer, PlyRating, InputPage, SearchPage, EditPage, HistoryPage, DispatchHistory, AlertPage, User, Role, EditHistory
from forms import SearchForm, EditForm, CombinedForm
from flask_login import LoginManager, UserMixin, login_user, logout_user, current_user, login_required, AnonymousUserMixin
from utils import role_required # role_requiredをインポート
from routes.admin import admin_bp
from debug import debug_bp  # ← これを追加！
from config import Config
from datetime import datetime, date, timezone, timedelta
import requests
import uuid
from flask_cors import CORS, cross_origin  # 🔥 追加
import json  # ← これを追加
import gc
import subprocess
from flask import send_file
from dotenv import load_dotenv
import os

load_dotenv()  # .env を読み込む

# ✅ グローバルで JST を定義（import の直後に記述する）
JST = timezone(timedelta(hours=9))

# ✅ どんな datetime も JST（タイムゾーンあり）に揃える関数
def to_jst(dt):
    if dt is None:
        return None
    if isinstance(dt, datetime):
        if dt.tzinfo is None:
            return dt.replace(tzinfo=timezone.utc).astimezone(JST)
        else:
            return dt.astimezone(JST)
    return None

app = Flask(__name__)
app.config.from_object(Config)  # Config クラスを読み込む

@app.context_processor
def inject_config():
    return dict(config=app.config)

# 日本語形式に日時を整形するJinjaフィルター
def format_datetime_jp(value):
    if value is None:
        return ''
    if isinstance(value, str):
        try:
            value = datetime.fromisoformat(value)
        except Exception:
            return value
    if value.tzinfo is None:
        value = value.replace(tzinfo=timezone.utc)
    return value.astimezone(JST).strftime('%Y年%-m月%-d日 %H:%M')


app.jinja_env.filters['datetime_jp'] = format_datetime_jp

# CORS の適用範囲を広げる
CORS(app, resources={r"/*": {"origins": "*"}})  # すべてのルートでCORS許可

# 必要な設定
# 修正後（環境変数から読み込む）
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'fallback_secret_key')

# データベースを初期化
db.init_app(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# カスタム AnonymousUserMixin クラスを設定
class CustomAnonymousUser(AnonymousUserMixin):
    id = None  # デフォルトの id 属性を追加

login_manager.anonymous_user = CustomAnonymousUser  # ログイン管理にカスタムクラスを登録

# Flask-Migrate を初期化
migrate = Migrate(app, db)

# ホームルート
@app.route('/')
def index():
    admin_url = url_for('admin.manage') if current_user.is_authenticated and current_user.has_role('admin') else None
    return render_template('index.html', user=current_user, admin_url=admin_url)

# ユーザーローダー関数
@login_manager.user_loader
def load_user(user_id):
    return User.query.filter_by(id=user_id).first()  # ✅ `users.id` を明確に指定

# ログインルート
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            login_user(user)
            flash('Logged in successfully.', 'success')
            return redirect(url_for('index'))
        else:
            flash('Invalid username or password.', 'danger')
    return render_template('login.html')

@app.context_processor
def inject_user():
    from flask_login import current_user
    return dict(user=current_user)

# ログアウトルート
@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'success')
    return redirect(url_for('login'))

from flask_login import login_required

@app.route('/protected')
@login_required
def protected_route():
    # current_user.id はログインが保証されているため安全に使用可能
    return f"Welcome, user {current_user.id}"

# ユーザー登録ルート
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if User.query.filter_by(username=username).first():
            flash('Username already exists.', 'danger')
        else:
            new_user = User(username=username)
            new_user.set_password(password)
            db.session.add(new_user)
            db.session.commit()
            flash('User registered successfully.', 'success')
            return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/api/manufacturers', methods=['GET'])
def get_manufacturers():
    manufacturers = Manufacturer.query.all()
    return {'data': [{'id': m.id, 'name': m.name} for m in manufacturers]}

@app.route('/api/ply_ratings', methods=['GET'])
def get_ply_ratings():
    ply_ratings = PlyRating.query.all()
    return {'data': [{'id': p.id, 'value': p.value} for p in ply_ratings]}

@app.route('/input', methods=['GET', 'POST'])
def input_page():
    form = CombinedForm()
    mode = request.args.get('mode', 'new')  # デフォルトは新規登録

    if request.method == 'GET':
        # セッションから無効データを取得してフォームに反映
        invalid_entries = session.pop('invalid_entries', [])
        invalid_common_data = session.pop('invalid_common_data', {})  # 共通データ
        # デバッグ: 無効データを確認
        print(f"Invalid entries from session: {invalid_entries}")
        # デバッグ: 無効データの確認
        print(f"Invalid entries: {invalid_entries}")
        print(f"Invalid common data: {invalid_common_data}")

        # フォームを表示
        return render_template(
            'input_page.html', 
            form=form, 
            invalid_entries=invalid_entries,
            invalid_common_data=invalid_common_data
            )

    elif request.method == 'POST':

        # `registration_date` を `datetime` 型で取得
        registration_date = datetime.now(JST)

        print(f"New registration_date (before saving to DB): {registration_date}")  # 追加
        # デバッグ出力
        print(f"New registration_date: {registration_date}")
        print(f"Final registration_date (datetime): {registration_date}")  # ✅ デバッグ出力
        # デバッグ用: 送信されたフォームデータを確認
        print(f"Received POST data: {request.form}")
        print(f"tread_depths raw value: {request.form.get('tread_depths')}")
        print(f"uneven_wear raw value: {request.form.get('uneven_wear')}")
        print(f"uneven_wears list: {request.form.getlist('uneven_wear[]')}")
        print(f"tread_depths list: {request.form.getlist('tread_depths[]')}")
        print(f"Received uneven_wear list: {request.form.getlist('uneven_wear[]')}")
        print(f"Received tread_depth list: {request.form.getlist('tread_depth[]')}")
        print(f"Single tread_depth: {request.form.get('tread_depth')}")
        print(f"List of tread_depths: {request.form.getlist('tread_depth[]')}")
        print(f"Single uneven_wear: {request.form.get('uneven_wear')}")
        print(f"List of uneven_wears: {request.form.getlist('uneven_wear[]')}")

        # 必須項目の取得
        width = request.form.get('width')
        aspect_ratio = request.form.get('aspect_ratio')
        inch = request.form.get('inch')
        ply_rating_raw = request.form.get('ply_rating')
        ply_rating = None if ply_rating_raw == "0" or not ply_rating_raw else int(ply_rating_raw)

        # ✅ `registration_date` は `datetime` 型のまま
        print(f"Final registration_date (datetime): {registration_date}")

        # 動的フォームのデータ取得
        manufacturers = request.form.getlist('manufacturer[]') or []
        manufacturing_years = request.form.getlist('manufacturing_year[]') or []
        tread_depths = [
            int(value) for value in request.form.getlist('tread_depth[]') if value.isdigit()
        ]
        uneven_wears = [
            int(value) for value in request.form.getlist('uneven_wear[]') if value.isdigit()
        ]
        other_details = request.form.getlist('other_details[]') or []

        # 単一値のデータをリストに追加
        single_manufacturer = request.form.get('manufacturer')
        single_manufacturing_year = request.form.get('manufacturing_year')
        single_tread_depth = request.form.get('tread_depth')
        single_uneven_wear = request.form.get('uneven_wear')
        single_other_detail = request.form.get('other_details', '')

        if single_manufacturer:
            manufacturers.insert(0, single_manufacturer)
        if single_manufacturing_year:
            manufacturing_years.insert(0, single_manufacturing_year)
        if single_tread_depth and single_tread_depth.isdigit():
            tread_depths.insert(0, int(single_tread_depth))
        if single_uneven_wear and single_uneven_wear.isdigit():
            uneven_wears.insert(0, int(single_uneven_wear))
        if single_other_detail:
            other_details.append(single_other_detail)

        # リストが空の場合のデフォルト値を補填
        if len(uneven_wears) < len(manufacturers):
            uneven_wears.extend([-1] * (len(manufacturers) - len(uneven_wears)))

        if len(tread_depths) < len(manufacturers):
            tread_depths.extend([0] * (len(manufacturers) - len(tread_depths)))

        if len(other_details) < len(manufacturers):
            other_details.extend([''] * (len(manufacturers) - len(other_details)))

        # デバッグ情報を出力
        print(f"Processed manufacturers: {manufacturers}")
        print(f"Processed manufacturing_years: {manufacturing_years}")
        print(f"Processed tread_depths: {tread_depths}")
        print(f"Processed uneven_wears: {uneven_wears}")
        print(f"Processed other_details: {other_details}")

        # 共通データの検証
        common_errors = []
        if not width:
            common_errors.append("幅を選択してください。")
        if not aspect_ratio:
            common_errors.append("扁平率を選択してください。")
        if not inch:
            common_errors.append("インチを選択してください。")

        invalid_common_data = {
            'width': width,
            'aspect_ratio': aspect_ratio,
            'inch': inch,
            'ply_rating': ply_rating,
            # ✅ 修正後（時刻も保持）
            'registration_date': registration_date.strftime('%Y-%m-%d %H:%M:%S'),
            'errors': common_errors
        }

        # 有効なデータと無効なデータを分離
        valid_entries = []
        invalid_entries = []

        for i in range(len(manufacturers)):
            errors = []
            if not manufacturers[i] or manufacturers[i] == "0":
                errors.append("メーカーを選択してください。")
            if tread_depths[i] <= 0:
                errors.append("残り溝を正しく入力してください。")
            if uneven_wears[i] < 0:
                errors.append("片減りを正しく入力してください。")

            if errors:
                # 無効データの処理
                invalid_entries.append({
                    'id': str(uuid.uuid4()),  # ユニークIDを生成
                    'index': i + 1,
                    'errors': errors,
                    'manufacturer': manufacturers[i],
                    'manufacturing_year': manufacturing_years[i] if i < len(manufacturing_years) else '',
                    'tread_depth': tread_depths[i] if i < len(tread_depths) else '',
                    'uneven_wear': uneven_wears[i] if i < len(uneven_wears) else '',
                    'other_details': other_details[i] if i < len(other_details) else ''
                })
            else:
                # 有効データの処理
                valid_entries.append({
                    'manufacturer': manufacturers[i],
                    'manufacturing_year': manufacturing_years[i] if i < len(manufacturing_years) else None,
                    'tread_depth': tread_depths[i],
                    'uneven_wear': uneven_wears[i],
                    'other_details': other_details[i]
                })

        # デバッグコードをここに挿入
        print(f"Valid entries: {valid_entries}")
        print(f"Invalid entries: {invalid_entries}")

    # データ登録 (有効データがあれば処理)
    if valid_entries:
        try:
            ids = []
            for entry in valid_entries:
                new_tire = InputPage(
                    registration_date=registration_date,  # ✅ 修正ポイント
                    created_by=current_user.id if current_user.is_authenticated else 0,  # ★ 追加
                    width=width,
                    aspect_ratio=aspect_ratio,
                    inch=inch,
                    ply_rating=ply_rating,
                    manufacturer=entry['manufacturer'],
                    manufacturing_year=entry['manufacturing_year'],
                    tread_depth=entry['tread_depth'],
                    uneven_wear=entry['uneven_wear'],
                    other_details=entry['other_details'],
                    is_dispatched=False
                )
                db.session.add(new_tire)
                db.session.commit()
                print(f"New tire registered: {new_tire.id}")  # 新規登録の確認
                ids.append(new_tire.id)
            print(f"Valid entries registered with IDs: {ids}")
            # ✅ デバッグで IDs を表示
            print(f"Valid entries registered with IDs (before redirect): {ids}")
            
                      
        except Exception as e:
            db.session.rollback()
            print(f"Error during registration: {e}")
            flash("登録中にエラーが発生しました。", "danger")
            return redirect(url_for('register_success', ids=','.join(map(str, ids)), width=width, aspect_ratio=aspect_ratio, inch=inch, ply_rating=ply_rating, registration_date=registration_date))
    
    # ✅ 常に `invalid_common_data` を作成  ← コメントは残して OK
    if common_errors or invalid_entries:                 # ★ この行を追加
        session['invalid_common_data'] = {
            'width': width,
            'aspect_ratio': aspect_ratio,
            'inch': inch,
            'ply_rating': ply_rating,
            'registration_date': registration_date.strftime('%Y-%m-%d'),
            'errors': common_errors if common_errors else []
        }
    else:                                                # ★ この行と次を追加
        session.pop('invalid_common_data', None)

    # ✅ 有効データがある場合、`session` に `ids` を保存
    if valid_entries:
        session['valid_entry_ids'] = ids
    
    if invalid_entries:
        session['invalid_entries'] = invalid_entries

        flash("一部のデータが無効です。エラー内容をご確認ください。", "warning")
        # **変更箇所**: 無効データがある場合は`register_success`にリダイレクト
        return redirect(url_for('register_success'))

    # ✅ デバッグで IDs を表示
    print(f"Valid entries registered with IDs (before redirect): {ids}")

    # 登録確認ページへ遷移
    return redirect(url_for(
        'register_success',
        ids=','.join(map(str, ids)) if ids else '',
        width=width,
        aspect_ratio=aspect_ratio,
        inch=inch,
        ply_rating=ply_rating,
        registration_date=registration_date.strftime('%Y-%m-%d %H:%M:%S')  # ← ✅ 修正ポイント
    ))
    
    # 有効データがない場合は無効データのみ確認画面に渡す
    #return redirect(url_for('register_success', ids=''))
        
@app.route('/register_success')
def register_success():
    # URL引数から `ids` を取得
    ids = request.args.get('ids', '')  # デフォルト値を空文字列に設定
    session_ids = session.pop('valid_entry_ids', [])  # `session` から取得
    
    # URLから取得した `ids` が空なら、セッションの `ids` を使用
    if not ids and session_ids:
        ids = session_ids
    else:
        ids = ids.split(',') if isinstance(ids, str) and ids else []
    
    print(f"IDs for query: {ids}")  # デバッグ用
        
    # 無効データをセッションから取得
    invalid_entries = session.get('invalid_entries', [])
    invalid_common_data = session.get('invalid_common_data', {})

    # ✅ `registration_date` を明示的に取得する
    registration_date = request.args.get('registration_date') or invalid_common_data.get('registration_date')

    # `registration_date` の型を統一
    if registration_date:
        try:
            # 文字列なら `datetime` に変換
            if isinstance(registration_date, str):
                if len(registration_date) == 10:  # 'YYYY-MM-DD' の場合
                    registration_date = datetime.strptime(registration_date, '%Y-%m-%d')
                elif len(registration_date) == 19:  # 'YYYY-MM-DD HH:MM:SS' の場合
                    registration_date = datetime.strptime(registration_date, '%Y-%m-%d %H:%M:%S')
            # ✅ JST になってない場合だけ補正する（←重要！）
            if registration_date.tzinfo is None:
                registration_date = registration_date.replace(tzinfo=JST)
        except ValueError:
            registration_date = None  # 変換エラーが起きたら `None`
    else:
        registration_date = None  # `None` を許容
    
    # ✅ データベースから有効データを取得
    valid_tires = InputPage.query.filter(InputPage.id.in_(ids)).all() if ids else []

    # `valid_tires` から `registration_date` を取得（必要なら）
    if valid_tires and registration_date is None:
        registration_date = valid_tires[0].registration_date  # 最初のタイヤの登録日を使用
        if registration_date and registration_date.tzinfo is None:
            registration_date = registration_date.replace(tzinfo=timezone.utc).astimezone(JST)
  
    # クエリが空の場合のデバッグ出力
    if not ids:
        print("No IDs provided for query.")
    
    # ✅ デバッグ出力
    print(f"IDs for query: {ids}")
    print(f"Registration Date from URL: {request.args.get('registration_date')}")
    print(f"Registration Date from Session: {invalid_common_data.get('registration_date')}")
    # デバッグ用: tires の内容を確認
    print(f"Register success: IDs={ids}, Tires={valid_tires}")
    print(f"Tires retrieved: {valid_tires}")  # デバッグ用
    return render_template(
        'register_success.html',
        tires=valid_tires,
        invalid_entries=invalid_entries,
        invalid_common_data=invalid_common_data,
        width=request.args.get('width'),
        aspect_ratio=request.args.get('aspect_ratio'),
        inch=request.args.get('inch'),
        ply_rating=request.args.get('ply_rating'),
        registration_date=registration_date  # ✅ ここで反映
        )
 
@app.route('/search', methods=['GET', 'POST'])
def search_page():
    form = SearchForm()
    tires = []  # 検索結果を保持する変数
    # 初期状態で selected_tires をクリア 
    selected_tires = session.get('selected_tires', [])  # セッションから選択されたタイヤを取得
    search_conditions = session.get('search_conditions', {})
    
    # GETリクエストまたは「戻る」で復元する場合
    if request.args.get('from_dispatch_confirm'):
        # dispatch_confirmから戻ってきた場合
        print("GET action from dispatch_confirm triggered")
        # セッションに保存された条件をフォームに反映
        form.width.data = search_conditions.get('width', '')
        form.aspect_ratio.data = search_conditions.get('aspect_ratio', '')
        form.inch.data = search_conditions.get('inch', '')
        form.ply_rating.data = search_conditions.get('ply_rating', '')

        # 検索クエリの実行
        query = InputPage.query.filter_by(
            width=search_conditions.get('width'),
            aspect_ratio=search_conditions.get('aspect_ratio'),
            inch=search_conditions.get('inch')
        )
        if search_conditions.get('ply_rating') and search_conditions['ply_rating'] != '0':
            query = query.filter(InputPage.ply_rating == search_conditions['ply_rating'])
        tires = query.filter(InputPage.is_dispatched == False).all()
        
        # クエリ結果をデバッグ
        print(f"GET action from dispatch_confirm - Conditions: {search_conditions}")
        print(f"Tires after GET action: {[tire.id for tire in tires]} -> Count: {len(tires)}")

        # 選択済みタイヤを検索結果に追加
        existing_tire_ids = {tire.id for tire in tires}
        selected_tire_ids = set(session.get('selected_tires', []))
        # すでに検索結果に含まれるタイヤは除外する
        additional_tires = [
            InputPage.query.get(tire_id) for tire_id in selected_tire_ids if tire_id not in existing_tire_ids
            and tire_id is not None  # Noneのタイヤも排除
        ]
        # Noneを除外して追加
        tires.extend([tire for tire in additional_tires if tire and tire.id not in existing_tire_ids])

        # 更新後の重複チェックを追加
        existing_tire_ids.update(tire.id for tire in tires)

        # デバッグコード
        print(f"Existing tire IDs: {existing_tire_ids}")
        print(f"Selected tire IDs: {selected_tire_ids}")
        print(f"Additional tires to add: {[tire.id for tire in additional_tires if tire]}")
        print(f"Final tires in result: {[tire.id for tire in tires]}")

    elif request.method == 'POST':
        if form.validate_on_submit():
            session['selected_tires'] = []
            # フォームから値を取得して検索条件を作成
            search_conditions = {
                'width': form.width.data,
                'aspect_ratio': form.aspect_ratio.data,
                'inch': form.inch.data,
                'ply_rating': form.ply_rating.data,
            }
            session['search_conditions'] = search_conditions  # セッションに保存
            # 検索クエリの実行
            query = InputPage.query.filter_by(
                width=search_conditions['width'],
                aspect_ratio=search_conditions['aspect_ratio'],
                inch=search_conditions['inch']
            )
            # ply_rating の条件追加
            if search_conditions['ply_rating'] and search_conditions['ply_rating'] != '0':
                query = query.filter(InputPage.ply_rating == search_conditions['ply_rating'])
            # 出庫されていないタイヤのみを取得
            tires = query.filter(InputPage.is_dispatched == False).all()
            # デバッグログ
            print(f"SEARCH action - Conditions: {search_conditions}")
            print(f"Tires after SEARCH action: {[tire.id for tire in tires]} -> Count: {len(tires)}")
        
        # デバッグログ
        print(f"GET action from dispatch_confirm - Conditions: {search_conditions}")
        print(f"Tires after GET action: {[tire.id for tire in tires]} -> Count: {len(tires)}")
        
    else:
        # 初期画面または他の処理
        tires = []
    
    # 最終的にテンプレートをレンダリングして結果を表示
    return render_template(
        'search_page.html', 
        form=form, 
        tires=tires, 
        selected_tires=selected_tires, 
        search_conditions=search_conditions  # 検索条件を渡す
    )

@app.route('/dispatch/confirm', methods=['GET', 'POST'], endpoint='dispatch_confirm')
def dispatch_confirm():
    # POSTリクエスト（出庫ボタンが押された場合）
    if request.method == 'POST':
        # 確認ボタンから送信されたタイヤIDリストを取得
        selected_tires = request.form.getlist('tire_ids')
        print(f"POST action - Selected tires: {selected_tires}")
        # 確認リストが空の場合のエラーメッセージ
        if not selected_tires:
            flash("出庫するタイヤが確認されていません。", "warning")
            return redirect(url_for('search_page'))

        # セッションに確認されたタイヤを保存し、出庫処理へ移動
        session['selected_tires'] = list(set(selected_tires))

        # デバッグコード
        print(f"POST action - Session updated selected tires: {session['selected_tires']}")

        return redirect(url_for('dispatch_confirm'))  # 出庫処理へリダイレクト
    
    # 「戻る」ボタンで検索画面に戻る場合
    if request.args.get('action') == 'back':
        print("Back action triggered from dispatch_confirm")
        return redirect(url_for('search_page', from_dispatch_confirm=True))

    # GETリクエスト（初めて確認画面を開いた場合）
    selected_tires = session.get('selected_tires', [])
    tires_to_dispatch = [InputPage.query.get(tire_id) for tire_id in selected_tires]

    # ✅ 出庫日を JST で取得し、マイクロ秒をカット
    dispatch_date = datetime.now(JST).replace(microsecond=0)
    formatted_dispatch_date = dispatch_date.strftime('%Y-%m-%d')  # 日付のみの形式に変換
    print(f"仮の出庫日: {formatted_dispatch_date}")  # デバッグ

    
    # デバッグログ
    print(f"GET action - Tires to dispatch: {[tire.id for tire in tires_to_dispatch]} -> Count: {len(tires_to_dispatch)}")
    
    return render_template(
        'dispatch_confirm.html', 
        tires_to_dispatch=tires_to_dispatch, 
        dispatch_date=dispatch_date  # ← ✅ datetime型のまま渡す！
    )

@app.route('/dispatch', methods=['GET', 'POST'])
def dispatch():
    # デバッグログ
    print(f"Request method: {request.method}")
    print(f"Session selected tires before processing: {session.get('selected_tires')}")
    print(f"🚀 Before processing, session['selected_tires']: {session.get('selected_tires')}")
    selected_tires = session.get('selected_tires', [])
    processed_tire_ids = []  # 処理済みタイヤIDのリスト
    dispatch_date = datetime.now(JST).replace(microsecond=0)  # ✅ `datetime` 型で統一
    try:
        # データベース処理: 確認済みタイヤを出庫処理
        for tire_id in selected_tires:
            print(f"Processing tire ID: {tire_id}")
            tire = InputPage.query.get(tire_id)  # タイヤ情報を取得
            if tire and not tire.is_dispatched:  # 未出庫のタイヤのみ処理
                tire.is_dispatched = True  # 出庫済みフラグを設定

                # 出庫履歴を記録
                new_dispatch = DispatchHistory(
                    tire_id=tire_id,
                    user_id=current_user.id if current_user.is_authenticated else 0,  # ✅ `users.id` を正しく参照
                    dispatch_date=dispatch_date  # ✅ `datetime` 型で統一
                )
                db.session.add(new_dispatch)

                # ✅ 編集者・日時を input_page に記録
                user_id = current_user.id if current_user.is_authenticated else 0
                tire.last_edited_by = user_id
                tire.last_edited_at = dispatch_date

                processed_tire_ids.append(tire_id)
        print("Committing changes to the database...")
        # データベースの変更を保存
        db.session.commit()
        print(f"Processed tire IDs: {processed_tire_ids}")
        session['processed_tires'] = processed_tire_ids
        session.modified = True  # ✅ セッション変更を明示
        
        print(f"✅ After processing, session['processed_tires']: {session.get('processed_tires')}")

        flash("出庫処理が完了しました。", "success")
    except Exception as e:
        # エラー発生時はロールバック
        db.session.rollback()
        print(f"Database error: {e}")  # デバッグログを強化
        flash(f"エラーが発生しました: {e}", "danger")
        return jsonify({"error": "Database commit failed"}), 500  # ✅ エラー時に即座に処理を中断

    # 処理完了後、出庫履歴画面にリダイレクト
    return redirect(url_for('dispatch_page'))

@app.route("/session_check", methods=["GET"])
def check_session():
    return jsonify({"processed_tires": session.get("processed_tires", [])})

@app.route('/dispatch_page', methods=['GET'])
def dispatch_page():
    # デバッグログ
    print("Accessing dispatch page")
    try:
        # 出庫履歴から今回の出庫データを取得
        processed_tire_ids = session.get('processed_tires', [])  # セッションから取得
        dispatch_history = DispatchHistory.query.filter(DispatchHistory.tire_id.in_(processed_tire_ids)).all()

        # 出庫対象タイヤを再取得
        tires_to_dispatch = [
            InputPage.query.get(dispatch.tire_id) for dispatch in dispatch_history
        ]
        
        # デバッグ: 各タイヤの `price` を確認
        for tire in tires_to_dispatch:
            print(f"Debug: Tire ID {tire.id if tire else 'None'} - Price: {tire.price if tire and tire.price is not None else 'None'}")

        # ここで dispatch_date を取得（最初のデータのみを使用）
        dispatch_date = dispatch_history[0].dispatch_date if dispatch_history else None
        print(f"Dispatch Date: {dispatch_date}")

        # 合計数と合計金額を計算
        total_tires = len(tires_to_dispatch)
        total_price = sum(tire.price for tire in tires_to_dispatch if tire and tire.price)

        # 消費税と税込み合計金額を計算
        tax = total_price * 0.1  # 消費税10%
        total_price_with_tax = total_price + tax
        
        # デバッグログ
        print(f"Processed tire IDs: {processed_tire_ids}")
        print(f"Tires to dispatch: {[tire.id for tire in tires_to_dispatch if tire]}")

        return render_template(
            'dispatch_page.html',
            tires_to_dispatch=tires_to_dispatch,
            total_tires=total_tires,
            total_price=total_price,
            tax=tax,
            total_price_with_tax=total_price_with_tax,
            dispatch_date=dispatch_date  # ✅ フォーマット済みの日付を渡す
        )
    except Exception as e:
        print(f"Error fetching dispatch history: {e}")
        flash(f"エラーが発生しました: {e}", "danger")
        return redirect(url_for('search_page'))
    
# ✅ Google Apps Script の API エンドポイント (※ 必ず正しい URL に変更)
GAS_API_URL = "https://script.google.com/macros/s/AKfycbxc7tMdBSylkv7Zvr9oLAEfTxLqwZ_TN1ztv6Mb6jWl5WnsYaUckyVgWGVL_ORTRc7G/exec"

### =========================================
### ✅ `/shipments` → タイヤ ID を受け取り詳細データを GAS へ送信
### =========================================
@app.route("/shipments", methods=["OPTIONS", "POST"])
def get_shipments():
    """フロントエンドから受け取ったタイヤ ID を元にデータベースから詳細情報を取得し、GAS へ送信する"""
    
    if request.method == "OPTIONS":
        response = jsonify({"message": "CORS preflight response"})
        response.headers.add("Access-Control-Allow-Origin", "*")
        response.headers.add("Access-Control-Allow-Methods", "POST, GET, OPTIONS")
        response.headers.add("Access-Control-Allow-Headers", "Content-Type")
        return response, 200

    data = request.get_json()
    if not data or "tire_ids" not in data:
        return jsonify({"error": "No tire IDs provided"}), 400

    # ✅ `outerjoin` を使用して NULL の場合も取得できるようにする
    tires = (
        db.session.query(
            InputPage.id,
            Manufacturer.name.label("manufacturer"),
            Width.value.label("width"),
            AspectRatio.value.label("aspect_ratio"),
            Inch.value.label("inch"),
            PlyRating.value.label("ply_rating"),
            InputPage.manufacturing_year,
            InputPage.tread_depth,
            InputPage.uneven_wear,
            InputPage.other_details,
            InputPage.price
        )
        .outerjoin(Manufacturer, InputPage.manufacturer == Manufacturer.id)
        .outerjoin(Width, InputPage.width == Width.id)
        .outerjoin(AspectRatio, InputPage.aspect_ratio == AspectRatio.id)
        .outerjoin(Inch, InputPage.inch == Inch.id)
        .outerjoin(PlyRating, InputPage.ply_rating == PlyRating.id)
        .filter(InputPage.id.in_(data["tire_ids"]))
        .all()
    )

    if not tires:
        return jsonify({"error": "No matching tires found"}), 404

    # ✅ GAS に送るデータを組み立て
    shipment_data = [
        {
            "id": tire.id,
            "manufacturer": tire.manufacturer,
            "width": tire.width,
            "aspect_ratio": tire.aspect_ratio,
            "inch": tire.inch,
            "ply_rating": tire.ply_rating,
            "manufacturing_year": tire.manufacturing_year,
            "tread_depth": tire.tread_depth,
            "uneven_wear": tire.uneven_wear,
            "other_details": tire.other_details,
            "price": tire.price
        }
        for tire in tires
    ]

    payload = {
        "shipments": shipment_data,
        "dispatch_date": datetime.now(JST).strftime("%Y-%m-%d")  # ✅ JST に統一
    }

    # ✅ デバッグ用ログ
    print("🚀 送信するデータ:", json.dumps(payload, ensure_ascii=False, indent=2))

    # ✅ GAS にデータを送信
    response = requests.post(GAS_API_URL, json=payload)

    return jsonify({"status": "success", "gas_response": response.text}), 200

### =========================================
### ✅ `/send_to_gas` → 確定した出庫データを GAS に送信
### =========================================
@app.route('/send_to_gas', methods=['POST'])
def send_to_gas():
    data = request.get_json()
    print("📥 Flask側で受け取ったJSON:", data)
    """確定した出庫データを GAS に送信し、スプレッドシート記録 & PDF 生成"""

    try:
        # ✅ 出庫履歴から今回の出庫データを取得
        processed_tire_ids = session.get('processed_tires', [])  # セッションから取得
        print(f"🚀 DEBUG: processed_tire_ids = {processed_tire_ids}")  # デバッグ追加

        if not processed_tire_ids:
            return jsonify({"error": "No processed tire IDs found"}), 400

        dispatch_history = DispatchHistory.query.filter(DispatchHistory.tire_id.in_(processed_tire_ids)).all()
        print(f"🚀 DEBUG: dispatch_history = {[d.tire_id for d in dispatch_history]}")  # デバッグ追加

        if not dispatch_history:
            return jsonify({"error": "No dispatch records found"}), 404

        # ✅ `JOIN` を使用してデータを取得 (外部結合 & int() 適用)
        tires_to_dispatch = (
            db.session.query(
                InputPage.id,
                Manufacturer.name.label("manufacturer"),
                Width.value.label("width"),
                AspectRatio.value.label("aspect_ratio"),
                Inch.value.label("inch"),
                PlyRating.value.label("ply_rating"),
                InputPage.manufacturing_year,
                InputPage.tread_depth,
                InputPage.uneven_wear,
                InputPage.other_details,
                InputPage.price
            )
            .outerjoin(Manufacturer, InputPage.manufacturer == Manufacturer.id)
            .outerjoin(Width, InputPage.width == Width.id)
            .outerjoin(AspectRatio, InputPage.aspect_ratio == AspectRatio.id)
            .outerjoin(Inch, InputPage.inch == Inch.id)
            .outerjoin(PlyRating, InputPage.ply_rating == PlyRating.id)
            .filter(InputPage.id.in_([int(dispatch.tire_id) for dispatch in dispatch_history]))
            .all()
        )

        print(f"🚀 DEBUG: tires_to_dispatch = {[t.id for t in tires_to_dispatch]}")  # デバッグ追加

        if not tires_to_dispatch:
            print("🚨 ERROR: No matching tires found in InputPage.")
            return jsonify({"error": "No tires found for dispatch"}), 404

        # ✅ 出庫日を取得（最初のデータを使用）
        dispatch_date = None
        if dispatch_history:
            first_dispatch = dispatch_history[0].dispatch_date
            if isinstance(first_dispatch, datetime) and first_dispatch.tzinfo is None:
                dispatch_date = (first_dispatch + timedelta(hours=9)).strftime('%Y年%-m月%-d日 %H:%M')
            else:
                dispatch_date = first_dispatch.astimezone(JST).strftime('%Y年%-m月%-d日 %H:%M')

        # ✅ 合計数と合計金額を計算
        total_tires = len(tires_to_dispatch)
        total_price = sum(tire.price for tire in tires_to_dispatch if tire and tire.price)
        tax = int(total_price * 0.1)  # 消費税10%
        total_price_with_tax = total_price + tax

        # ✅ GAS に送るデータを組み立て
        payload = {
            "dispatch_date": dispatch_date,
            "common_data": {
                "width": tires_to_dispatch[0].width if tires_to_dispatch else None,
                "aspect_ratio": tires_to_dispatch[0].aspect_ratio if tires_to_dispatch else None,
                "inch": tires_to_dispatch[0].inch if tires_to_dispatch else None,
                "ply_rating": tires_to_dispatch[0].ply_rating if tires_to_dispatch else None
            },
            "shipments": [
                {
                    "id": tire.id,
                    "manufacturer": tire.manufacturer,
                    "manufacturing_year": tire.manufacturing_year,
                    "tread_depth": tire.tread_depth,
                    "uneven_wear": tire.uneven_wear,
                    "ply_rating": tire.ply_rating,
                    "other_details": tire.other_details,
                    "price": tire.price
                } for tire in tires_to_dispatch
            ],
            "total_tires": total_tires,
            "total_price": total_price,
            "tax": tax,
            "total_price_with_tax": total_price_with_tax
        }

        # ✅ デバッグ出力
        print("🚀 送信するデータ:", json.dumps(payload, ensure_ascii=False, indent=2))

    # ✅ 修正済：responseの安全な利用
        try:
            response = requests.post(GAS_API_URL, json=payload)
            response.raise_for_status()

            response_text = response.text
            print(f"✅ GASからのレスポンス: {response_text}")

            del payload
            del response
            gc.collect()

            try:
                gas_response = json.loads(response_text)
            except ValueError:
                gas_response = {"error": "Invalid JSON response from GAS", "response_text": response_text}

            # ✅ PDF URL を取り出して、JSONで返すようにする
            pdf_url = gas_response.get("pdf_url")
            if not pdf_url:
                return jsonify({"status": "error", "message": "PDF URL が取得できませんでした"}), 500

            # ✅ JavaScript 側で処理できるよう JSONで返す
            return jsonify({"status": "success", "pdf_url": pdf_url})

        except requests.exceptions.RequestException as e:
            print(f"❌ GASへのリクエストエラー: {e}")
            return jsonify({"status": "error", "message": str(e)}), 500

    except requests.exceptions.RequestException as e:
        print(f"❌ GASへのリクエストエラー: {e}")  # エラーログを出力
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/pdf_ready')
def pdf_ready():
    pdf_url = request.args.get("pdf_url")
    return render_template("preview.html", pdf_url=pdf_url)


@app.route('/generate-pdf', methods=['POST'])
def generate_pdf():
    print("🚀 Flask: /generate-pdf にリクエストを受信")

    try:
        gas_response = request.json  # GAS のレスポンスを受け取る
        print("📥 Flask: 受信データ →", gas_response)

        pdf_url = gas_response.get("pdf_url")
        if not pdf_url:
            raise ValueError("🚨 Flask: PDF URL が None です")

        print("✅ Flask: 受信した PDF URL →", pdf_url)
            
        # ✅ フロントエンドに JSON で返す
        return jsonify({
            "status": "success",
            "pdf_url": pdf_url
        })

    except Exception as e:
        print("🚨 Flask: エラー発生", str(e))
        return jsonify({"error": "サーバーエラー: " + str(e)}), 500

@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit_page(id):
    tire = InputPage.query.get_or_404(id)
    form = EditForm(obj=tire)

    if request.method == "POST":
        if form.validate_on_submit():
            old_data = {
                'width': tire.width,
                'aspect_ratio': tire.aspect_ratio,
                'inch': tire.inch,
                'ply_rating': tire.ply_rating,
                'manufacturer': tire.manufacturer,
                'manufacturing_year': tire.manufacturing_year,
                'tread_depth': tire.tread_depth,
                'uneven_wear': tire.uneven_wear,
                'other_details': tire.other_details,
                'price': tire.price
            }

            # フォームの内容でタイヤ情報を更新
            form.populate_obj(tire)

            # ---------- ★ 追加：0 → None 変換 ----------
            ply_val = form.ply_rating.data       # 0 または 実ID
            tire.ply_rating = ply_val if ply_val else None
            # -------------------------------------

            edit_details = []
            updated = False

            for field, old_value in old_data.items():
                new_value = getattr(tire, field)
                if old_value != new_value:
                    if field == 'price':
                        formatted_old_price = "{:,.0f}".format(old_value) if old_value is not None else "なし"
                        formatted_new_price = "{:,.0f}".format(new_value) if new_value is not None else "なし"
                        edit_details.append(f"価格: {formatted_old_price} → {formatted_new_price}")
                    else:
                        edit_details.append(f"{field}: {old_value} → {new_value}")
                    updated = True

            if updated:
                new_edit = HistoryPage(
                    tire_id=id,
                    user_id=current_user.id if current_user.is_authenticated else 0,  # ✅ `users.id` に統一
                    action="編集",
                    edit_date=datetime.now(JST),
                    details=", ".join(edit_details)
                )
                db.session.add(new_edit)

            try:
                db.session.commit()
                flash("編集が完了しました。", "success")
            except Exception as e:
                db.session.rollback()
                flash("データの保存に失敗しました。", "danger")

            return redirect(url_for('history_page'))
        else:
            flash("フォームのバリデーションに失敗しました。", "danger")

    return render_template('edit_page.html', form=form, tire=tire)

@app.route('/history')
def history_page():
    import logging

    logging.basicConfig()
    logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)
    # 出庫履歴を取得（新しい順）
    dispatch_history = DispatchHistory.query.all()

    # 編集履歴を取得（新しい順）
    edit_history = HistoryPage.query.all()
    # 各レコードの `dispatch_date` のデータ型と値を確認
    for record in dispatch_history:
        print(f"デバッグ: {record.dispatch_date} (型: {type(record.dispatch_date)})")

    # 出庫履歴を共通フォーマットに変換
    dispatch_records = []  # ここでリストを定義
    for record in dispatch_history:
        user = User.query.get(record.user_id)
        dispatch_records.append({
            "tire_id": record.tire_id,
            "date": to_jst(record.dispatch_date),
            "user_id": record.user_id,
            "user_name": user.username if user else "不明",  # 👈 追加
            "action": "出庫",
            "details": record.dispatch_note or "出庫処理"
        })

    # 編集履歴を共通フォーマットに変換
    edit_records = []
    for record in edit_history:
        user = User.query.get(record.user_id)  # 🔍 ユーザー情報を取得
        edit_records.append({
            "tire_id": record.tire_id,
            "date": to_jst(record.edit_date),
            "user_id": record.user_id,
            "user_name": user.username if user else "不明",  # 👈 追加
            "action": record.action,
            "details": record.details
        })
        
    # 履歴を統合し、新しい順（降順）にソート
    combined_history = sorted(dispatch_records + edit_records, key=lambda x: x["date"], reverse=True)


    return render_template('history_page.html', history=combined_history)

@app.route('/alerts')
def alert_page():
    alerts = AlertPage.query.all()
    return render_template('alert_page.html', alerts=alerts)

@app.route('/inventory_list', methods=['GET', 'POST'])
def inventory_list():
    form = SearchForm()
    edit_forms = {}
    query = InputPage.query.order_by(InputPage.id.desc())
    price_alert = False  # ← 通知モーダル表示用のフラグ
    tires = []  # ← 🔧 POST時のために仮定義しておく

    # GET時：価格未登録がある場合はそれを優先表示
    if request.method == 'GET':
        unpriced = InputPage.query.filter(InputPage.price == None, InputPage.is_dispatched.is_(False)).all()
        if unpriced:
            tires = unpriced
            price_alert = True  # ← モーダル表示用
        else:
            tires = query.filter(InputPage.is_dispatched.is_(False)).all()
    
    # JST補正（登録日・編集日）
    for tire in tires:
        if isinstance(tire.registration_date, datetime) and tire.registration_date.tzinfo is None:
            tire.registration_date = tire.registration_date.replace(tzinfo=timezone.utc).astimezone(JST)
        if isinstance(tire.last_edited_at, datetime) and tire.last_edited_at.tzinfo is None:
            tire.last_edited_at = tire.last_edited_at.replace(tzinfo=timezone.utc).astimezone(JST)

    # POSTリクエスト処理（フィルタリング）
    if request.method == 'POST':
        print("📝 送信された内容:", request.form)

        if 'reset' in request.form:
            query = InputPage.query
            tires = query.order_by(InputPage.id.desc()).all()

        elif 'filter_in_stock' in request.form:
            query = InputPage.query.filter(InputPage.is_dispatched.is_(False))
            tires = query.order_by(InputPage.id.desc()).all()

        elif 'filter_dispatched' in request.form:
            query = InputPage.query.filter(InputPage.is_dispatched.is_(True))
            tires = query.order_by(InputPage.id.desc()).all()

        elif 'filter_unpriced' in request.form:
            query = InputPage.query.filter(InputPage.price.is_(None))
            tires = query.order_by(InputPage.id.desc()).all()

        elif 'search' in request.form:
            if form.validate_on_submit():
                query = InputPage.query
                if form.registration_date.data:
                    target = form.registration_date.data
                    next_day = target + timedelta(days=1)
                    query = query.filter(InputPage.registration_date >= target,
                                        InputPage.registration_date < next_day)
                tires = query.order_by(InputPage.id.desc()).all()
            else:
                flash("日付の形式が正しくありません。", "warning")
                tires = []

        else:
            tires = InputPage.query.order_by(InputPage.id.desc()).all()

    # 🔹 一括更新処理（履歴記録を追加）
    if request.method == 'POST' and 'update_all' in request.form:
        updated = False  # ✅ ← ここで定義しておくと後で使える！

        for tire in tires:
            print(f"⛏️ チェック中: tire.id = {tire.id}, price = {tire.price}, other_details = {tire.other_details}")

            price_key = f"price_{tire.id}"
            other_details_key = f"other_details_{tire.id}"

            old_price = tire.price
            old_details = tire.other_details

            edit_details = []

            # 価格を更新
            if price_key in request.form:
                new_price_str = request.form[price_key].replace(',', '').strip()
                if new_price_str:
                    try:
                        new_price = int(new_price_str)
                        if old_price != new_price:
                            tire.price = new_price
                            edit_details.append(f"価格: {old_price} → {new_price}")
                            updated = True
                    except ValueError:
                        print(f"Invalid price value for tire ID {tire.id}, skipping update.")
                else:
                    print(f"No new price provided for tire ID {tire.id}, skipping update.")
            
            # その他の詳細を更新
            if other_details_key in request.form and request.form[other_details_key]:
                new_details = request.form[other_details_key].strip()
                if old_details != new_details:
                    tire.other_details = new_details
                    edit_details.append(f"詳細: {old_details} → {new_details}")
                    updated = True

            # ✅ 変更があった場合のみ履歴と編集者情報を記録
            if edit_details:
                user_id = current_user.id if current_user.is_authenticated else 0

                # 履歴を追加
                new_edit = HistoryPage(
                    tire_id=tire.id,
                    user_id=user_id,
                    action="一括更新",
                    edit_date=datetime.now(JST),
                    details=", ".join(edit_details)
                )
                db.session.add(new_edit)

                # 編集者情報をタイヤにも記録
                tire.last_edited_by = user_id
                tire.last_edited_at = datetime.now(JST)
        # ✅ 最後に一括でコミット＆通知
        try:
            db.session.commit()
            flash("在庫データが更新されました。", "success")
        except Exception as e:
            db.session.rollback()
            print(f"Error committing to the database: {e}")
            flash("データの保存に失敗しました。", "danger")

        return redirect(url_for('inventory_list'))
    
    # ===== 差し替え開始 ==================================================
    # 登録者・編集者に登場する user_id をまとめて取得
    creator_ids = {t.created_by for t in tires if t.created_by}
    editor_ids  = {t.last_edited_by for t in tires if t.last_edited_by}
    user_ids    = creator_ids.union(editor_ids)

    users     = User.query.filter(User.id.in_(user_ids)).all()
    user_map  = {u.id: u.username for u in users}

    for tire in tires:
        # 登録者
        tire.created_name = user_map.get(tire.created_by, "不明") if tire.created_by else ""
        tire.created_time = tire.registration_date

        # 最終更新者
        tire.last_edited_name = user_map.get(tire.last_edited_by, "") if tire.last_edited_by else ""
        tire.last_edited_time = tire.last_edited_at

        # 表示用（更新があれば更新者、なければ登録者）
        if tire.last_edited_at:
            tire.display_name = tire.last_edited_name or tire.created_name
            tire.display_time = tire.last_edited_time
        else:
            tire.display_name = tire.created_name
            tire.display_time = tire.created_time

    return render_template(
        'inventory_list.html',
        form=form,
        tires=tires,
        price_alert=price_alert
    )
    # ===== 差し替え終了 ==================================================

# Blueprintの登録
app.register_blueprint(admin_bp)
app.register_blueprint(debug_bp)  # ← これを追加！

# 金額を3桁区切りでフォーマットするカスタムフィルタ
@app.template_filter('currency')
def format_currency(value):
    if value is None:
        return ""  # 値がない場合は空文字を返す
    try:
        # 金額を3桁区切りの整数形式でフォーマット
        return "{:,.0f}".format(value)
    except ValueError:
        return value  # フォーマットに失敗した場合は元の値を返す

@app.route('/backup', methods=['GET'])
def backup_database():
    try:
        # PostgreSQL 接続情報（Renderの情報に書き換えてください）
        host = "dpg-cutev07noe9s73997blg-a.singapore-postgres.render.com"  # ← 正しいドメインに！
        user = "u_tire_app_user"
        dbname = "u_tire_app"
        port = "5432"
        output_file = "backup.dump"

        env = os.environ.copy()
        env["PGPASSWORD"] = os.getenv("PGPASSWORD")  # .envから読み込み

        # pg_dump コマンドの構築
        command = [
            "pg_dump",
            "-h", host,
            "-U", user,
            "-p", port,
            "-d", dbname,
            "-F", "c",
            "-f", output_file
        ]

        # 実行
        subprocess.run(command, check=True, env=env)

        # ファイル送信
        return send_file(output_file, as_attachment=True)

    except subprocess.CalledProcessError as e:
        return f"バックアップに失敗しました: {str(e)}", 500

if __name__ == '__main__':
    # print(app.url_map)  # 登録済みルートを確認
    app.run(debug=True)
