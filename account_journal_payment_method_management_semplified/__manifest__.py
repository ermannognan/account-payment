# -*- coding: utf-8 -*-

{
    'name': 'Account Journal Payment Method Management Simplified',
    'version': '1.0',
    'category': 'Sale Extensions',
    'description': """
Tech Plus Sale.
""",
    'author': 'Ermanno Gnan',
    'website': '',
    'summary': """
        This module adds a simplified menu to manage payment methods ad allow to
        create a new payment method easily.
        """,
    'sequence': 1,
    'depends': [
        'account',
    ],
    'data': [
        'views/account_journal_view.xml',
        'views/menu_view.xml',
    ],
    'demo': [
    ],
    'test': [
    ],
    'qweb': [
    ],
    'installable': True,
    'auto_install': True,
}
