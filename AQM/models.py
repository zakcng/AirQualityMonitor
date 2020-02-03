from AQM import login_manager, app
from flask_login import UserMixin
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
import dbm


class User(UserMixin):
    def __init__(self, account_id, user_type, username, password, email, active=True):
        self.account_id = account_id
        self.user_type = user_type
        self.username = username
        self.password = password
        self.email = email
        self.active = active

    def is_active(self):
        return self.active

    def is_anonymous(self):
        return False

    def is_authenticated(self):
        return True

    def get_id(self):
        return self.account_id

    def get_user_type(self):
        return self.user_type

    def get_reset_token(self, expires=3600):
        s = Serializer(app.config['SECRET_KEY'], expires)

        return s.dumps({'account_id': self.account_id}).decode('utf-8')

    @staticmethod
    def verify_reset_token(token):
        s = Serializer(app.config['SECRET_KEY'])

        user_id = s.loads(token)['account_id']

        return user_id
