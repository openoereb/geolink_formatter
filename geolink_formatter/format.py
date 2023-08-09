# -*- coding: utf-8 -*-
from datetime import date


class HTML(object):
    def __init__(self):
        """Creates a new HTML formatter."""
        pass

    @classmethod
    def format(cls, documents):
        """Formats a list of :obj:`geolink_formatter.entity.Document` instances as HTML list.

        Args:
            documents (list[geolink_formatter.entity.Document]): The list of documents to be formatted.

        Returns:
            str: An HTML formatted string containing the documents as HTML list.

        """
        return u'<ul class="geolink-formatter">{documents}</ul>'.format(
            documents=u''.join([cls.__format_document__(document) for document in documents])
        )

    @classmethod
    def __format_document__(cls, document):
        """Formats a :obj:`geolink_formatter.entity.Document` instance as HTML list item.

        Args:
            document (geolink_formatter.entity.Document): The document to be formatted.

        Returns:
            str: The document formatted as HTML list item.

        """
        if document.enactment_date:
            enactment_date = u'({0})'.format(document.enactment_date.strftime('%d.%m.%Y'))
        else:
            enactment_date = u''
        if document.abrogation_date and document.abrogation_date < date.today():
            files = u''
            strike_start = u'<strike>'
            strike_end = u'</strike>'
            abrogation_date = u'({0})'.format(document.abrogation_date.strftime('%d.%m.%Y'))
        else:
            files = cls.__format_files__(document.files)
            strike_start = u''
            strike_end = u''
            abrogation_date = u''
        subtype = u' ({0})'.format(document.subtype) if document.subtype else u''
        return u'<li class="geolink-formatter-document">' \
               u'{strike_start}{type}{title} {enactment_date}{strike_end} {abrogation_date}{files}' \
               u'</li>'.format(
                   type=u'{0}{1}: '.format(document.type or u'', subtype)
                   if document.type or document.subtype else u'',
                   title=document.title,
                   enactment_date=enactment_date,
                   files=files,
                   strike_start=strike_start,
                   strike_end=strike_end,
                   abrogation_date=abrogation_date
               )

    @classmethod
    def __format_files__(cls, files):
        """Formats a list of :obj:`geolink_formatter.entity.File` instances as HTML list.

        Args:
            files (list[geolink_formatter.entity.File]): The list of files to be formatted.

        Returns:
            str: The files formatted as HTML list.

        """
        if len(files) > 0:
            return u'<ul class="geolink-formatter">{files}</ul>'.format(
                files=u''.join([cls.__format_file__(file) for file in files])
            )
        return u''

    @classmethod
    def __format_file__(cls, file):
        """Formats a :obj:`geolink_formatter.entity.File` instance as HTML list item.

        The name displayed is the description, falling back on the title
        (containing the filename) if no description is present.

        Args:
            file (geolink_formatter.entity.File): The file to be formatted.

        Returns:
            str: The file formatted as HTML list item.

        """
        title = file.description
        if not title:
            title = file.title

        return u'<li class="geolink-formatter-file"><a href="{href}" target="_blank">{title}</a></li>'.format(
            title=title,
            href=file.href
        )
