import pytest
from markupsafe import Markup
from pytest_mock import MockerFixture

from overhave.admin.views import TestRunView, result_report_formatter
from overhave.db import TestRun, TestRunStatus


class TestResultReportFormatter:
    """ Unit tests for result_report_formatter. """

    def test_empty_status(self, test_testrun_view: TestRunView, mocker: MockerFixture):
        assert result_report_formatter(
            view=test_testrun_view, context=mocker.MagicMock(), model=TestRun(), name="status"
        ) == Markup("")

    @pytest.mark.parametrize("status", [x.value for x in list(TestRunStatus)])
    def test_success_status_no_report(
        self,
        test_testrun_view,
        mocker: MockerFixture,
        test_testrun_id: int,
        status: str,
        test_testrun_button_css_class: str,
    ):
        result = result_report_formatter(
            view=test_testrun_view,
            context=mocker.MagicMock(),
            model=TestRun(id=test_testrun_id, status=status),
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

    @pytest.mark.parametrize("status", [x.value for x in list(TestRunStatus)])
    def test_success_status_with_report(
        self,
        test_testrun_view,
        mocker: MockerFixture,
        test_testrun_id: int,
        test_testrun_report_link: str,
        status: str,
        test_testrun_button_css_class: str,
    ):
        result = result_report_formatter(
            view=test_testrun_view,
            context=mocker.MagicMock(),
            model=TestRun(id=test_testrun_id, status=status, report=test_testrun_report_link),
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
