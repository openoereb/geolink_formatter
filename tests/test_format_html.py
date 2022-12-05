# -*- coding: utf-8 -*-
from geolink_formatter.format import HTML


def test_format_with_file(documents):
    formatter = HTML()
    html = formatter.format(documents)
    assert html == '<ul class="geolink-formatter">' \
                   '<li class="geolink-formatter-document">Document with file (15.01.2017) ' \
                   '<ul class="geolink-formatter">' \
                   '<li class="geolink-formatter-file">' \
                   '<a href="http://www.example.com/test.pdf" target="_blank">Test file</a>' \
                   '</li>' \
                   '</ul>' \
                   '</li>' \
                   '</ul>'


def test_format_with_file_prepublink(prepublink_documents):
    formatter = HTML()
    html = formatter.format(prepublink_documents)
    assert html == '<ul class="geolink-formatter">' \
                   '<li class="geolink-formatter-document">Document with file (15.01.2017) ' \
                   '<ul class="geolink-formatter">' \
                   '<li class="geolink-formatter-file">' \
                   '<a href="http://www.example.com/test.pdf" target="_blank">Test file</a>' \
                   '</li>' \
                   '</ul>' \
                   '</li>' \
                   '</ul>'


def test_format_without_file(document_without_file):
    formatter = HTML()
    html = formatter.format(document_without_file)
    assert html == '<ul class="geolink-formatter">' \
                   '<li class="geolink-formatter-document">Document without file (15.01.2017) ' \
                   '</li>' \
                   '</ul>'


def test_format_archived(document_archived):
    formatter = HTML()
    html = formatter.format(document_archived)
    assert html == '<ul class="geolink-formatter">' \
                   '<li class="geolink-formatter-document">' \
                   '<strike>Archived document (15.01.2017)</strike> (01.01.2019)' \
                   '</li>' \
                   '</ul>'


def test_format_archived_prepublink(prepublink_document_archived):
    formatter = HTML()
    html = formatter.format(prepublink_document_archived)
    assert html == '<ul class="geolink-formatter">' \
                   '<li class="geolink-formatter-document">' \
                   '<strike>Archived document (15.01.2017)</strike> (01.01.2019)' \
                   '</li>' \
                   '</ul>'
