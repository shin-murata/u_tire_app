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

        # データ登録
        try:
            if not manufacturers: # 動的フォームがない場合（単一登録）
                manufacturer = request.form.get('manufacturer')  # 固定フォームから取得
                manufacturing_year = request.form.get('manufacturing_year')
                tread_depth = request.form.get('tread_depth')
                uneven_wear = request.form.get('uneven_wear')
                other_details = request.form.get('other_details')
                
                new_tire = InputPage(
                    registration_date=registration_date,
                    width=width,
                    aspect_ratio=aspect_ratio,
                    inch=inch,
                    ply_rating=ply_rating,
                    manufacturer=manufacturer,
                    manufacturing_year=manufacturing_year,
                    tread_depth=tread_depth,
                    uneven_wear=uneven_wear,
                    other_details=other_details,
                    is_dispatched=False  # 新規登録時は未出庫
                )
                db.session.add(new_tire)
            else:
                # 複数登録
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
            return jsonify({'message': '登録が完了しました！'})
        except Exception as e:
            db.session.rollback()
            print(f"Error: {e}")
            return jsonify({'error': '登録中にエラーが発生しました！'})

    return render_template('input_page.html', form=form)

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

@app.route('/inventory_list')
def inventory_list():
    tires = InputPage.query.all()  # すべてのタイヤ情報を取得
    return render_template('inventory_list.html', tires=tires)

if __name__ == '__main__':
    app.run(debug=True)
