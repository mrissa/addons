# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Etablissement',
    'version': '11.à',
    'author': 'IP-TECH',
    'description': """
Gestion des Etablissements
==========================
Application de gestion des Etablissements.
La gestion des Etablissements est en rapport avec la gestion des locaux,
des classes et du materiel fixe attribue aux classes en dehors des consommables.

    """,
    'website': '',
    'images': [
        'static/src/img/default_image.png',
    ],
    'depends': [
        'mail',
        'product',
        'student',
        'base_config',
        'web',

    ],
    'data': [
        'security/etablissement_security.xml',
        'security/ir.model.access.csv',
        'data/etablissement_sequence.xml',
        'views/etablissement.xml',
        'views/building.xml',
        'views/educational_structure.xml',
        'views/product_view.xml',
        'views/menu.xml',
        'static/src/xml/hide_menu.xml',
    ],
    'demo': [
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
    'qweb': [],
}
