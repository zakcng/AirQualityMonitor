from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import *


class RegisterNode(FlaskForm):
    nodeName = StringField('Node name:', validators=[DataRequired()])
    nodeLocation = StringField('Location:', validators=[DataRequired()])
    nodeAdd = SubmitField('Add Node')
