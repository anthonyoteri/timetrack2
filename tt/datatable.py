# Copyright (C) 2018, Anthony Oteri
# All rights reserved.
import tabulate


class Datatable(object):
    """Representation of a printable data table.

    :param table: A list of dictionaries containing the data.
    :param headers: A list or tuple of required header columns.
    :param labels: A list of label values for the rows.
    :param summaries: A list of summary values for the rows.
    :param label_header: An optional header for the label column.
    :param summary_header: An optional header for the summary column.
    :param table_fmt: Formating string to apply to this table.
    :param sort_fn: Callable used to sort the columns.
    :param header_fn: Callable to apply to each header value.
    :param label_fn: Callable to apply to each label value.
    :param value_fn: Callable to apply to each data value.
    """

    table_fmt = None
    """Default table formatting style."""

    sort_fn = sorted
    """Default sorting method."""

    header_fn = str.capitalize
    """Default function to apply to all headers."""

    label_fn = str.capitalize
    """Default function to apply to all labels."""

    summary_fn = None
    """Default function to apply to all summaries."""

    value_fn = None
    """Default function to apply to all values."""

    def __init__(self,
                 table=None,
                 headers=None,
                 labels=None,
                 summaries=None,
                 label_header=None,
                 summary_header=None,
                 table_fmt=None,
                 sort_fn=None,
                 header_fn=None,
                 label_fn=None,
                 summary_fn=None,
                 value_fn=None):

        self.table = list(table) if table is not None else list()
        self.headers = headers if headers is not None else set()
        self.labels = list(labels) if labels is not None else list()
        self.summaries = list(summaries) if summaries is not None else list()

        self.label_header = label_header
        self.summary_header = summary_header

        self.caption = None

        self.table_fmt = table_fmt or Datatable.table_fmt or self.__nop
        self.sort_fn = sort_fn or Datatable.sort_fn or self.__nop
        self.header_fn = header_fn or Datatable.header_fn or self.__nop
        self.label_fn = label_fn or Datatable.label_fn or self.__nop
        self.summary_fn = summary_fn or Datatable.summary_fn or self.__nop
        self.value_fn = value_fn or Datatable.value_fn or self.__nop

    def __nop(self, x):
        """Dummy No-Operation pass-through function."""
        return x

    def append(self, row, label=None, summary=None):
        """Append a row to the table.

        :param row: A dictionary containing the data for 1 row.  Missing
                    columns are allowed.
        :param label: An optional label description for the row.
        :param summary: Value for a final column"
        """
        self.labels.append(label)
        self.summaries.append(summary)
        self.table.append(row)

    def _make(self):
        """Construct the full table.

        This method does the following:

        1) Determines the full set of headers by looking at all the columns in
        the data.
        2) Applies the header_fn to each header value
        3) Sorts the headers by the sort_fn
        4) Applies the label_fn to each label for each row
        5) Applies the value_fn to each value in each row
        6) Fills in the missing columns in the data.

        :returns: A tuple consisting of the sorted list of headers, and a table
                  of values.
        """

        if not self.headers:
            for row in self.table:
                self.headers = self.headers | set(row.keys())
            self.headers = self.sort_fn(list(self.headers))

        result = []
        for i, row in enumerate(self.table):
            if any(self.labels):
                try:
                    label = [self.label_fn(self.labels[i])]
                except IndexError:
                    label = [None]
            else:
                label = []

            if any(self.summaries):
                try:
                    summary = [self.summary_fn(self.summaries[i])]
                except IndexError:
                    summary = [None]
            else:
                summary = []

            result.append(
                label + [self.value_fn(row.get(h))
                         for h in self.headers] + summary)

        headers = list(self.header_fn(h) for h in self.headers)
        if self.label_header is not None and any(self.labels):
            headers = [self.label_header] + headers
        if self.summary_header is not None and any(self.summaries):
            headers = headers + [self.summary_header]

        return headers, result

    def __str__(self):
        headers, table = self._make()
        table = tabulate.tabulate(table, headers, tablefmt=self.table_fmt)

        if self.caption:
            return "%s\n%s" % (self.caption, table)
        else:
            return table
