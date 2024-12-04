# -*- coding: utf-8 -*-
import pytest
from geolink_formatter.utils import filter_duplicated_documents
from geolink_formatter.entity import Document


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

    result = filter_duplicated_documents(docs)

    result = sorted(result, key=lambda x: (x.id, (x.language_link is None, x.language_link)), reverse=False)

    exp_docs_filtered = sorted(
        exp_docs_filtered, key=lambda x: (x.id, (x.language_link is None, x.language_link)), reverse=False)

    assert [[x.id, x.language_link] for x in result] == \
        [[x.id, x.language_link] for x in exp_docs_filtered]
