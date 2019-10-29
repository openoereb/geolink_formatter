# -*- coding: utf-8 -*-
import pytest

from geolink_formatter import GeoLinkFormatter


def test_init():
    formatter = GeoLinkFormatter(host_url='http://example.com', dtd_validation=True)
    assert isinstance(formatter, GeoLinkFormatter)
    assert formatter._host_url == 'http://example.com'
    assert formatter._dtd_validation


def test_html_string():
    formatter = GeoLinkFormatter()
    xml = """<?xml version="1.0" encoding="utf-8"?>
        <geolinks>
            <document authority='Example Authority' authority_url='http://www.example.com'
                      category='main' doctype='decree' enactment_date='1999-10-18'
                      federal_level='Gemeinde' id='1' subtype='Example Subtype' title='Example Document'
                      type='Example Type'>
                <file category='main' href='/api/attachments/1' title='example1.pdf'></file>
            </document>
        </geolinks>
        """
    html = formatter.html(xml.encode('utf-16be'))
    assert html == u'<ul class="geolink-formatter">' \
                   u'<li class="geolink-formatter-document">' \
                   u'Example Type (Example Subtype): Example Document (18.10.1999) ' \
                   u'<ul class="geolink-formatter">' \
                   u'<li class="geolink-formatter-file">' \
                   u'<a href="/api/attachments/1" target="_blank">example1.pdf</a>' \
                   u'</li>' \
                   u'</ul>' \
                   u'</li>' \
                   u'</ul>'


def test_html_url(mock_request):
    formatter = GeoLinkFormatter()
    with mock_request():
        html = formatter.html('http://oereblex.test.com/api/geolinks/1500.xml')
    assert html == u'<ul class="geolink-formatter"><li class="geolink-formatter-document">' \
                   u'Sondernutzungsplan (Gestaltungsplan): Tiefkühllager (27.03.2001) ' \
                   u'<ul class="geolink-formatter">' \
                   u'<li class="geolink-formatter-file">' \
                   u'<a href="/api/attachments/4735" target="_blank">2918-E-1.pdf</a>' \
                   u'</li>' \
                   u'<li class="geolink-formatter-file">' \
                   u'<a href="/api/attachments/4736" target="_blank">2918-P-1.pdf</a>' \
                   u'</li>' \
                   u'<li class="geolink-formatter-file">' \
                   u'<a href="/api/attachments/4737" target="_blank">2918-P-2.pdf</a>' \
                   u'</li>' \
                   u'<li class="geolink-formatter-file">' \
                   u'<a href="/api/attachments/4738" target="_blank">2918-P-3.pdf</a>' \
                   u'</li>' \
                   u'<li class="geolink-formatter-file">' \
                   u'<a href="/api/attachments/4739" target="_blank">2918-S-1.pdf</a>' \
                   u'</li>' \
                   u'</ul>' \
                   u'</li>' \
                   u'<li class="geolink-formatter-document">' \
                   u'Planungs- und Baugesetz (01.04.2017) ' \
                   u'<ul class="geolink-formatter">' \
                   u'<li class="geolink-formatter-file">' \
                   u'<a href="http://www.rechtsbuch.tg.ch/frontend/versions/pdf_file_with_annex/1379?' \
                   u'locale=de" target="_blank">700.pdf</a>' \
                   u'</li>' \
                   u'</ul>' \
                   u'</li>' \
                   u'<li class="geolink-formatter-document">' \
                   u'Bundesgesetz über die Raumplanung (01.01.2016) ' \
                   u'<ul class="geolink-formatter">' \
                   u'<li class="geolink-formatter-file">' \
                   u'<a href="http://www.lexfind.ch/dtah/136884/2" target="_blank">700.de.pdf</a>' \
                   u'</li>' \
                   u'</ul>' \
                   u'</li>' \
                   u'<li class="geolink-formatter-document">' \
                   u'Verordnung des Regierungsrates zum Planungs- und Baugesetz und zur Interkantonalen ' \
                   u'Vereinbarung über die Harmonisierung der Baubegriffe (05.11.2016) ' \
                   u'<ul class="geolink-formatter">' \
                   u'<li class="geolink-formatter-file">' \
                   u'<a href="http://www.rechtsbuch.tg.ch/frontend/versions/pdf_file_with_annex/1319?' \
                   u'locale=de" target="_blank">700.1.pdf</a>' \
                   u'</li>' \
                   u'</ul>' \
                   u'</li>' \
                   u'</ul>'


def test_html_invalid_source():
    with pytest.raises(TypeError):
        GeoLinkFormatter().html(1)
