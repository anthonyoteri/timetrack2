# Copyright (C) 2018, Anthony Oteri
# All rights reserved

from tt.datatable import Datatable

from unittest import mock


def test_basic_table():
    rows = [
        {"col_1": "1", "col_2": "2", "col_3": "3"},
        {"col_1": "4", "col_2": "5", "col_3": "6"},
    ]

    t = Datatable(table=rows)

    headers, table = t._make()

    assert headers == ["Col_1", "Col_2", "Col_3"]
    assert table == [["1", "2", "3"], ["4", "5", "6"]]


def test_basic_table_append():
    rows = [
        {"col_1": "1", "col_2": "2", "col_3": "3"},
        {"col_1": "4", "col_2": "5", "col_3": "6"},
    ]

    t = Datatable()
    for r in rows:
        t.append(r)

    headers, table = t._make()

    assert headers == ["Col_1", "Col_2", "Col_3"]
    assert table == [["1", "2", "3"], ["4", "5", "6"]]


def test_basic_table_labels():
    rows = [
        {"col_1": "1", "col_2": "2", "col_3": "3"},
        {"col_1": "4", "col_2": "5", "col_3": "6"},
    ]

    t = Datatable(table=rows, labels=["row_0", "row_1"])

    headers, table = t._make()

    assert headers == ["Col_1", "Col_2", "Col_3"]
    assert table == [["Row_0", "1", "2", "3"], ["Row_1", "4", "5", "6"]]


def test_basic_table_append_with_labels():
    rows = [
        {"col_1": "1", "col_2": "2", "col_3": "3"},
        {"col_1": "4", "col_2": "5", "col_3": "6"},
    ]

    t = Datatable()
    for i, r in enumerate(rows):
        t.append(r, label="row_%d" % i)

    headers, table = t._make()

    assert headers == ["Col_1", "Col_2", "Col_3"]
    assert table == [["Row_0", "1", "2", "3"], ["Row_1", "4", "5", "6"]]


def test_basic_table_not_enough_labels():
    rows = [
        {"col_1": "1", "col_2": "2", "col_3": "3"},
        {"col_1": "4", "col_2": "5", "col_3": "6"},
    ]

    t = Datatable(table=rows, labels=["row_0"])

    headers, table = t._make()

    assert headers == ["Col_1", "Col_2", "Col_3"]
    assert table == [["Row_0", "1", "2", "3"], [None, "4", "5", "6"]]


def test_basic_table_summary():
    rows = [
        {"col_1": "1", "col_2": "2", "col_3": "3"},
        {"col_1": "4", "col_2": "5", "col_3": "6"},
    ]

    t = Datatable(table=rows, summaries=["row_0", "row_1"], summary_header="summary")

    headers, table = t._make()

    assert headers == ["Col_1", "Col_2", "Col_3", "summary"]
    assert table == [["1", "2", "3", "row_0"], ["4", "5", "6", "row_1"]]


def test_basic_table_append_with_summary():
    rows = [
        {"col_1": "1", "col_2": "2", "col_3": "3"},
        {"col_1": "4", "col_2": "5", "col_3": "6"},
    ]

    t = Datatable()
    for i, r in enumerate(rows):
        t.append(r, summary="row_%d" % i)

    headers, table = t._make()

    assert headers == ["Col_1", "Col_2", "Col_3"]
    assert table == [["1", "2", "3", "row_0"], ["4", "5", "6", "row_1"]]


def test_basic_table_not_enough_summaries():
    rows = [
        {"col_1": "1", "col_2": "2", "col_3": "3"},
        {"col_1": "4", "col_2": "5", "col_3": "6"},
    ]

    t = Datatable(table=rows, summaries=["row_0"])

    headers, table = t._make()

    assert headers == ["Col_1", "Col_2", "Col_3"]
    assert table == [["1", "2", "3", "row_0"], ["4", "5", "6", None]]


def test_basic_table_missing_values():
    rows = [{"col_1": "1", "col_3": "3"}, {"col_2": "5", "col_3": "6"}]

    t = Datatable(table=rows)

    headers, table = t._make()

    assert headers == ["Col_1", "Col_2", "Col_3"]
    assert table == [["1", None, "3"], [None, "5", "6"]]


def test_basic_table_extra_column():
    rows = [
        {"col_1": "1", "col_2": "2", "col_3": "3"},
        {"col_1": "4", "col_2": "5", "col_3": "6"},
    ]

    t = Datatable(table=rows, headers=["col_1", "col_2", "col_3", "col_4"])

    headers, table = t._make()

    assert headers == ["Col_1", "Col_2", "Col_3", "Col_4"]
    assert table == [["1", "2", "3", None], ["4", "5", "6", None]]


@mock.patch("tabulate.tabulate")
def test_table_string_conversion(tabulate, mocker):
    rows = [
        {"col_1": "1", "col_2": "2", "col_3": "3"},
        {"col_1": "4", "col_2": "5", "col_3": "6"},
    ]

    table_fmt = mocker.MagicMock()

    t = Datatable(table=rows, table_fmt=table_fmt)
    tabulate.return_value = ""
    str(t)

    headers = ["Col_1", "Col_2", "Col_3"]
    table = [["1", "2", "3"], ["4", "5", "6"]]

    tabulate.assert_called_once_with(table, headers, tablefmt=table_fmt)


@mock.patch("tabulate.tabulate")
def test_table_string_conversion_with_caption(tabulate, mocker):
    rows = [
        {"col_1": "1", "col_2": "2", "col_3": "3"},
        {"col_1": "4", "col_2": "5", "col_3": "6"},
    ]

    table_fmt = mocker.MagicMock()

    t = Datatable(table=rows, table_fmt=table_fmt)
    t.caption = "Foo"
    tabulate.return_value = "Bar"
    assert "Foo\nBar" == str(t)
