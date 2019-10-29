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
            id='1',
            title='Document with file',
            category='main',
            doctype='decree',
            files=[File(title='Test file', href='http://www.example.com/test.pdf', category='main')],
            enactment_date=datetime.date(2017, 1, 15)
        )
    ]


@pytest.fixture()
def document_without_file():
    return [
        Document(
            id='1',
            title='Document without file',
            category='main',
            doctype='decree',
            files=[],
            enactment_date=datetime.date(2017, 1, 15)
        )
    ]


@pytest.fixture()
def document_archived():
    return [
        Document(
            id='1',
            title='Archived document',
            category='main',
            doctype='decree',
            files=[File(title='Test file', href='http://www.example.com/test.pdf', category='main')],
            enactment_date=datetime.date(2017, 1, 15),
            abrogation_date=datetime.date(2019, 1, 1)
        )
    ]


@contextmanager
def _mock_request():
    with requests_mock.mock() as m:
        with open('tests/resources/geolink_v1.1.1.xml', 'rb') as f:
            m.get('http://oereblex.test.com/api/geolinks/1500.xml', content=f.read())
        yield m


@pytest.fixture()
def mock_request():
    return _mock_request
