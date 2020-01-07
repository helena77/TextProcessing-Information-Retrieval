from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, validators, SelectField

class ReviewSearchForm(FlaskForm):
	keywords = StringField('Review Keywords', validators=[validators.DataRequired()])
	submit = SubmitField('Submit')
