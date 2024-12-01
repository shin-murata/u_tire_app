# forms.py
from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, FloatField, SelectField, DateField
from wtforms.validators import DataRequired, Optional  # Optional をインポート
from models import Width, AspectRatio, Inch, Manufacturer, PlyRating
from datetime import date
class InputForm(FlaskForm):
    registration_date = DateField(
        'Registration Date',
        validators=[Optional()],  # データ必須ではなく、オプショナルに
        default=date.today  # lambdaを使わず、直接関数を指定
    )
    
    width = SelectField('Width', coerce=int, validators=[DataRequired()])
    aspect_ratio = SelectField('Aspect Ratio', coerce=int, validators=[DataRequired()])
    inch = SelectField('Inch', coerce=int, validators=[DataRequired()])
    other_details = StringField('Other Details')
    manufacturing_year = IntegerField('Manufacturing Year')
    manufacturer = SelectField('Manufacturer', coerce=int, validators=[DataRequired()])
    tread_depth = IntegerField('Tread Depth', validators=[DataRequired()])
    uneven_wear = IntegerField('Uneven Wear')
    ply_rating = SelectField('Ply Rating', coerce=int, validators=[DataRequired()])
    price = FloatField('Price', validators=[DataRequired()])

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # データベースからの動的な選択肢の設定
        # 'name'ではなく、'value'を使用
        self.width.choices = [(w.id, w.value) for w in Width.query.all()]  # 'name' ではなく 'value' に修正
        self.aspect_ratio.choices = [(ar.id, ar.value) for ar in AspectRatio.query.all()]  # 'name' ではなく 'value' に修正
        self.inch.choices = [(i.id, i.value) for i in Inch.query.all()]  # 'name' ではなく 'value' に修正
        self.manufacturer.choices = [(m.id, m.name) for m in Manufacturer.query.all()]  # 'name' は正しい
        self.ply_rating.choices = [(p.id, p.value) for p in PlyRating.query.all()]  # 'name' ではなく 'value' に修正

class SearchForm(FlaskForm):
    width = SelectField('Width', coerce=int, choices=[(1, '195'), (2, '205')], validators=[DataRequired()])
    aspect_ratio = SelectField('Aspect Ratio', coerce=int, choices=[(1, '50'), (2, '60')], validators=[DataRequired()])
    inch = SelectField('Inch', coerce=int, choices=[(1, '15'), (2, '16')], validators=[DataRequired()])

class EditForm(InputForm):
    pass
