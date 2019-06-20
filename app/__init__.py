from flask import Flask

from flask_restful import Api

from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)

api = Api(app)
db = SQLAlchemy(app)

from app import views, resources

# Endpoints
api.add_resource(resources.UserRegistration, '/registration')
api.add_resource(resources.UserLogin, '/login')
api.add_resource(resources.UserLogoutAccess, '/logout/access')
api.add_resource(resources.UserLogoutRefresh, '/logout/refresh')
api.add_resource(resources.TokenRefresh, '/token/refresh')
api.add_resource(resources.AllUsers, '/users')
api.add_resource(resources.SecretResource, '/secret')

# DB
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'pass'



@app.before_first_request
def create_tables():
    db.create_all()