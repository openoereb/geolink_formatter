# -*- coding: utf-8 -*-


class HTML(object):
    def __init__(self):
        """Creates a new HTML formatter."""
        pass

    def format(self, documents):
        """Formats a list of :obj:`geolink_formatter.entity.Document` instances as HTML list.

        Args:
            documents (list[geolink_formatter.entity.Document]): The list of documents to be formatted.

        Returns:
            str: An HTML formatted string containing the documents as HTML list.

        """
        return '<ul class="geolink-formatter">{documents}</ul>'.format(
            documents=''.join([self.__format_document__(document) for document in documents])
        )

    def __format_document__(self, document):
        """Formats a :obj:`geolink_formatter.entity.Document` instance as HTML list item.

        Args:
            document (geolink_formatter.entity.Document): The document to be formatted.

        Returns:
            str: The document formatted as HTML list item.

        """
        return '<li class="geolink-formatter-document">{title}{files}</li>'.format(
            title=document.title,
            files=self.__format_files__(document.files)
        )

    def __format_files__(self, files):
        """Formats a list of :obj:`geolink_formatter.entity.File` instances as HTML list.

        Args:
            files (list[geolink_formatter.entity.File]): The list of files to be formatted.

        Returns:
            str: The files formatted as HTML list.

        """
        return '<ul class="geolink-formatter">{files}</ul>'.format(
            files=''.join([self.__format_file__(file) for file in files])
        )

    def __format_file__(self, file):
        """Formats a :obj:`geolink_formatter.entity.File` instance as HTML list item.

        Args:
            file (geolink_formatter.entity.File): The file to be formatted.

        Returns:
            str: The file formatted as HTML list item.

        """
        return '<li class="geolink-formatter-file"><a href="{href}" target="_blank">{title}</a></li>'.format(
            title=file.title,
            href=file.href
        )