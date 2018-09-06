# Copyright (C) 2018, Anthony Oteri
# All rights reserved


def test_can_access_db(session):
    result = session.execute("select 1")
    assert result.scalar() == 1
