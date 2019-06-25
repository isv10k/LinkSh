from flask_restful import Resource, reqparse
from app.models import UnregisteredLinkModel, LinkModel, UserModel

parser = reqparse.RequestParser()
parser.add_argument('link')  #, help = 'This field cannot be blank', required = True)
parser.add_argument('link_alias')  # , help = 'This field cannot be blank', required = True)
parser.add_argument('link_type')

from flask_jwt_extended import (create_access_token, create_refresh_token,
                                jwt_required, jwt_refresh_token_required,
                                get_jwt_identity, get_raw_jwt, jwt_optional)

class Links(Resource):
    @jwt_optional
    def post(self):
        data = parser.parse_args()
        current_user = get_jwt_identity()
        if current_user:
            # ToDo: if link exists
            short_url = LinkModel.shrink_link(data['link'])
            link_name = None
            if data['link_alias']:
                link_name = data['link_alias']

            new_link = LinkModel(
                original_link=data['link'],
                short_link=short_url,
                link_alias=link_name,
                link_type=data['link_type'],
                link_owner_id=UserModel.find_id_by_username(current_user)
            )
            try:
                new_link.save_to_db()
            except Exception as e:
                return {'message': 'Something went wrong', 'text': '{}'.format(e)}, 500
            else:
                return {'Your link': '{}'.format(short_url),
                        'Link alias': '{}'.format(link_name)}
        else:
            short_url = LinkModel.shrink_link(data['link'])
            # ToDo: change
            if UnregisteredLinkModel.find_by_short_link(short_url):
                return {'message': 'Link {} already exists'.format(data['link'])}
            new_link = UnregisteredLinkModel(
                original_link=data['link'],
                short_link=short_url,
            )
            try:
                new_link.save_to_db()
            except Exception as e:
                return {'message': 'Something went wrong', 'text': f'{e}'}, 500
            else:
                return {'Your link': '{}'.format(short_url)}, 200

    @jwt_required
    def get(self):
        current_user = get_jwt_identity()
        user_id = UserModel.find_id_by_username(current_user)
        return LinkModel.return_all(user_id)

    @jwt_required
    def delete(self, link_id):
        current_user = get_jwt_identity()
        user_id = UserModel.find_id_by_username(current_user)
        LinkModel.delete_by_id(link_id, user_id)

    @jwt_required
    def patch(self, link_id):
        data = parser.parse_args()

        props_to_change = {}
        if 'link_alias' in data:
            props_to_change['link_alias'] = data['link_alias']
        if 'link_type' in data:
            props_to_change['link_type'] = data['link_type']


        current_user = get_jwt_identity()
        user_id = UserModel.find_id_by_username(current_user)

        try:
            LinkModel.change_link_properties(link_id, user_id, props_to_change)
        except Exception as e:
            return {'message': 'Something went wrong', 'text': '{}'.format(e)}, 500








