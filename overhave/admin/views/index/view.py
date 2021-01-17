import logging
import typing
from typing import Any

import flask
import ldap
from flask_admin import AdminIndexView, expose
from flask_login import login_required, login_user, logout_user
from sqlalchemy.exc import OperationalError, ProgrammingError
from werkzeug.wrappers import Response
from wtforms.validators import ValidationError

from overhave.admin.views.index.custom_page import CustomPageForm
from overhave.admin.views.index.login_form import LoginForm
from overhave.entities.authorization.manager import IAdminAuthorizationManager
from overhave.factory import OverhaveContext

logger = logging.getLogger(__name__)


class OverhaveIndexView(AdminIndexView):
    """ View for index. """

    def __init__(self, name: str, url: str, context: OverhaveContext, auth_manager: IAdminAuthorizationManager) -> None:
        super().__init__(
            name=name, url=url,
        )
        self._context = context
        self._auth_manager = auth_manager

    @expose('/login', methods=['GET', 'POST'])
    def login(self) -> Any:  # noqa: C901
        form = LoginForm(auth_manager=self._auth_manager)
        if not form.validate_on_submit():
            return self.render('login.html', form=form)
        try:
            user = form.get_user()
            login_user(user)
        except ValidationError:
            return form.flash_and_redirect('Incorrect username/password pair!')
        except ldap.SERVER_DOWN:
            return form.flash_and_redirect('LDAP authorization service is unreachable!')
        except OperationalError:
            logger.exception("DataBase is unreachable!")
            return form.flash_and_redirect('DataBase is unreachable!')
        except ProgrammingError:
            logger.exception("Error while trying to operate with DataBase")
            return form.flash_and_redirect('Error while trying to operate with DataBase')
        except Exception:
            logger.exception('Unknown error!')
            return form.flash_and_redirect("Unknown error!")
        next_path = flask.request.args.get('next')
        if next_path:
            logger.info("Redirect to %s...", next_path)
            return flask.redirect(next_path)
        return flask.redirect(flask.url_for('admin.index'))

    @expose('/logout', methods=['GET'])
    @login_required
    def logout(self) -> Response:
        logout_user()
        return flask.redirect(flask.url_for('admin.login'))

    @expose('/', methods=['GET', 'POST'])  # noqa: C901
    @login_required
    def index(self) -> typing.Any:  # noqa: C901
        return self.render(
            'index.html', form=CustomPageForm(template_path=self._context.admin_settings.index_template_path)
        )
