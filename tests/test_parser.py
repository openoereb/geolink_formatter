# -*- coding: utf-8 -*-
import pytest
import requests_mock
from lxml.etree import _Element, DocumentInvalid
from requests import RequestException

from geolink_formatter.parser import XML, SCHEMA


def test_xml_init():
    parser = XML(host_url='http://oereblex.test.com')
    assert isinstance(parser, XML)
    assert parser.host_url == 'http://oereblex.test.com'


@pytest.mark.parametrize('as_bytes', [False, True])
def test_xml_parse(as_bytes):
    xml = u"""<?xml version="1.0" encoding="utf-8"?>
    <geolinks>
        <document authority='Example Authority' authority_url='http://www.example.com'
                  category='main' doctype='decree' enactment_date='1999-10-18'
                  federal_level='Gemeinde' id='1' subtype='Example Subtype' title='Example'
                  type='Example Type'>
            <file category='main' href='/api/attachments/1' title='example1.pdf'></file>
            <file category='additional' href='/api/attachments/2' title='example2.pdf'></file>
            <file category='additional' href='/api/attachments/3' title='example3.pdf'></file>
        </document>
        <document authority='Another authority' authority_url='http://www.example.com' category='related'
                  doctype='edict' enactment_date='2016-01-01' federal_level='Bund' id='2'
                  title='Another example'>
            <file category='main' href='http://www.example.com/example' title='example.pdf'></file>
        </document>
    </geolinks>
    """
    if as_bytes:
        xml = xml.encode('utf-16be')
    parser = XML()
    root = parser._parse_xml(xml)
    assert isinstance(root, _Element)
    assert root.tag == 'geolinks'
    assert len(root.findall('document')) == 2
    document = root.find('document')
    assert isinstance(document, _Element)
    assert document.attrib.get('category') == 'main'
    assert len(document.findall('file')) == 3


def test_xml_from_string_invalid():
    xml = """<?xml version="1.0" encoding="utf-8"?>
    <invalidTag></invalidTag>
    """
    with pytest.raises(DocumentInvalid):
        parser = XML()
        parser.from_string(xml)


@pytest.mark.parametrize('host_url', [None, 'http://oereblex.test.com'])
def test_xml_from_string(host_url):
    xml = """<?xml version="1.0" encoding="utf-8"?>
    <geolinks>
        <document authority='Example Authority' authority_url='http://www.example.com'
                  category='main' doctype='decree' enactment_date='1999-10-18'
                  federal_level='Gemeinde' id='1' subtype='Example Subtype' title='Example'
                  type='Example Type' decree_date='1999-11-01'>
            <file category='main' href='/api/attachments/1' title='example1.pdf'></file>
            <file category='additional' href='/api/attachments/2'
                  description='Example File' title='example2.pdf'></file>
            <file category='additional' href='/api/attachments/3'
                  description='Example 2' title='example3.pdf'></file>
        </document>
        <document authority='Another authority' authority_url='http://www.example.com' category='related'
                  doctype='edict' enactment_date='2016-01-01' federal_level='Bund' id='2'
                  title='Another example'>
            <file category='main' href='http://www.example.com/example' title='example.pdf'></file>
        </document>
    </geolinks>
    """
    parser = XML(host_url=host_url)
    documents = parser.from_string(xml)
    assert len(documents) == 2
    assert documents[0].authority == 'Example Authority'
    assert documents[0].authority_url == 'http://www.example.com'
    assert documents[0].category == 'main'
    assert documents[0].doctype == 'decree'
    assert documents[0].enactment_date.year == 1999
    assert documents[0].enactment_date.month == 10
    assert documents[0].enactment_date.day == 18
    assert documents[0].federal_level == 'Gemeinde'
    assert documents[0].id == '1'
    assert documents[0].subtype == 'Example Subtype'
    assert documents[0].title == 'Example'
    assert documents[0].type == 'Example Type'
    assert documents[0].decree_date.year == 1999
    assert documents[0].decree_date.month == 11
    assert documents[0].decree_date.day == 1
    assert len(documents[0].files) == 3
    assert documents[0].files[1].description == 'Example File'
    assert documents[0].files[1].title == 'example2.pdf'
    if host_url:
        assert documents[0].files[1].href == 'http://oereblex.test.com/api/attachments/2'
    else:
        assert documents[0].files[1].href == '/api/attachments/2'
    assert documents[0].files[1].category == 'additional'


def test_xml_duplicate_document():
    xml = """<?xml version="1.0" encoding="utf-8"?>
    <geolinks>
        <document authority='Example Authority' authority_url='http://www.example.com'
                  category='main' doctype='decree' enactment_date='1999-10-18'
                  federal_level='Gemeinde' id='1' subtype='Example Subtype' title='Example'
                  type='Example Type' decree_date='1999-11-01'>
            <file category='main' href='/api/attachments/1' title='example1.pdf'></file>
            <file category='additional' href='/api/attachments/2' title='example2.pdf'></file>
            <file category='additional' href='/api/attachments/3' title='example3.pdf'></file>
        </document>
        <document authority='Example Authority' authority_url='http://www.example.com'
                  category='main' doctype='decree' enactment_date='1999-10-18'
                  federal_level='Gemeinde' id='1' subtype='Example Subtype' title='Example'
                  type='Example Type' decree_date='1999-11-01'>
            <file category='main' href='/api/attachments/1' title='example1.pdf'></file>
            <file category='additional' href='/api/attachments/2' title='example2.pdf'></file>
            <file category='additional' href='/api/attachments/3' title='example3.pdf'></file>
        </document>
    </geolinks>
    """
    parser = XML()
    documents = parser.from_string(xml)
    assert len(documents) == 1


def test_xml_from_url_invalid():
    with pytest.raises(RequestException):
        XML().from_url('http://invalid.url.bl.ch/')


def test_xml_from_url_error():
    with requests_mock.mock() as m:
        m.get('http://oereblex.test.com/api/geolinks/1501.xml', text='error', status_code=500)
        with pytest.raises(RequestException):
            XML().from_url('http://oereblex.test.com/api/geolinks/1501.xml')


def test_xml_from_url(mock_request):
    fmt = '%Y-%m-%d'
    with mock_request():
        documents = XML().from_url('http://oereblex.test.com/api/geolinks/1500.xml')
        assert len(documents) == 5
        assert len(documents[0].files) == 5
        assert documents[0].decree_date.strftime(fmt) == '2001-03-15'


def test_wrong_schema_version(mock_request):
    with mock_request():
        with pytest.raises(DocumentInvalid):
            XML(version=SCHEMA.V1_0_0).from_url('http://oereblex.test.com/api/geolinks/1500.xml')


def test_schema_version_1_0_0():
    with requests_mock.mock() as m:
        with open('tests/resources/geolink_v1.0.0.xml', 'rb') as f:
            m.get('http://oereblex.test.com/api/geolinks/1500.xml', content=f.read())
        documents = XML(version=SCHEMA.V1_0_0).from_url('http://oereblex.test.com/api/geolinks/1500.xml')
    assert documents[0].cycle == 'cycle'


def test_schema_version_1_1_0():
    fmt = '%Y-%m-%d'
    with requests_mock.mock() as m:
        with open('tests/resources/geolink_v1.1.0.xml', 'rb') as f:
            m.get('http://oereblex.test.com/api/geolinks/1500.xml', content=f.read())
        documents = XML(version=SCHEMA.V1_1_0).from_url('http://oereblex.test.com/api/geolinks/1500.xml')
    assert documents[0].number == '1A'
    assert documents[0].abbreviation == 'abbr'
    assert documents[0].abrogation_date.strftime(fmt) == '2008-12-31'


def test_schema_version_1_1_1():
    with requests_mock.mock() as m:
        with open('tests/resources/geolink_v1.1.1.xml', 'rb') as f:
            m.get('http://oereblex.test.com/api/geolinks/1500.xml', content=f.read())
        documents = XML(version=SCHEMA.V1_1_1).from_url('http://oereblex.test.com/api/geolinks/1500.xml')
    assert documents[0].number == '1A'
    assert documents[0].abbreviation == 'abbr'
    assert documents[0].abrogation_date is None


def test_schema_version_1_1_1_with_bezirk():
    fmt = '%Y-%m-%d'
    with requests_mock.mock() as m:
        with open('tests/resources/geolink_v1.1.1_bezirk.xml', 'rb') as f:
            m.get('http://oereblex.test.com/api/geolinks/1500.xml', content=f.read())
        documents = XML(version=SCHEMA.V1_1_1).from_url('http://oereblex.test.com/api/geolinks/1500.xml')
    assert documents[0].number == '1A'
    assert documents[0].abbreviation == 'abbr'
    assert documents[0].abrogation_date.strftime(fmt) == '2008-12-31'
    assert documents[0].federal_level == 'Bezirk'


def test_schema_version_1_2_0():
    with requests_mock.mock() as m:
        with open('tests/resources/geolink_v1.2.0.xml', 'rb') as f:
            m.get('http://oereblex.test.com/api/geolinks/1500.xml', content=f.read())
        documents = XML(version=SCHEMA.V1_2_0).from_url('http://oereblex.test.com/api/geolinks/1500.xml')
    assert len(documents) == 5
    assert documents[-1].doctype == 'notice'
    assert documents[-1].category == 'related'
    assert len(documents[-1].files) == 1


def test_schema_version_1_2_1():
    with requests_mock.mock() as m:
        with open('tests/resources/geolink_v1.2.1.xml', 'rb') as f:
            m.get('http://oereblex.test.com/api/geolinks/1500.xml', content=f.read())
        documents = XML(version=SCHEMA.V1_2_1).from_url('http://oereblex.test.com/api/geolinks/1500.xml')
    assert len(documents) == 5
    assert documents[0].municipality == 'Testgemeinde'
    assert documents[1].municipality is None


def test_default_version_with_locale():
    with requests_mock.mock() as m:
        with open('tests/resources/geolink_v1.2.1.xml', 'rb') as f:
            m.get('http://oereblex.test.com/api/geolinks/1500.xml?locale=fr', content=f.read())
        documents = XML().from_url('http://oereblex.test.com/api/geolinks/1500.xml', {'locale': 'fr'})
    assert documents[0].number == '1A'
    assert documents[0].abbreviation == 'abbr'


def test_dtd_validation_valid():
    content = XML(dtd_validation=True, xsd_validation=False)._parse_xml(
        """<?xml version="1.1" encoding="utf-8"?>
        <!DOCTYPE root [<!ELEMENT root EMPTY>]>
        <root></root>
        """
    )
    assert content.tag == 'root'


def test_dtd_validation_invalid():
    with pytest.raises(DocumentInvalid):
        XML(dtd_validation=True, xsd_validation=False)._parse_xml(
            """<?xml version="1.1" encoding="utf-8"?>
            <root></root>
            """
        )
