# -*- coding: utf-8 -*-
{
    'name': 'Scolarity',
    'version': '11.1',
    'author': 'IP-TECH',
    'summary': '',
    'description': """
    Ce modulepermet la gestion de la scolarité fondamentale et secndaire
    """,
    'website': '',
    'images': [],
     'depends': ['base_config','hr_assignment','etablissement','student','report_xlsx'],
 
    'data': [
        'views/scolarity_views.xml',
        'views/menu.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
