from flask import Blueprint, Flask, render_template, request, redirect, url_for,  jsonify, flash, session, Response, g
from flask_migrate import Migrate  # Flask-Migrate をインポート
from models import db, Width, AspectRatio, Inch, Manufacturer, PlyRating, InputPage, SearchPage, EditPage, HistoryPage, DispatchHistory, AlertPage, User, Role
from forms import SearchForm, EditForm, CombinedForm
from flask_login import LoginManager, UserMixin, login_user, logout_user, current_user, login_required, AnonymousUserMixin
from utils import role_required # role_requiredをインポート
from routes.admin import admin_bp
from config import Config
from datetime import datetime, date
import pdfkit

app = Flask(__name__)
app.config.from_object(Config)  # Config クラスを読み込む

# 必要な設定
app.config['SECRET_KEY'] = 'your_secret_key'

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
@login_required
def index():
    # 管理画面のリンクを生成
    admin_url = url_for('admin.manage')
    return render_template('base.html', user=current_user, admin_url=admin_url)

# ユーザーローダー関数
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

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

    if request.method == 'GET':
        # フォームを表示
        return render_template('input_page.html', form=form)

    elif request.method == 'POST':
        # デバッグ用: 送信されたフォームデータを確認
        print(f"Received POST data: {request.form}")
        print(f"tread_depths raw value: {request.form.get('tread_depths')}")
        print(f"uneven_wear raw value: {request.form.get('uneven_wear')}")
        print(f"uneven_wears list: {request.form.getlist('uneven_wear[]')}")
        print(f"tread_depths list: {request.form.getlist('tread_depths[]')}")
        # 共通データの取得
        registration_date = request.form.get('registration_date')
        if not registration_date:
            # registration_dateが指定されていない場合、現在日付を自動設定
            registration_date = date.today()
        width = request.form.get('width')
        aspect_ratio = request.form.get('aspect_ratio')
        inch = request.form.get('inch')
        ply_rating = request.form.get('ply_rating')

        # 動的フォームの個別データ取得
        manufacturers = request.form.getlist('manufacturer[]')
        manufacturing_years = request.form.getlist('manufacturing_year[]')
        tread_depths = request.form.getlist('tread_depth[]')
        uneven_wears = request.form.getlist('uneven_wear[]')
        uneven_wears = request.form.getlist('uneven_wear[]')
        other_details = request.form.getlist('other_details[]')

        # 個別データの初期化とデフォルト値設定を統一
        tread_depths = [
            int(value) if value and value.isdigit() else None for value in tread_depths
        ]
        uneven_wears = [
            int(value) if value and value.isdigit() else None for value in uneven_wears
        ]

        # デバッグ用: 修正後のリストを確認
        print(f"Processed tread_depths: {tread_depths}")
        print(f"Processed uneven_wears: {uneven_wears}")

        # デバッグ用: uneven_wears の値を確認
        print(f"uneven_wears (raw): {uneven_wears}")

        # バリデーション: 必須項目が選択されていない場合エラーを返す
        if not width or not aspect_ratio or not inch or not manufacturers:
            flash("必須項目をすべて正しく選択してください。", "danger")
            return render_template('input_page.html', form=form)

        # コピー元フォームのデータを動的リストの先頭に追加
        manufacturers.insert(0, request.form.get('manufacturer'))
        manufacturing_years.insert(0, request.form.get('manufacturing_year'))
        tread_depths.insert(0, request.form.get('tread_depth'))
        uneven_wears.insert(0, request.form.get('uneven_wear'))
        other_details.insert(0, request.form.get('other_details'))

        # データ登録
        try:
            ids = []
            for i in range(len(manufacturers)):
                new_tire = InputPage(
                    registration_date=registration_date,
                    width=width,
                    aspect_ratio=aspect_ratio,
                    inch=inch,
                    ply_rating=ply_rating,
                    manufacturer=manufacturers[i],
                    manufacturing_year=manufacturing_years[i] if i < len(manufacturing_years) else None,
                    tread_depth=tread_depths[i] if i < len(tread_depths) else None,
                    uneven_wear=uneven_wears[i] if i < len(uneven_wears) else None,
                    other_details=other_details[i] if i < len(other_details) else None,
                    is_dispatched=False
                )
                db.session.add(new_tire)
                db.session.commit()
                ids.append(new_tire.id)
            
            # 登録完了画面にリダイレクト
            return redirect(url_for('register_success', ids=','.join(map(str, ids)), width=width, aspect_ratio=aspect_ratio, inch=inch, ply_rating=ply_rating, registration_date=registration_date))
        except Exception as e:
            db.session.rollback()
            print(f"Error: {e}")
            return jsonify({'error': '登録中にエラーが発生しました！'})

    return render_template('input_page.html', form=form)


@app.route('/register_success')
def register_success():
    ids = request.args.get('ids').split(',')
    width = request.args.get('width')
    aspect_ratio = request.args.get('aspect_ratio')
    inch = request.args.get('inch')
    ply_rating = request.args.get('ply_rating')
    registration_date = request.args.get('registration_date')

    # 登録されたタイヤのデータを取得
    tires = InputPage.query.filter(InputPage.id.in_(ids)).all()

    return render_template('register_success.html', tires=tires, width=width, aspect_ratio=aspect_ratio, inch=inch, ply_rating=ply_rating, registration_date=registration_date)

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

@app.route('/dispatch/confirm', methods=['GET', 'POST'])
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

    # デバッグログ
    print(f"GET action - Tires to dispatch: {[tire.id for tire in tires_to_dispatch]} -> Count: {len(tires_to_dispatch)}")
    
    return render_template('dispatch_confirm.html', tires_to_dispatch=tires_to_dispatch)

@app.route('/dispatch', methods=['GET', 'POST'])
def dispatch():
    # デバッグログ
    print(f"Request method: {request.method}")
    print(f"Session selected tires before processing: {session.get('selected_tires')}")

    selected_tires = session.get('selected_tires', [])
    processed_tire_ids = []  # 処理済みタイヤIDのリスト
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
                    user_id=1,  # 仮のログインユーザーID（実際にはセッションなどから取得）
                    dispatch_date=date.today()
                )
                db.session.add(new_dispatch)
                processed_tire_ids.append(tire_id)
        # データベースの変更を保存
        db.session.commit()

        # セッションに保存
        session['processed_tires'] = processed_tire_ids

        flash("出庫処理が完了しました。", "success")
    except Exception as e:
        # エラー発生時はロールバック
        db.session.rollback()
        flash(f"エラーが発生しました: {e}", "danger")

    # 処理完了後、出庫履歴画面にリダイレクト
    return redirect(url_for('dispatch_page'))

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

        # 合計数と合計金額を計算
        total_tires = len(tires_to_dispatch)
        total_price = sum(tire.price for tire in tires_to_dispatch if tire and tire.price)

        # デバッグログ
        print(f"Processed tire IDs: {processed_tire_ids}")
        print(f"Tires to dispatch: {[tire.id for tire in tires_to_dispatch if tire]}")

        return render_template(
            'dispatch_page.html',
            tires_to_dispatch=tires_to_dispatch,
            total_tires=total_tires,
            total_price=total_price
        )
    except Exception as e:
        flash(f"エラーが発生しました: {e}", "danger")
        return redirect(url_for('home'))


@app.route('/generate_dispatch_pdf', methods=['POST'])
def generate_dispatch_pdf():
    try:
        # 今回の出庫タイヤを取得
        processed_tire_ids = session.get('processed_tires', [])

        if not processed_tire_ids:
            flash("出庫対象のタイヤが見つかりません。", "warning")
            return redirect(url_for('dispatch_page'))

        # 出庫履歴から対象データを取得
        dispatch_history = DispatchHistory.query.filter(DispatchHistory.tire_id.in_(processed_tire_ids)).all()

        # 出庫対象タイヤを再取得
        tires_to_dispatch = [
            InputPage.query.get(dispatch.tire_id) for dispatch in dispatch_history
        ]

        # 合計本数と金額計算
        total_tires = len(tires_to_dispatch)
        total_price = sum(tire.price for tire in tires_to_dispatch if tire and tire.price)

        # デバッグログ
        print(f"Processed tire IDs: {processed_tire_ids}")
        print(f"Tires to dispatch for PDF: {[tire.id for tire in tires_to_dispatch if tire]}")
        
        # PDF生成用HTMLテンプレートをレンダリング
        rendered_html = render_template(
            'dispatch_pdf.html', 
            tires_to_dispatch=tires_to_dispatch,
            total_tires=total_tires,
            total_price=total_price
        )

        # PDF生成
        pdf = pdfkit.from_string(rendered_html, False)

        # PDFをレスポンスとして返す
        response = Response(pdf, content_type='application/pdf')
        response.headers['Content-Disposition'] = 'inline; filename=dispatch_instructions.pdf'
        return response
    except Exception as e:
        flash(f"PDF生成中にエラーが発生しました: {e}", "danger")
        return redirect(url_for('dispatch_page'))


@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit_page(id):
    tire = InputPage.query.get_or_404(id)
    form = EditForm(obj=tire)
    if form.validate_on_submit():
        # フォームの内容でタイヤ情報を更新
        form.populate_obj(tire)
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('edit_page.html', form=form, tire=tire)

@app.route('/history')
def history_page():
    history = HistoryPage.query.all()
    return render_template('history_page.html', history=history)

@app.route('/alerts')
def alert_page():
    alerts = AlertPage.query.all()
    return render_template('alert_page.html', alerts=alerts)

@app.route('/inventory_list', methods=['GET', 'POST'])
def inventory_list():
    form = SearchForm()  # SearchForm をそのまま利用
    edit_forms = {}  # 各アイテムごとにフォームを保持
    query = InputPage.query.order_by(InputPage.id.desc())
    tires = None

    # POSTリクエスト処理
    if request.method == 'POST':
        if 'reset' in request.form:
            # 全ての条件を解除して全在庫を表示
            tires = query.all()
        elif 'filter_in_stock' in request.form:
            # 在庫があるものだけを取得
            query = query.filter(InputPage.is_dispatched == False)
            tires = query.all()
        elif 'filter_dispatched' in request.form:
            # 出庫済みのものだけを取得
            query = query.filter(InputPage.is_dispatched == True)
            tires = query.all()
        else:
            # その他の条件はフォームから取得して適用
            if form.validate_on_submit():
                if form.registration_date.data:
                    query = query.filter(InputPage.registration_date == form.registration_date.data)
                if 'filter_unpriced' in request.form:
                    query = query.filter(InputPage.price.is_(None))
            tires = query.all()
    else:
        # GETリクエスト時：デフォルトで在庫があるものだけを取得
        query = query.filter(InputPage.is_dispatched == False)
        tires = query.all()

    # 一括更新処理
    if request.method == 'POST' and 'update_all' in request.form:
        for tire in tires:
            # フィールド名にIDを含めてユニークにする
            price_key = f"price_{tire.id}"
            other_details_key = f"other_details_{tire.id}"

            # 入力データがある場合に更新
            if price_key in request.form and request.form[price_key]:
                try:
                    # 空白や無効な値を弾く
                    # 金額を整数として保存
                    tire.price = int(request.form[price_key].replace(',', '').strip())
                except ValueError:
                    # 無効な値の場合はスキップ
                    print(f"Invalid price value for tire ID {tire.id}, skipping update.")
            if other_details_key in request.form and request.form[other_details_key]:
                tire.other_details = request.form[other_details_key]

            # 編集者と日時を更新
            tire.last_edited_by = current_user.id  # Assuming `current_user` contains the logged-in user
            tire.last_edited_at = datetime.utcnow()


        # 変更をデータベースに保存
        db.session.commit()
        return redirect(url_for('inventory_list'))

    return render_template('inventory_list.html', form=form, tires=tires)

# Blueprintの登録
app.register_blueprint(admin_bp)

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


if __name__ == '__main__':
    # print(app.url_map)  # 登録済みルートを確認
    app.run(debug=True)
