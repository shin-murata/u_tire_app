from flask import Flask, render_template, request, redirect, url_for,  jsonify
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
    tires = None
    if form.validate_on_submit():
        # 検索条件に基づいてタイヤ情報を取得
        tires = InputPage.query.filter_by(
            width=form.width.data,
            aspect_ratio=form.aspect_ratio.data,
            inch=form.inch.data
        ).all()
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
        # 出庫処理
        selected_tires = request.form.getlist('tire_ids')  # 選択されたタイヤIDリスト
        user_id = 1  # 固定値でログインユーザーIDを仮定（実際にはログインセッションから取得）

        for tire_id in selected_tires:
            tire = InputPage.query.get(tire_id)
            if tire:
                tire.is_dispatched = 1  # 出庫フラグを1に更新
                # 出庫履歴を記録
                new_dispatch = DispatchHistory(
                    tire_id=tire_id,
                    user_id=user_id,
                    dispatch_date=date.today(),
                    dispatch_note="販売による出庫"
                )
                db.session.add(new_dispatch)

        db.session.commit()  # 一括でコミット

        return redirect(url_for('search_page'))  # 在庫検索画面に戻る


@app.route('/alerts')
def alert_page():
    alerts = AlertPage.query.all()
    return render_template('alert_page.html', alerts=alerts)

@app.route('/inventory_list', methods=['GET', 'POST'])
def inventory_list():
    query = InputPage.query.order_by(InputPage.id.desc())

    # フィルターデータの準備（リレーション値を取得）
    filters = {
        'registration_date': [
            row[0].strftime('%Y-%m-%d') for row in db.session.query(InputPage.registration_date).distinct() if row[0]
        ],
        'width': [{'id': row.id, 'value': row.value} for row in db.session.query(Width).distinct()],
        'aspect_ratio': [{'id': row.id, 'value': row.value} for row in db.session.query(AspectRatio).distinct()],
        'inch': [{'id': row.id, 'value': row.value} for row in db.session.query(Inch).distinct()],
        'manufacturer': [{'id': row.id, 'name': row.name} for row in db.session.query(Manufacturer).distinct()],
        'ply_rating': [{'id': row.id, 'value': row.value} for row in db.session.query(PlyRating).distinct()],
        'other_details': [{'id': row[0], 'value': row[0]} for row in db.session.query(InputPage.other_details).distinct() if row[0]],
        'manufacturing_year': [{'id': row[0], 'value': row[0]} for row in db.session.query(InputPage.manufacturing_year).distinct() if row[0]],
        'tread_depth': [{'id': row[0], 'value': row[0]} for row in db.session.query(InputPage.tread_depth).distinct() if row[0]],
        'uneven_wear': [{'id': row[0], 'value': row[0]} for row in db.session.query(InputPage.uneven_wear).distinct() if row[0]],
        'price': [{'id': row[0], 'value': row[0]} for row in db.session.query(InputPage.price).distinct() if row[0]],
        'is_dispatched': [{'id': row[0], 'value': row[0]} for row in db.session.query(InputPage.is_dispatched).distinct()],
    }

    selected_column = None
    selected_value = None

    if request.method == 'POST':
        action = request.form.get('action')
        selected_column = request.form.get('filter_column')
        selected_value = request.form.get('filter_value')

        if action == 'filter' and selected_column:
            if selected_value == "":
                print("Selected value is empty, skipping filter.")
            elif selected_value == "NULL":  # 値が空欄の場合
                query = query.filter(getattr(InputPage, selected_column) == None)
            else:
                try:
                    if selected_column == 'registration_date':
                        selected_value = datetime.strptime(selected_value, '%Y-%m-%d').date()
                    elif selected_column in ['price', 'tread_depth', 'uneven_wear']:
                        selected_value = float(selected_value) if '.' in selected_value else int(selected_value)
                    elif selected_column in ['manufacturer', 'inch', 'width', 'aspect_ratio', 'ply_rating']:
                        selected_value = int(selected_value)
                    query = query.filter(getattr(InputPage, selected_column) == selected_value)

                except ValueError as e:
                    print(f"Error converting value for column {selected_column}: {e}")
                    query = InputPage.query.order_by(InputPage.id.desc())

    # クエリ結果を取得
    tires = query.all()

    # デバッグ用出力
    print("Filters:", filters)
    print("Selected Column:", selected_column)
    print("Selected Value:", selected_value)

    return render_template(
        'inventory_list.html',
        tires=tires,
        filters=filters,
        selected_column=selected_column,
        selected_value=selected_value,
    )



# リレーション値を取得するヘルパー関数
def lookup_name(column, id):
    if column == 'width':
        return db.session.query(Width).filter_by(id=id).first().value
    elif column == 'aspect_ratio':
        return db.session.query(AspectRatio).filter_by(id=id).first().value
    elif column == 'inch':
        return db.session.query(Inch).filter_by(id=id).first().value
    elif column == 'manufacturer':
        return db.session.query(Manufacturer).filter_by(id=id).first().name
    elif column == 'ply_rating':
        return db.session.query(PlyRating).filter_by(id=id).first().value
    return id


if __name__ == '__main__':
    app.run(debug=True)
