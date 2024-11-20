# -*- coding: utf-8 -*-
import pytest
import requests_mock
import xmlschema
from unittest.mock import patch
from lxml.etree import DocumentInvalid, _Element, Element, SubElement
from requests import RequestException

from geolink_formatter.parser import XML, SCHEMA
from geolink_formatter.entity import Document


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
    with pytest.raises(xmlschema.XMLSchemaValidationError):
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
    with requests_mock.mock() as mock_m:
        mock_m.get('http://oereblex.test.com/api/geolinks/1501.xml', text='error', status_code=500)
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
        with pytest.raises(xmlschema.XMLSchemaValidationError):
            XML(version=SCHEMA.V1_0_0).from_url('http://oereblex.test.com/api/geolinks/1500.xml')


def test_schema_version_1_0_0():
    with requests_mock.mock() as mock_m:
        with open('tests/resources/geolink_v1.0.0.xml', 'rb') as file_f:
            mock_m.get('http://oereblex.test.com/api/geolinks/1500.xml', content=file_f.read())
        documents = XML(version=SCHEMA.V1_0_0).from_url('http://oereblex.test.com/api/geolinks/1500.xml')
    assert documents[0].cycle == 'cycle'


def test_schema_version_1_1_0():
    fmt = '%Y-%m-%d'
    with requests_mock.mock() as mock_m:
        with open('tests/resources/geolink_v1.1.0.xml', 'rb') as file_f:
            mock_m.get('http://oereblex.test.com/api/geolinks/1500.xml', content=file_f.read())
        documents = XML(version=SCHEMA.V1_1_0).from_url('http://oereblex.test.com/api/geolinks/1500.xml')
    assert documents[0].number == '1A'
    assert documents[0].abbreviation == 'abbr'
    assert documents[0].abrogation_date.strftime(fmt) == '2008-12-31'


def test_schema_version_1_1_1():
    with requests_mock.mock() as mock_m:
        with open('tests/resources/geolink_v1.1.1.xml', 'rb') as file_f:
            mock_m.get('http://oereblex.test.com/api/geolinks/1500.xml', content=file_f.read())
        documents = XML(version=SCHEMA.V1_1_1).from_url('http://oereblex.test.com/api/geolinks/1500.xml')
    assert documents[0].number == '1A'
    assert documents[0].abbreviation == 'abbr'
    assert documents[0].abrogation_date is None


def test_schema_version_1_1_1_with_bezirk():
    fmt = '%Y-%m-%d'
    with requests_mock.mock() as mock_m:
        with open('tests/resources/geolink_v1.1.1_bezirk.xml', 'rb') as file_f:
            mock_m.get('http://oereblex.test.com/api/geolinks/1500.xml', content=file_f.read())
        documents = XML(version=SCHEMA.V1_1_1).from_url('http://oereblex.test.com/api/geolinks/1500.xml')
    assert documents[0].number == '1A'
    assert documents[0].abbreviation == 'abbr'
    assert documents[0].abrogation_date.strftime(fmt) == '2008-12-31'
    assert documents[0].federal_level == 'Bezirk'


def test_schema_version_1_2_0():
    with requests_mock.mock() as mock_m:
        with open('tests/resources/geolink_v1.2.0.xml', 'rb') as file_f:
            mock_m.get('http://oereblex.test.com/api/geolinks/1500.xml', content=file_f.read())
        documents = XML(version=SCHEMA.V1_2_0).from_url('http://oereblex.test.com/api/geolinks/1500.xml')
    assert len(documents) == 5
    assert documents[-1].doctype == 'notice'
    assert documents[-1].category == 'related'
    assert len(documents[-1].files) == 1


def test_schema_version_1_2_1():
    with requests_mock.mock() as mock_m:
        with open('tests/resources/geolink_v1.2.1.xml', 'rb') as file_f:
            mock_m.get('http://oereblex.test.com/api/geolinks/1500.xml', content=file_f.read())
        documents = XML(version=SCHEMA.V1_2_1).from_url('http://oereblex.test.com/api/geolinks/1500.xml')
    assert len(documents) == 5
    assert documents[0].municipality == 'Testgemeinde'
    assert documents[1].municipality is None


def test_schema_version_1_2_2():
    with requests_mock.mock() as mock_m:
        with open('tests/resources/geolink_v1.2.2.xml', 'rb') as file_f:
            mock_m.get('http://oereblex.test.com/api/geolinks/1500.xml', content=file_f.read())
        documents = XML(version=SCHEMA.V1_2_2).from_url('http://oereblex.test.com/api/geolinks/1500.xml')
    assert len(documents) == 5
    assert documents[0].index is None
    assert documents[-3].index == 1
    assert documents[-2].index == 2
    assert documents[-1].index == 3


def test_schema_version_1_2_2_prepublink():
    with requests_mock.mock() as mock_m:
        with open('tests/resources/prepublink_v1.2.2.xml', 'rb') as file_f:
            mock_m.get('http://oereblex.test.com/api/geolinks/1500.xml', content=file_f.read())
        documents = XML(version=SCHEMA.V1_2_2).from_url('http://oereblex.test.com/api/geolinks/1500.xml')
    assert len(documents) == 6
    assert documents[0].index is None
    assert documents[-3].index == 1
    assert documents[-2].index == 2
    assert documents[-1].index == 3


def test_schema_version_1_2_2_faulty_prepublink():
    with pytest.raises(xmlschema.XMLSchemaValidationError):
        with requests_mock.mock() as mock_m:
            with open('tests/resources/prepublink_v1.2.2_error_enactment_date.xml', 'rb') as file_f:
                mock_m.get('http://oereblex.test.com/api/geolinks/1500.xml', content=file_f.read())
            XML(version=SCHEMA.V1_2_2).from_url('http://oereblex.test.com/api/geolinks/1500.xml')


def test_schema_version_1_2_2_faulty_geolink():
    with pytest.raises(xmlschema.XMLSchemaValidationError):
        with requests_mock.mock() as mock_m:
            with open('tests/resources/geolink_v1.2.2_error_status.xml', 'rb') as file_f:
                mock_m.get('http://oereblex.test.com/api/geolinks/1500.xml', content=file_f.read())
            XML(version=SCHEMA.V1_2_2).from_url('http://oereblex.test.com/api/geolinks/1500.xml')


def test_schema_version_1_2_3():
    with requests_mock.mock() as mock_m:
        with open('tests/resources/geolink_v1.2.3.xml', 'rb') as file_f:
            mock_m.get('http://oereblex.test.com/api/geolinks/1500.xml', content=file_f.read())
        documents = XML(version=SCHEMA.V1_2_3).from_url('http://oereblex.test.com/api/geolinks/1500.xml')
    assert len(documents) == 5
    assert documents[0].index is None
    assert documents[-3].index == 1
    assert documents[-2].index == 2
    assert documents[-1].index == 3


def test_schema_version_1_2_3_prepublink():
    with requests_mock.mock() as mock_m:
        with open('tests/resources/prepublink_v1.2.3.xml', 'rb') as file_f:
            mock_m.get('http://oereblex.test.com/api/geolinks/1500.xml', content=file_f.read())
        documents = XML(version=SCHEMA.V1_2_3).from_url('http://oereblex.test.com/api/geolinks/1500.xml')
    assert len(documents) == 6
    assert documents[0].index is None
    assert documents[-3].index == 1
    assert documents[-2].index == 2
    assert documents[-1].index == 3


def test_schema_version_1_2_3_faulty_prepublink():
    with pytest.raises(xmlschema.XMLSchemaValidationError):
        with requests_mock.mock() as mock_m:
            with open('tests/resources/prepublink_v1.2.3_error_enactment_date.xml', 'rb') as file_f:
                mock_m.get('http://oereblex.test.com/api/geolinks/1500.xml', content=file_f.read())
            XML(version=SCHEMA.V1_2_3).from_url('http://oereblex.test.com/api/geolinks/1500.xml')


def test_schema_version_1_2_3_faulty_geolink():
    with pytest.raises(xmlschema.XMLSchemaValidationError):
        with requests_mock.mock() as mock_m:
            with open('tests/resources/geolink_v1.2.3_error_status.xml', 'rb') as file_f:
                mock_m.get('http://oereblex.test.com/api/geolinks/1500.xml', content=file_f.read())
            XML(version=SCHEMA.V1_2_3).from_url('http://oereblex.test.com/api/geolinks/1500.xml')


def test_schema_version_1_2_4():
    """
    test of schema version 1.2.4
    """
    with requests_mock.mock() as mock_m:
        with open('tests/resources/geolink_v1.2.4.xml', 'rb') as file_f:
            mock_m.get('http://oereblex.test.com/api/geolinks/1500.xml', content=file_f.read())
        documents = XML(version=SCHEMA.V1_2_4).from_url('http://oereblex.test.com/api/geolinks/1500.xml')
    assert len(documents) == 5
    assert documents[0].index is None
    assert documents[-3].index == 1
    assert documents[-2].index == 2
    assert documents[-1].index == 3


def test_schema_version_1_2_4_prepublink():
    """
    test of schema version 1.2.4: prepublink
    """
    with requests_mock.mock() as mock_m:
        with open('tests/resources/prepublink_v1.2.4.xml', 'rb') as file_f:
            mock_m.get('http://oereblex.test.com/api/geolinks/1500.xml', content=file_f.read())
        documents = XML(version=SCHEMA.V1_2_4).from_url('http://oereblex.test.com/api/geolinks/1500.xml')
    assert len(documents) == 6
    assert documents[0].index is None
    assert documents[-3].index == 1
    assert documents[-2].index == 2
    assert documents[-1].index == 3


def test_schema_version_1_2_4_faulty_prepublink():
    """
    test of schema version 1.2.4: faulty prepublink
    """
    with pytest.raises(xmlschema.XMLSchemaValidationError):
        with requests_mock.mock() as mock_m:
            with open('tests/resources/prepublink_v1.2.4_error_enactment_date.xml', 'rb') as file_f:
                mock_m.get('http://oereblex.test.com/api/geolinks/1500.xml', content=file_f.read())
            XML(version=SCHEMA.V1_2_4).from_url('http://oereblex.test.com/api/geolinks/1500.xml')


def test_schema_version_1_2_4_faulty_geolink():
    """
    test of schema version 1.2.4: faulty geolink
    """
    with pytest.raises(xmlschema.XMLSchemaValidationError):
        with requests_mock.mock() as mock_m:
            with open('tests/resources/geolink_v1.2.4_error_status.xml', 'rb') as file_f:
                mock_m.get('http://oereblex.test.com/api/geolinks/1500.xml', content=file_f.read())
            XML(version=SCHEMA.V1_2_4).from_url('http://oereblex.test.com/api/geolinks/1500.xml')


def test_schema_version_1_2_5():
    """
    test of schema version 1.2.5
    """
    with requests_mock.mock() as mock_m:
        with open('tests/resources/geolink_v1.2.5.xml', 'rb') as file_f:
            mock_m.get('http://oereblex.test.com/api/geolinks/1500.xml', content=file_f.read())
        documents = XML(version=SCHEMA.V1_2_5).from_url('http://oereblex.test.com/api/geolinks/1500.xml')
    assert len(documents) == 12
    assert documents[0].index is None
    assert documents[0].id == '400'
    assert documents[-11].id == '390'
    assert documents[-10].id == '17'
    assert documents[-9].id == '18'
    assert documents[-8].id == '34'
    assert documents[-7].id == '19'
    assert documents[-6].id == '23'
    assert documents[-5].id == '24'
    assert documents[-4].id == '5'
    assert documents[-3].id == '11'
    assert documents[-2].id == '13'
    assert documents[-1].id == '14'


def test_schema_version_1_2_5_ml():
    """
    test of schema version 1.2.5
    """
    with requests_mock.mock() as mock_m:
        with open('tests/resources/geolink_v1.2.5_ml.xml', 'rb') as file_f:
            mock_m.get('http://oereblex.test.com/api/geolinks/1500.xml', content=file_f.read())
        documents = XML(version=SCHEMA.V1_2_5).from_url('http://oereblex.test.com/api/geolinks/1500.xml')
    assert len(documents) == 36
    assert documents[0].id == '400'
    assert documents[-11].id == '390'
    assert documents[-10].id == '17'
    assert documents[-9].id == '18'
    assert documents[-8].id == '34'
    assert documents[-7].id == '19'
    assert documents[-6].id == '23'
    assert documents[-5].id == '24'
    assert documents[-4].id == '5'
    assert documents[-3].id == '11'
    assert documents[-2].id == '13'
    assert documents[-1].id == '14'


def test_default_version_with_locale():
    with requests_mock.mock() as mock_m:
        with open('tests/resources/geolink_v1.2.1.xml', 'rb') as file_f:
            mock_m.get('http://oereblex.test.com/api/geolinks/1500.xml?locale=fr', content=file_f.read())
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


@pytest.mark.parametrize('docs,exp_docs_filtered', [
    (
        [
            Document([], id=1, language_link='de'),
            Document([], id=1, language_link='fr'),
            Document([], id=2, language_link='de')],
        [
            Document([], id=1, language_link='de'),
            Document([], id=1, language_link='fr'),
            Document([], id=2, language_link='de')]
    ),
    (
        [
            Document([], id=2, language_link='de'),
            Document([], id=1, language_link='fr'),
            Document([], id=1, language_link='de'),
            Document([], id=2, language_link='fr'),
            Document([], id=2, language_link='de')
        ],
        [
            Document([], id=1, language_link='de'),
            Document([], id=1, language_link='fr'),
            Document([], id=2, language_link='de'),
            Document([], id=2, language_link='fr')
        ]
    ),
    (
        [
            Document([], id=2, language_link='de'),
            Document([], id=1, language_link=None),
            Document([], id=2, language_link=None),
            Document([], id=1, language_link=None)
        ],
        [
            Document([], id=2, language_link='de'),
            Document([], id=1, language_link=None),
            Document([], id=2, language_link=None),
        ]
    )
])
def test_filter_duplicated_documents(docs, exp_docs_filtered):

    result = XML()._filter_duplicated_documents(docs)

    result = sorted(result, key=lambda x: (x.id, (x.language_link is None, x.language_link)), reverse=False)

    exp_docs_filtered = sorted(
        exp_docs_filtered, key=lambda x: (x.id, (x.language_link is None, x.language_link)), reverse=False)

    assert [[x.id, x.language_link] for x in result] == \
        [[x.id, x.language_link] for x in exp_docs_filtered]


@pytest.fixture()
def provide_geolinks_el():
    geolinks_el = Element('geolinks', attrib={'language': 'de'})
    SubElement(geolinks_el, 'document', attrib={'id': '1'})
    SubElement(geolinks_el, 'document', attrib={'id': '2'})
    yield geolinks_el


def test_process_geolinks_prepublinks(provide_geolinks_el):
    with patch.object(
        XML,
        '_process_single_document',
        return_value=Document([], id=1, language_link='de')
    ):
        result = XML()._process_geolinks_prepublinks(provide_geolinks_el)
        assert all([isinstance(x, Document) for x in result])
        assert len(result) == 2


@pytest.fixture()
def provide_document_el():
    document_el = Element(
        'document',
        attrib={
            'language': 'de',
            'authority': 'Gemeindeverwaltung',
            'authority_url': 'https://www.domleschg.ch',
            'category': 'main',
            'doctype': 'decree',
            'enactment_date': '2012-06-22',
            'federal_level': 'Gemeinde',
            'id': '400',
            'language': 'de',
            'municipality': 'Domleschg',
            'number': '12.GDEf1',
            'subtype': 'Domleschg (Paspels) 3634',
            'title': 'Quartierplan Radiend',
            'type': 'Nutzungsplanung - Quartierplanverfahren'
        }
    )
    SubElement(document_el, 'file', attrib={
        'category': 'main',
        'description': '3634_B_QP_Radiend_Platzhalter.pdf',
        'href': '/api/attachments/1123',
        'title': '3634_B_QP_Radiend_Platzhalter.pdf'
    })
    SubElement(document_el, 'file', attrib={
        'category': 'additional',
        'description': '',
        'href': '/api/attachments/6027',
        'title': 'PlatzhalterFehlendeDokumente.pdf'
    })

    yield document_el


def test_process_single_document(provide_document_el):
    document = XML()._process_single_document(provide_document_el, language_link='de')
    assert document.id == '400'
    assert document.language_link == 'de'
    assert document.files[1].title == 'PlatzhalterFehlendeDokumente.pdf'
