# Copyright (C) 2018, Anthony Oteri
# All rights reserved.

import logging

import pytest

from tt.sql import connect_test, transaction


@pytest.fixture(scope='module')
def log():
    log = logging.getLogger(__name__)
    logging.basicConfig(level=logging.DEBUG)
    return log


@pytest.yield_fixture
def session(log):
    connect_test()

    with transaction() as session:
        yield session
