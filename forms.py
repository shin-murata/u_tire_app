# forms.py
from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, FloatField, SelectField, DateField, SubmitField
from wtforms.validators import DataRequired, Optional  # Optional をインポート
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
    manufacturer = SelectField('メーカー', coerce=int, validators=[DataRequired()])
    ply_rating = SelectField('プライ', coerce=int, validators=[DataRequired()])
    price = FloatField('価格', validators=[Optional()])  # Optionalに変更

    # プルダウンメニュー用フィールド
    manufacturing_year = SelectField(
        '製造年',
        coerce=int,
        validators=[DataRequired()],
        choices=[(year, f"{year}年") for year in range(2022, 2026)]  # 2022年〜2025年
    )
    tread_depth = SelectField(
        '残り溝',
        coerce=int,
        validators=[DataRequired()],
        choices=[(depth, f"{depth} 分山") for depth in reversed(range(3, 11))]  # 10分山〜3分山
    )
    uneven_wear = SelectField(
        '片減り',
        coerce=int,
        validators=[Optional()],
        choices=[(wear, f"{wear}段階") for wear in range(0, 3)]  # 0〜3段階
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # データベースからの動的な選択肢の設定
        # 'name'ではなく、'value'を使用
        self.width.choices = [(0, '選択してください')] + [(w.id, w.value) for w in Width.query.all()]  # 'name' ではなく 'value' に修正
        self.aspect_ratio.choices = [(0, '選択してください')] + [(ar.id, ar.value) for ar in AspectRatio.query.all()]  # 'name' ではなく 'value' に修正
        self.inch.choices = [(0, '選択してください')] + [(i.id, i.value) for i in Inch.query.all()]  # 'name' ではなく 'value' に修正
        self.manufacturer.choices = [(0, '選択してください')] + [(m.id, m.name) for m in Manufacturer.query.all()]  # 'name' は正しい
        self.ply_rating.choices = [(0, '選択してください')] + [(p.id, p.value) for p in PlyRating.query.all()]  # 'name' ではなく 'value' に修正

class SearchForm(FlaskForm):
    width = SelectField('Width', coerce=int, validators=[Optional()])
    aspect_ratio = SelectField('Aspect Ratio', coerce=int, validators=[Optional()])
    inch = SelectField('Inch', coerce=int, validators=[Optional()])
    ply_rating = SelectField('Ply Rating', coerce=int, validators=[Optional()])  # ply_rating フィールド
    registration_date = DateField('登録日', format='%Y-%m-%d', validators=[Optional()])  # 日付フィールド追加
    submit = SubmitField('検索')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # データベースから動的に選択肢を設定
        self.width.choices = [(0, '選択してください')] + [(w.id, w.value) for w in Width.query.all()]
        self.aspect_ratio.choices = [(0, '選択してください')] + [(ar.id, ar.value) for ar in AspectRatio.query.all()]
        self.inch.choices = [(0, '選択してください')] + [(i.id, i.value) for i in Inch.query.all()]
        self.ply_rating.choices = [(0, '選択してください')] + [(p.id, p.value) for p in PlyRating.query.all()]
class EditForm(CombinedForm):
    price = FloatField('価格', validators=[Optional()])
    other_details = StringField('その他', validators=[Optional()])
    submit = SubmitField('登録')
    pass
