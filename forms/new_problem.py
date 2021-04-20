from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField
from wtforms import BooleanField, SubmitField
from wtforms.validators import DataRequired


class NewsForm(FlaskForm):
    title = StringField('Идея', validators=[DataRequired()])
    content = TextAreaField("Раскрыть идею")
    is_private = BooleanField("Личное")
    submit = SubmitField('Применить')