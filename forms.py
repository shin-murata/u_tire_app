# forms.py
from flask_wtf import FlaskForm
from flask import current_app as app  # ✅ 修正: `current_app` を使う
from wtforms import StringField, IntegerField, FloatField, SelectField, DateField, SubmitField
from wtforms.validators import DataRequired, Optional, InputRequired  # Optional をインポート
from models import Width, AspectRatio, Inch, Manufacturer, PlyRating
from datetime import date
from wtforms.widgets import Input

class RangeInput(Input):
    input_type = 'range'

    def __call__(self, field, **kwargs):
        # デフォルト値を設定
        if 'value' not in kwargs:
            kwargs['value'] = field.data or 0
        # フィールドのrender_kw属性からスライダー設定を適用
        kwargs.update(field.render_kw or {})
        return super().__call__(field, **kwargs)
    @property
    def validation_attrs(self):
        # 必要ならここで追加の属性を定義可能
        return {}
    
class CombinedForm(FlaskForm):
    registration_date = DateField(
        'Registration Date',
        validators=[Optional()],  # データ必須ではなく、オプショナルに
        default=date.today  # lambdaを使わず、直接関数を指定
    )
    
    width = SelectField('幅', coerce=int, validators=[DataRequired()])
    aspect_ratio = SelectField('扁平率', coerce=int, validators=[DataRequired()])
    inch = SelectField('インチ', coerce=int, validators=[DataRequired()])
    other_details = StringField('その他')
    manufacturer = SelectField(
        'メーカー', 
        coerce=int, 
        validators=[DataRequired()]
        )
    ply_rating = SelectField('プライ', coerce=int, validators=[DataRequired()])
    price = FloatField('価格', validators=[Optional()])  # Optionalに変更

    # プルダウンメニュー用フィールド
    manufacturing_year = SelectField(
        '製造年',
        coerce=int,
        validators=[DataRequired()],
        default=0,  # 明示的に初期値を指定
        choices=[(0, "製造年")] + [(year, f"{year}年") for year in range(2022, 2026)]  # 2022年〜2025年
    )
    tread_depth = SelectField(
        '残り溝',
        coerce=int,
        validators=[DataRequired()],
        default=0,  # 明示的に初期値を指定
        choices=[(0, "残り溝")] + [(depth, f"{depth} 分山") for depth in reversed(range(3, 11))]  # 10分山〜3分山
    )
    uneven_wear = SelectField(
        '片減り',
        coerce=int,
        validators=[DataRequired()],
        default=-1,  # 明示的に初期値を指定
        choices=[(-1, "片減り")] + [(wear, f"{wear}段階") for wear in range(0, 4)]  # 0〜3段階
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # データベースからの動的な選択肢の設定
        # 'name'ではなく、'value'を使用
        self.width.choices = [(0, f"{self.width.label.text}")] + [(w.id, w.value) for w in Width.query.all()]  # 'name' ではなく 'value' に修正
        self.width.default = 0  # 初期値を指定
        self.aspect_ratio.choices = [(0, f"{self.aspect_ratio.label.text}")] + [(ar.id, ar.value) for ar in AspectRatio.query.all()]  # 'name' ではなく 'value' に修正
        self.aspect_ratio.default = 0  # 初期値を指定
        self.inch.choices = [(0, f"{self.inch.label.text}")] + [(i.id, i.value) for i in Inch.query.all()]  # 'name' ではなく 'value' に修正
        self.inch.default = 0  # 初期値を指定
        self.manufacturer.choices = [(0,f"{self.manufacturer.label.text}")] + [(m.id, m.name) for m in Manufacturer.query.all()]  # 'name' は正しい
        self.manufacturer.default = 0  # 初期値を指定
        print(self.manufacturer.choices)
        self.ply_rating.choices = [(0, f"{self.ply_rating.label.text}")] + [(p.id, p.value) for p in PlyRating.query.all()]  # 'name' ではなく 'value' に修正
        self.ply_rating.default = 0  # 初期値を指定

class SearchForm(FlaskForm):
    width = SelectField('幅', coerce=int, validators=[Optional()])
    aspect_ratio = SelectField('扁平率', coerce=int, validators=[Optional()])
    inch = SelectField('インチ', coerce=int, validators=[Optional()])
    ply_rating = SelectField('プライ', coerce=int, validators=[Optional()])  # ply_rating フィールド
    registration_date = DateField('登録日', format='%Y-%m-%d', validators=[Optional()])  # 日付フィールド追加
    submit = SubmitField('検索')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # データベースから動的に選択肢を設定
        self.width.choices = [(0, f"{self.width.label.text}")] + [(w.id, w.value) for w in Width.query.all()]
        self.width.default = 0  # 初期値を指定
        self.aspect_ratio.choices = [(0, f"{self.aspect_ratio.label.text}")] + [(ar.id, ar.value) for ar in AspectRatio.query.all()]
        self.aspect_ratio.default = 0  # 初期値を指定
        self.inch.choices = [(0, f"{self.inch.label.text}")] + [(i.id, i.value) for i in Inch.query.all()]
        self.inch.default = 0  # 初期値を指定
        self.ply_rating.choices = [(0, f"{self.ply_rating.label.text}")] + [(p.id, p.value) for p in PlyRating.query.all()]
        self.ply_rating.default = 0  # 初期値を指定

class EditForm(CombinedForm):
    price = FloatField(
        '価格', 
        validators=[Optional()],  # 必須ではないことを明示
        default=0.0  # 初期値を明示的に設定
    )
    other_details = StringField('その他', validators=[Optional()])
    submit = SubmitField('登録')
    pass

# 共通のフォーム
class EditForm(FlaskForm):
    id = IntegerField('ID')  # 編集対象のID（編集対象を識別）
    width = SelectField('幅', coerce=int, validators=[DataRequired()])
    aspect_ratio = SelectField('扁平率', coerce=int, validators=[DataRequired()])
    inch = SelectField('インチ', coerce=int, validators=[DataRequired()])
    ply_rating = SelectField(
        'プライ',
        coerce=int,
        validators=[InputRequired()],  # DataRequired() → InputRequired() に変更
        choices=[]
    )
    manufacturer = SelectField('メーカー', coerce=int, validators=[DataRequired()])
    manufacturing_year = SelectField(
        '製造年',
        coerce=int,
        validators=[DataRequired()],
        choices=[(0, "製造年")] + [(year, f"{year}年") for year in range(2022, 2026)]
    )
    tread_depth = SelectField(
        '残り溝',
        coerce=int,
        validators=[DataRequired()],
        choices=[(0, "残り溝")] + [(depth, f"{depth} 分山") for depth in reversed(range(3, 11))]
    )
    uneven_wear = SelectField(
        '片減り',
        coerce=int,
        validators=[InputRequired()],  # ✅ `InputRequired()` に変更
        choices=[(-1, "片減り")] + [(wear, f"{wear}段階") for wear in range(0, 4)]
    )
    other_details = StringField('その他', validators=[Optional()])
    price = FloatField('価格', validators=[Optional()])
    value = StringField('Value', validators=[Optional()])  # ✅ Optional に変更してエラーを防ぐ
    submit = SubmitField('更新')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        with app.app_context():
                    self.width.choices = [(0, "幅を選択")] + [(w.id, w.value) for w in Width.query.all()]
                    self.aspect_ratio.choices = [(0, "扁平率を選択")] + [(ar.id, ar.value) for ar in AspectRatio.query.all()]
                    self.inch.choices = [(0, "インチを選択")] + [(i.id, i.value) for i in Inch.query.all()]
                    self.manufacturer.choices = [(0, "メーカーを選択")] + [(m.id, m.name) for m in Manufacturer.query.all()]
                    self.ply_rating.choices = [(0, "プライを選択")] + [(p.id, p.value) for p in PlyRating.query.all()]
                    if self.ply_rating.data is None:
                        self.ply_rating.data = 0  # ✅ 初期値を 0 にセット
                    self.uneven_wear.choices = [(-1, "片減り")] + [(wear, f"{wear}段階") for wear in range(0, 4)]
                    if self.uneven_wear.data is None:
                        self.uneven_wear.data = 0  # ✅ 初期値を0にセット