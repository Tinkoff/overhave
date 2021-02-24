from datetime import datetime, timedelta
from typing import Optional

import pytest
from markupsafe import Markup
from pytest_mock import MockerFixture

from overhave.admin.views import TestRunView, datetime_formatter, result_report_formatter
from overhave.db import TestReportStatus, TestRun, TestRunStatus
from overhave.utils import get_current_time


class TestResultReportFormatter:
    """ Unit tests for result_report_formatter. """

    def test_empty_status(self, test_testrun_view: TestRunView, mocker: MockerFixture):
        assert result_report_formatter(
            view=test_testrun_view, context=mocker.MagicMock(), model=TestRun(), name="status"
        ) == Markup("")

    @pytest.mark.parametrize("status", list(TestRunStatus))
    @pytest.mark.parametrize("report_status", [x for x in list(TestReportStatus) if not x.has_report])
    def test_no_report(
        self,
        test_testrun_view,
        mocker: MockerFixture,
        test_testrun_id: int,
        status: TestRunStatus,
        report_status: TestReportStatus,
        test_testrun_button_css_class: str,
    ):
        result = result_report_formatter(
            view=test_testrun_view,
            context=mocker.MagicMock(),
            model=TestRun(id=test_testrun_id, status=status, report_status=report_status),
            name="status",
        )
        assert result == Markup(
            f"<a href='/testrun/details/?id={test_testrun_id}'"
            f"<form action='#'>"
            f"<fieldset title='Show details'>"
            f"<button class='link-button {test_testrun_button_css_class}'>{status}</button>"
            "</fieldset>"
            "</form>"
            "</a>"
        )

    @pytest.mark.parametrize("status", list(TestRunStatus))
    @pytest.mark.parametrize("report_status", [x for x in list(TestReportStatus) if x.has_report])
    def test_with_report(
        self,
        test_testrun_view,
        mocker: MockerFixture,
        test_testrun_id: int,
        status: TestRunStatus,
        report_status: TestReportStatus,
        test_testrun_report_link: Optional[str],
        test_testrun_button_css_class: str,
    ):
        result = result_report_formatter(
            view=test_testrun_view,
            context=mocker.MagicMock(),
            model=TestRun(
                id=test_testrun_id, status=status, report_status=report_status, report=test_testrun_report_link
            ),
            name="status",
        )
        assert result == Markup(
            f"<a href='/reports/{test_testrun_report_link}' target='_blank'"
            f"<form action='#'>"
            f"<fieldset title='Go to report'>"
            f"<button class='link-button {test_testrun_button_css_class}'>{status}</button>"
            "</fieldset>"
            "</form>"
            "</a>"
        )


class TestDatetimeFormatter:
    """ Unit tests for datetime_formatter. """

    def test_empty_status(self, test_testrun_view: TestRunView, mocker: MockerFixture):
        assert datetime_formatter(
            view=test_testrun_view, context=mocker.MagicMock(), model=TestRun(), name="start"
        ) == Markup("")

    @pytest.mark.parametrize(
        ("column_name", "time"),
        [
            ("created_at", get_current_time()),
            ("start", get_current_time() + timedelta(seconds=1)),
            ("end", get_current_time() + timedelta(seconds=5)),
        ],
    )
    def test_time(
        self, test_testrun_view, mocker: MockerFixture, test_testrun_id: int, column_name: str, time: datetime
    ):
        result = datetime_formatter(
            view=test_testrun_view,
            context=mocker.MagicMock(),
            model=TestRun(**{"id": test_testrun_id, column_name: time}),
            name=column_name,
        )
        assert result == Markup(time.strftime("%d-%m-%Y %H:%M:%S"))
