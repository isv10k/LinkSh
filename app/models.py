from app import db
from passlib.hash import pbkdf2_sha256 as sha256
import hashlib

class UserModel(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    link = db.relationship('LinkModel')

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    @classmethod
    def find_by_username(cls, username):
        return cls.query.filter_by(username=username).first()

    @classmethod
    def find_id_by_username(cls, username):
        user_data = cls.query.filter_by(username=username).first()
        return user_data.id

    @classmethod
    def return_all(cls):
        def to_json(x):
            return {
                'username': x.username,
                'password': x.password
            }

        return {'users': list(map(lambda x: to_json(x), UserModel.query.all()))}

    @classmethod
    def delete_all(cls):
        try:
            num_rows_deleted = db.session.query(cls).delete()
            db.session.commit()
            return {'message': '{} row(s) deleted'.format(num_rows_deleted)}
        except:
            return {'message': 'Something went wrong'}

    @staticmethod
    def generate_hash(password):
        return sha256.hash(password)

    @staticmethod
    def verify_hash(password, hash):
        return sha256.verify(password, hash)


class RevokedTokenModel(db.Model):
    __tablename__ = 'revoked_tokens'
    id = db.Column(db.Integer, primary_key=True)
    jti = db.Column(db.String(120))

    def add(self):
        db.session.add(self)
        db.session.commit()

    @classmethod
    def is_jti_blacklisted(cls, jti):
        query = cls.query.filter_by(jti=jti).first()
        return bool(query)

class LinkModel(db.Model):
    __tablename__ = 'links'
    id = db.Column(db.Integer, primary_key=True)
    original_link = db.Column(db.String(500), nullable=False)
    short_link = db.Column(db.String(50), nullable=False)
    link_alias = db.Column(db.String(100), nullable=True)
    # 1 - public, 2 - for registred users, 3 - private
    link_type = db.Column(db.Integer)
    click_counter = db.Column(db.Integer, nullable=True)
    link_owner_id = db.Column(db.Integer, db.ForeignKey('users.id'))


    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    @staticmethod
    def shrink_link(link):
        hash_object = hashlib.md5(str.encode(link))
        shrinked_URL = hash_object.hexdigest()[:8]
        return shrinked_URL

    @classmethod
    def return_all(cls, username_id):
        def to_json(x):
            return {
                'id': x.id,
                'original_link': x.original_link,
                'short_link': x.short_link,
                'link_alias': x.link_alias,
                'link_type': x.link_type,
                'click_counter': x.click_counter
            }
        # print(username_id)
        query = LinkModel.query.filter_by(link_owner_id=username_id)\
            .join(UserModel, LinkModel.link_owner_id == UserModel.id).all()
        # print(query)
        return {'links': list(map(lambda x: to_json(x), query))}

    @classmethod
    def delete_by_id(cls, link_id, username_id):
        LinkModel.query.filter_by(id=link_id, link_owner_id=username_id).delete()
        db.session.commit()

    @classmethod
    def change_link_properties(cls, link_id, username_id, new_props):
        link_to_change = LinkModel.query.filter_by(id=link_id, link_owner_id=username_id).first()

        if 'link_alias' in new_props:
            link_to_change.link_alias = new_props['link_alias']
        if 'link_type' in new_props:
            link_to_change.link_type = new_props['link_type']
        db.session.commit()

    @classmethod
    def change_count(cls, link_id):
        link_to_change = LinkModel.query.filter_by(id=link_id).first()
        if link_to_change.click_counter:
            link_to_change.click_counter += 1
        else:
            link_to_change.click_counter = 1
        db.session.commit()

    @classmethod
    def find_link(cls, short_url):
        link_data = LinkModel.query.filter_by(link_alias=short_url).first()
        if not link_data:
            link_data = LinkModel.query.filter_by(short_link=short_url).first()

        return link_data.id, link_data.original_link, link_data.link_type

    @classmethod
    def check_if_owner(cls, link_id, user_id):
        query = LinkModel.query.filter_by(id=link_id, link_owner_id=user_id).first()
        if query:
            return True
        else:
            return False

class UnregisteredLinkModel(db.Model):
    __tablename__ = 'unregistered_links'
    id = db.Column(db.Integer, primary_key=True)
    original_link = db.Column(db.String(500), nullable=False)
    short_link = db.Column(db.String(50), nullable=False)


    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    @staticmethod
    def shrink_link(link):
        hash_object = hashlib.md5(str.encode(link))
        shrinked_URL = hash_object.hexdigest()[:8]
        return shrinked_URL

    @classmethod
    def find_by_short_link(cls, link):
        return cls.query.filter_by(short_link=link).first()

