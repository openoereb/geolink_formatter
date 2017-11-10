# -*- coding: utf-8 -*-
import datetime
from contextlib import contextmanager

import pytest
import requests_mock

from geolink_formatter.entity import Document, File


@pytest.fixture()
def documents():
    return [
        Document(
            '1',
            'Document with file',
            'main',
            'decree',
            [File('Test file', 'http://www.example.com/test.pdf', 'main')],
            enactment_date=datetime.date(2017, 1, 15)
        )
    ]


@pytest.fixture()
def document_without_file():
    return [
        Document(
            '1',
            'Document with file',
            'main',
            'decree',
            [],
            enactment_date=datetime.date(2017, 1, 15)
        )
    ]


@contextmanager
def _mock_request():
    with requests_mock.mock() as m:
        with open('tests/resources/geolink.xml', 'rb') as f:
            m.get('http://oereblex.test.com/api/geolinks/1500.xml', content=f.read())
        yield m


@pytest.fixture()
def mock_request():
    return _mock_request
