from flask_admin import Admin
from flask_admin.menu import MenuLink

from overhave import db
from overhave.admin.views import (
    DraftView,
    EmulationRunView,
    EmulationView,
    FeatureView,
    GroupView,
    OverhaveIndexView,
    TagsView,
    TestRunView,
    TestUserView,
    UserView,
)
from overhave.factory import IAdminFactory


def get_flask_admin(factory: IAdminFactory) -> Admin:
    index_view = OverhaveIndexView(
        name="Info",
        url="/",
        auth_manager=factory.auth_manager,
        index_template_path=factory.context.admin_settings.index_template_path,
    )
    admin = Admin(name="Overhave", template_mode="bootstrap3", index_view=index_view)
    admin.add_link(MenuLink(name="Log out", url="/logout"))
    views_list = [
        FeatureView(db.Feature, db.current_session, category="Scenarios", name="Features"),
        TestRunView(db.TestRun, db.current_session, category="Scenarios", name="Test runs"),
        DraftView(db.Draft, db.current_session, category="Scenarios", name="Versions"),
        TagsView(db.Tags, db.current_session, category="Scenarios", name="Tags"),
        TestUserView(db.TestUser, db.current_session, name="Test users"),
        EmulationView(db.Emulation, db.current_session, category="Emulation", name="Templates"),
        EmulationRunView(db.EmulationRun, db.current_session, category="Emulation", name="Emulation runs"),
        UserView(db.UserRole, db.current_session, category="Access", name="Users"),
        GroupView(db.GroupRole, db.current_session, category="Access", name="Groups"),
    ]
    if factory.context.admin_settings.custom_views is not None:
        views_list.extend(factory.context.admin_settings.custom_views)
    admin.add_views(*views_list)
    return admin
