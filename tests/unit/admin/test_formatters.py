from datetime import datetime, timedelta
from types import FunctionType
from typing import Dict, Optional, Sequence

import pytest
from faker import Faker
from markupsafe import Markup
from pytest_mock import MockerFixture
from yarl import URL

from overhave import db
from overhave.admin.views import (
    DraftView,
    FeatureView,
    TestRunView,
    TestUserView,
    datetime_formatter,
    result_report_formatter,
    task_formatter,
)
from overhave.admin.views.base import ModelViewConfigured
from overhave.admin.views.formatters.formatters import (
    draft_feature_formatter,
    draft_prurl_formatter,
    draft_testrun_formatter,
    feature_link_formatter,
    file_path_formatter,
    json_formatter,
)
from overhave.admin.views.formatters.helpers import (
    get_feature_link_markup,
    get_report_index_link,
    get_testrun_details_link,
)
from overhave.db import TestReportStatus, TestRun, TestRunStatus, TestUser
from overhave.utils import get_current_time


class TestSafeFormatter:
    """ Unit tests for safe_formatter decorator. """

    @pytest.mark.parametrize(
        "formatter",
        [
            datetime_formatter,
            task_formatter,
            result_report_formatter,
            json_formatter,
            feature_link_formatter,
            draft_feature_formatter,
            draft_testrun_formatter,
            draft_prurl_formatter,
            file_path_formatter,
        ],
    )
    def test_with_nullable_attribute(
        self,
        test_table: db.BaseTable,
        test_view: ModelViewConfigured,
        formatter: FunctionType,
        mocker: MockerFixture,
        faker: Faker,
    ) -> None:
        assert formatter(
            view=test_view, context=mocker.MagicMock(), model=test_table, name="mykeysodifferrent"
        ) == Markup("")


class TestDatetimeFormatter:
    """ Unit tests for datetime_formatter. """

    @pytest.mark.parametrize(
        ("column_name", "value"), [("created_at", get_current_time())],
    )
    def test_created_at(
        self,
        test_table: db.BaseTable,
        test_view: ModelViewConfigured,
        mocker: MockerFixture,
        test_testrun_id: int,
        column_name: str,
        value: datetime,
    ) -> None:
        setattr(test_table, column_name, value)
        result = datetime_formatter(view=test_view, context=mocker.MagicMock(), model=test_table, name=column_name,)
        assert result == Markup(value.strftime("%d-%m-%Y %H:%M:%S"))

    @pytest.mark.parametrize(
        ("column_name", "value"),
        [("start", get_current_time() + timedelta(seconds=1)), ("end", get_current_time() + timedelta(seconds=5))],
    )
    def test_testrun_attrs(
        self,
        test_testrun_view: TestRunView,
        mocker: MockerFixture,
        test_testrun_id: int,
        column_name: str,
        value: datetime,
    ) -> None:
        result = datetime_formatter(
            view=test_testrun_view,
            context=mocker.MagicMock(),
            model=TestRun(**{"id": test_testrun_id, column_name: value}),  # type: ignore
            name=column_name,
        )
        assert result == Markup(value.strftime("%d-%m-%Y %H:%M:%S"))


@pytest.mark.parametrize("column_name", ["task"])
@pytest.mark.parametrize("value", [["TCS-123"], ["TCS-456", "TCS-789"]])
class TestTaskFormatter:
    """ Unit tests for task_formatter. """

    @pytest.mark.parametrize("test_browse_url", [None], indirect=True)
    def test_task_without_url(
        self,
        test_browse_url: None,
        test_feature_view_mocked: FeatureView,
        column_name: str,
        value: Sequence[str],
        mocker: MockerFixture,
    ) -> None:
        assert task_formatter(
            view=test_feature_view_mocked,
            context=mocker.MagicMock(),
            model=db.Feature(**{column_name: value}),  # type: ignore
            name=column_name,
        ) == Markup(", ".join(value))

    @pytest.mark.parametrize("test_browse_url", ["https://overhave.readthedocs.io"], indirect=True)
    def test_task_with_url(
        self,
        test_browse_url: str,
        test_feature_view_mocked: FeatureView,
        column_name: str,
        value: Sequence[str],
        mocker: MockerFixture,
    ) -> None:
        task_links = []
        for task in value:
            task_links.append(f"<a href='{test_browse_url}/{task}' target='blank'>{task}</a>")
        assert task_formatter(
            view=test_feature_view_mocked,
            context=mocker.MagicMock(),
            model=db.Feature(**{column_name: value}),  # type: ignore
            name=column_name,
        ) == Markup(", ".join(task_links))


@pytest.mark.parametrize("column_name", ["status"])
class TestResultReportFormatter:
    """ Unit tests for result_report_formatter. """

    @pytest.mark.parametrize("status", list(TestRunStatus))
    @pytest.mark.parametrize("report_status", [x for x in list(TestReportStatus) if not x.has_report])
    def test_no_report(
        self,
        test_testrun_view: TestRunView,
        mocker: MockerFixture,
        test_testrun_id: int,
        column_name: str,
        status: TestRunStatus,
        report_status: TestReportStatus,
        test_testrun_button_css_class: str,
    ) -> None:
        result = result_report_formatter(
            view=test_testrun_view,
            context=mocker.MagicMock(),
            model=TestRun(id=test_testrun_id, status=status, report_status=report_status),  # type: ignore
            name=column_name,
        )
        assert result == Markup(
            f"<form action='/testrun/details/?id={test_testrun_id}'>"
            f"<fieldset title='Show details'>"
            f"<button class='link-button {test_testrun_button_css_class}'>{status}</button>"
            "</fieldset>"
            "</form>"
        )

    @pytest.mark.parametrize("status", list(TestRunStatus))
    @pytest.mark.parametrize("report_status", [x for x in list(TestReportStatus) if x.has_report])
    def test_with_report(
        self,
        test_testrun_view: TestRunView,
        mocker: MockerFixture,
        test_testrun_id: int,
        column_name: str,
        status: TestRunStatus,
        report_status: TestReportStatus,
        test_testrun_report: Optional[str],
        test_testrun_button_css_class: str,
    ) -> None:
        result = result_report_formatter(
            view=test_testrun_view,
            context=mocker.MagicMock(),
            model=TestRun(  # type: ignore
                id=test_testrun_id, status=status, report_status=report_status, report=test_testrun_report
            ),
            name=column_name,
        )
        if test_testrun_report is None:
            raise RuntimeError
        assert result == Markup(
            f"<form action='{get_report_index_link(test_testrun_report)}' method='POST' target='_blank'>"
            f"<input type='hidden' name='run_id' value='{test_testrun_id}' />"
            f"<fieldset title='Go to report'>"
            f"<button class='link-button {test_testrun_button_css_class}' type='submit'>{status}</button>"
            "</fieldset>"
            "</form>"
        )


@pytest.mark.parametrize("column_name", ["specification"])
class TestJsonFormatter:
    """ Unit tests for json_formatter. """

    @pytest.mark.parametrize("value", [{"kek": "lol"}, {"a": "lot", "of": "items"}])
    def test_dict_with_data(
        self, test_testuser_view: TestUserView, mocker: MockerFixture, column_name: str, value: Dict[str, str],
    ) -> None:
        info = ""
        for k, v in list(filter(lambda x: x, value.items())):
            info += f"<b>{k}</b>:&nbsp;&nbsp;{v}<br>"
        expected = Markup("<form>" "<fieldset>" f"<div class='json-data'>{info}</div>" "</fieldset>" "</form>")

        result = json_formatter(
            view=test_testuser_view,
            context=mocker.MagicMock(),
            model=TestUser(**{column_name: value}),  # type: ignore
            name=column_name,
        )
        assert result == expected


@pytest.mark.parametrize("column_name", ["name"])
class TestFeatureLinkFormatter:
    """ Unit tests for feature_link_formatter. """

    @pytest.mark.parametrize("test_browse_url", [None], indirect=True)
    def test_with_feature(
        self,
        test_feature_view_mocked: FeatureView,
        mocker: MockerFixture,
        column_name: str,
        test_feature_id: int,
        test_feature_name: str,
    ) -> None:
        assert feature_link_formatter(
            view=test_feature_view_mocked,
            context=mocker.MagicMock(),
            model=db.Feature(**{"id": test_feature_id, column_name: test_feature_name}),  # type: ignore
            name=column_name,
        ) == get_feature_link_markup(feature_id=test_feature_id, feature_name=test_feature_name)

    def test_with_testrun(
        self,
        test_testrun_view: TestRunView,
        mocker: MockerFixture,
        column_name: str,
        test_feature_id: int,
        test_feature_name: str,
    ) -> None:
        assert feature_link_formatter(
            view=test_testrun_view,
            context=mocker.MagicMock(),
            model=db.TestRun(
                **{column_name: test_feature_name, "scenario": db.Scenario(feature_id=test_feature_id)}  # type: ignore
            ),
            name=column_name,
        ) == get_feature_link_markup(feature_id=test_feature_id, feature_name=test_feature_name)


@pytest.mark.parametrize("column_name", ["feature_id"])
class TestDraftFeatureFormatter:
    """ Unit tests for draft_feature_formatter. """

    def test_with_draft(
        self,
        test_draft_view: DraftView,
        mocker: MockerFixture,
        column_name: str,
        test_feature_id: int,
        test_feature_name: str,
    ) -> None:
        assert draft_feature_formatter(
            view=test_draft_view,
            context=mocker.MagicMock(),
            model=db.Draft(
                **{column_name: test_feature_id, "feature": db.Feature(name=test_feature_name)}  # type: ignore
            ),
            name=column_name,
        ) == get_feature_link_markup(feature_id=test_feature_id, feature_name=test_feature_name)


@pytest.mark.parametrize("column_name", ["test_run_id"])
class TestDraftTestRunFormatter:
    """ Unit tests for draft_testrun_formatter. """

    def test_with_id(
        self, test_draft_view: DraftView, mocker: MockerFixture, column_name: str, test_testrun_id: int
    ) -> None:
        assert draft_testrun_formatter(
            view=test_draft_view,
            context=mocker.MagicMock(),
            model=db.Draft(**{column_name: test_testrun_id}),  # type: ignore
            name=column_name,
        ) == Markup(f"<a {get_testrun_details_link(test_testrun_id)}>{test_testrun_id}</a>")


@pytest.mark.parametrize("column_name", ["pr_url"])
class TestDraftPrUrlFormatter:
    """ Unit tests for draft_prurl_formatter. """

    @pytest.mark.parametrize("test_prurl", ["https://overhave.readthedocs.io"], indirect=True)
    def test_with_url(
        self, test_draft_view: DraftView, mocker: MockerFixture, column_name: str, test_testrun_id: int, test_prurl: str
    ) -> None:
        assert draft_prurl_formatter(
            view=test_draft_view,
            context=mocker.MagicMock(),
            model=db.Draft(**{column_name: test_prurl}),  # type: ignore
            name=column_name,
        ) == Markup(f"<a href='{URL(test_prurl).human_repr()}'>{test_prurl}</a>")


@pytest.mark.parametrize("column_name", ["file_path"])
@pytest.mark.parametrize("value", ["my_file.feature", "my_folder/my_file.feature"])
@pytest.mark.parametrize("test_browse_url", [None], indirect=True)
class TestFilePathFormatter:
    """ Unit tests for file_path_formatter. """

    def test_task_without_url(
        self,
        test_browse_url: None,
        test_feature_view_mocked: FeatureView,
        column_name: str,
        value: str,
        mocker: MockerFixture,
    ) -> None:
        correct_value = value.rstrip(test_feature_view_mocked.feature_suffix).split("/")[-1]
        assert file_path_formatter(
            view=test_feature_view_mocked,
            context=mocker.MagicMock(),
            model=db.Feature(**{column_name: value}),  # type: ignore
            name=column_name,
        ) == Markup(f"<i>{correct_value}</i>")
