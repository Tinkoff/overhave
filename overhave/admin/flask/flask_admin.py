from flask_admin import Admin
from flask_admin.menu import MenuLink

from overhave.admin.views.index.view import OverhaveIndexView


def get_flask_admin(index_view: OverhaveIndexView) -> Admin:
    admin = Admin(name='Overhave', template_mode='bootstrap3', index_view=index_view,)
    admin.add_link(MenuLink(name='Log out', url='/logout'))
    return admin
