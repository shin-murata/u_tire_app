from flask import Flask, render_template, request, redirect, url_for,  jsonify, flash
from flask_migrate import Migrate  # Flask-Migrate をインポート
from models import db, Width, AspectRatio, Inch, Manufacturer, PlyRating, InputPage, SearchPage, EditPage, HistoryPage, DispatchHistory, AlertPage, User
from forms import InputForm, SearchForm, EditForm
from datetime import date

app = Flask(__name__)
app.config.from_object('config.Config')

# データベースを初期化
db.init_app(app)

# Flask-Migrate を初期化
migrate = Migrate(app, db)

# アプリケーションのルート設定
@app.route('/')
def index():
    return render_template('base.html')

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
    form = InputForm()

    if request.method == 'GET':
        # フォームを表示
        return render_template('input_page.html', form=form)

    elif request.method == 'POST':
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
        other_details = request.form.getlist('other_details[]')

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
    tires = None  # 結果を保持する変数
    if form.validate_on_submit():
        # ply_rating をフォームデータから取得
        ply_rating = form.ply_rating.data

        # 基本的な検索条件をクエリとして初期化
        query = InputPage.query.filter_by(
            width=form.width.data,
            aspect_ratio=form.aspect_ratio.data,
            inch=form.inch.data
        )

        # ply_rating が指定されている場合は追加条件を設定
        if ply_rating and ply_rating != 0:  # 0 は「選択してください」に対応
            query = query.filter(InputPage.ply_rating == ply_rating)

        # 出庫済みではない条件を追加
        query = query.filter(InputPage.is_dispatched == False)

        # クエリを実行して結果を取得
        tires = query.all()

    return render_template('search_page.html', form=form, tires=tires)

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

@app.route('/dispatch', methods=['GET', 'POST'])
def dispatch():
    if request.method == 'GET':
        # 出庫履歴を表示
        dispatch_history = DispatchHistory.query.all()
        return render_template('dispatch_page.html', dispatch_history=dispatch_history)

    elif request.method == 'POST':
        # POSTデータで送信されたチェックされたタイヤIDリストを取得
        selected_tires = request.form.getlist('tire_ids')  # 選択されたタイヤIDリスト
        user_id = 1  # 固定値でログインユーザーIDを仮定（実際にはログインセッションから取得）

        if not selected_tires:
            flash("出庫するタイヤを選択してください。", "warning")
            return redirect(url_for('search_page'))

        # 選択されたタイヤを処理
        for tire_id in selected_tires:
            tire = InputPage.query.get(tire_id)
            if tire and not tire.is_dispatched:  # 未出庫のタイヤのみ処理
                tire.is_dispatched = 1  # 出庫フラグを1に更新
                # 出庫履歴を記録
                new_dispatch = DispatchHistory(
                    tire_id=tire_id,
                    user_id=user_id,
                    dispatch_date=date.today(),
                    dispatch_note="販売による出庫"
                )
                db.session.add(new_dispatch)

        # データベースを更新
        db.session.commit()
        flash("出庫処理が完了しました。", "success")
        return redirect(url_for('dispatch'))
    
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

    # リセットボタンの処理
    if request.method == 'POST' and 'reset' in request.form:
        # 全ての条件を解除して初期状態を表示
        tires = query.all()
    elif form.validate_on_submit():
        # 登録日でのみフィルタリング
        if form.registration_date.data:
            query = query.filter(InputPage.registration_date == form.registration_date.data)
        # 結果を取得
        tires = query.all()
    else:
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
                    tire.price = float(request.form[price_key])
                except ValueError:
                    # 無効な値の場合はスキップ
                    print(f"Invalid price value for tire ID {tire.id}, skipping update.")
            if other_details_key in request.form and request.form[other_details_key]:
                tire.other_details = request.form[other_details_key]

        # 変更をデータベースに保存
        db.session.commit()
        return redirect(url_for('inventory_list'))

    return render_template('inventory_list.html', form=form, tires=tires)

if __name__ == '__main__':
    app.run(debug=True)
