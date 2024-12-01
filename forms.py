from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, FloatField, SelectField, DateField
from wtforms.validators import DataRequired

class InputForm(FlaskForm):
    registration_date = DateField('Registration Date', validators=[DataRequired()])
    width = SelectField('Width', coerce=int, choices=[(1, '195'), (2, '205')], validators=[DataRequired()])
    aspect_ratio = SelectField('Aspect Ratio', coerce=int, choices=[(1, '50'), (2, '60')], validators=[DataRequired()])
    inch = SelectField('Inch', coerce=int, choices=[(1, '15'), (2, '16')], validators=[DataRequired()])
    other_details = StringField('Other Details')
    manufacturing_year = IntegerField('Manufacturing Year')
    manufacturer = SelectField('Manufacturer', coerce=int, choices=[(1, 'Michelin'), (2, 'Bridgestone')], validators=[DataRequired()])
    tread_depth = IntegerField('Tread Depth', validators=[DataRequired()])
    uneven_wear = IntegerField('Uneven Wear')
    ply_rating = SelectField('Ply Rating', coerce=int, choices=[(1, '8PR'), (2, '10PR')], validators=[DataRequired()])
    price = FloatField('Price', validators=[DataRequired()])

class SearchForm(FlaskForm):
    width = SelectField('Width', coerce=int, choices=[(1, '195'), (2, '205')], validators=[DataRequired()])
    aspect_ratio = SelectField('Aspect Ratio', coerce=int, choices=[(1, '50'), (2, '60')], validators=[DataRequired()])
    inch = SelectField('Inch', coerce=int, choices=[(1, '15'), (2, '16')], validators=[DataRequired()])

class EditForm(InputForm):
    pass
