# -*- coding: utf-8 -*-

def filter_duplicated_documents(documents):
    """
    Filters duplicated documents.

    Args:
        documents (list[geolink_formatter.entity.Document]): list of documents

    Returns:
        list[geolink_formatter.entity.Document]: filtered list of documents
    """
    documents_filtered = list()
    for document in documents:
        if (
                [document.id, document.language_link]
                not in [[doc.id, doc.language_link] for doc in documents_filtered]
        ):
            documents_filtered.append(document)
    return documents_filtered
