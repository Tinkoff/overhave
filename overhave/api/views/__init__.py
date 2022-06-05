# flake8: noqa
from .auth_views import login_for_access_token
from .extra_views import docs, favicon
from .feature_views import get_features_handler, run_test_by_tag_handler
from .tags_views import tags_item_handler, tags_list_handler
from .testuser_views import test_user_get_spec_handler, test_user_handler, test_user_put_spec_handler
