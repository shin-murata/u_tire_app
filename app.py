from flask import Flask, render_template, request, redirect, url_for
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

@app.route('/input', methods=['GET', 'POST'])
def input_page():
    form = InputForm()
    if form.validate_on_submit():
        # 新しいタイヤ情報をデータベースに追加
        new_tire = InputPage(
            registration_date=form.registration_date.data,
            width=form.width.data,
            aspect_ratio=form.aspect_ratio.data,
            inch=form.inch.data,
            other_details=form.other_details.data,
            manufacturing_year=form.manufacturing_year.data,
            manufacturer=form.manufacturer.data,
            tread_depth=form.tread_depth.data,
            uneven_wear=form.uneven_wear.data,
            ply_rating=form.ply_rating.data,
            price=form.price.data,
            is_dispatched=0  # 出庫フラグを明示的に0で設定
        )
        db.session.add(new_tire)
        db.session.commit()
        return redirect(url_for('index'))
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
