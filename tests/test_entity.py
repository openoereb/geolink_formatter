# -*- coding: utf-8 -*-
import datetime

import pytest

from geolink_formatter.entity import File, Document


def test_file():
    f = File(description='File title', href='http://my.link.to/file', category='test', title='test.pdf')
    assert isinstance(f, File)
    assert f.description == 'File title'
    assert f.href == 'http://my.link.to/file'
    assert f.category == 'test'
    assert f.title == 'test.pdf'


def test_file_empty():
    f = File()
    assert isinstance(f, File)
    assert f.title is None
    assert f.href is None
    assert f.category is None
    assert f.description is None


def test_document():
    date = datetime.date.today()
    d = Document(id='1', title='Test', category='test', doctype='testdoc',
                 files=[File('TestCategory', 'http://my.link.to/file', 'Test Title', 'test.pdf')],
                 enactment_date=date, federal_level='testlevel', authority='Authority',
                 authority_url='http://my.link.to/authority', type='testtype', subtype='testsubtype',
                 decree_date=date, instance='INST', number='123', abbreviation='abbr', abrogation_date=date,
                 cycle='cycle', municipality='Test Municipality', index=1, status='neuer Status',
                 status_start_date=date, status_end_date=date)
    assert isinstance(d, Document)
    assert d.id == '1'
    assert d.title == 'Test'
    assert d.category == 'test'
    assert d.doctype == 'testdoc'
    assert len(d.files) == 1 and isinstance(d.files[0], File)
    assert d.enactment_date == date
    assert d.federal_level == 'testlevel'
    assert d.authority == 'Authority'
    assert d.authority_url == 'http://my.link.to/authority'
    assert d.type == 'testtype'
    assert d.subtype == 'testsubtype'
    assert d.decree_date == date
    assert d.instance == 'INST'
    assert d.number == '123'
    assert d.abbreviation == 'abbr'
    assert d.abrogation_date == date
    assert d.cycle == 'cycle'
    assert d.municipality == 'Test Municipality'
    assert d.index == 1
    assert d.status == 'neuer Status'
    assert d.status_start_date == date
    assert d.status_end_date == date


def test_document_empty():
    d = Document([])
    assert isinstance(d, Document)
    assert d.id is None
    assert d.title is None
    assert d.category is None
    assert d.doctype is None
    assert len(d.files) == 0 and isinstance(d.files, list)
    assert d.enactment_date is None
    assert d.federal_level is None
    assert d.authority is None
    assert d.authority_url is None
    assert d.type is None
    assert d.subtype is None
    assert d.decree_date is None
    assert d.instance is None
    assert d.number is None
    assert d.abbreviation is None
    assert d.abrogation_date is None
    assert d.cycle is None
    assert d.municipality is None
    assert d.index is None
    assert d.status is None
    assert d.status_start_date is None
    assert d.status_end_date is None


def test_document_invalid_decree_date():
    with pytest.raises(TypeError):
        Document([], decree_date='invalid')


def test_document_invalid_enactment_date():
    with pytest.raises(TypeError):
        Document([], enactment_date='invalid')


def test_document_invalid_abrogation_date():
    with pytest.raises(TypeError):
        Document([], abrogation_date='invalid')


def test_document_invalid_status_start_date():
    with pytest.raises(TypeError):
        Document([], status_start_date='invalid')


def test_document_invalid_status_end_date():
    with pytest.raises(TypeError):
        Document([], status_end_date='invalid')


def test_document_invalid_files():
    with pytest.raises(TypeError):
        Document('invalid')
