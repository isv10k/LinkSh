from flask_restful import Resource, reqparse
from flask import redirect
from app.models import UnregisteredLinkModel, LinkModel, UserModel

parser = reqparse.RequestParser()
parser.add_argument('username')
parser.add_argument('password')


def url_check(url):
    if url[:4] != 'http':
        url = 'http://' + url
    return url


class Redirect(Resource):

    def get(self, short_url):

        # Проверка ссылок незарегистрировнных пользователей
        try:
            link_data = UnregisteredLinkModel.find_by_short_link(short_url)
        except:
            pass
        else:
            if link_data:
                url = link_data.original_link
                url = url_check(url)
                return redirect(url)

        # Проверка ссылок зарегистрированных пользователей
        try:
            id, url, link_type = LinkModel.find_link(short_url)
        except AttributeError as e:
            return {'message': 'Unknown url', 'text': '{}'.format(e)}, 404

        if link_type == 1:
            LinkModel.change_count(id)
            url = url_check(url)
            return redirect(url)

        data = parser.parse_args()
        if not data['username']:
            return {'message': 'Missing username parameter'}, 400
        if not data['password']:
            return {'message': 'Missing password parameter'}, 400

        current_user = UserModel.find_by_username(data['username'])

        if not current_user:
            return {'message': 'User {} doesn\'t exist'.format(data['username'])}

        if UserModel.verify_hash(data['password'], current_user.password):
            if link_type == 2:
                LinkModel.change_count(id)
                url = url_check(url)
                return redirect(url)
            elif link_type == 3:
                user_id = UserModel.find_id_by_username(data['username'])
                if LinkModel.check_if_owner(id, user_id):
                    LinkModel.change_count(id)
                    url = url_check(url)
                    return redirect(url)
        else:
            return {'message': 'Wrong credentials'}