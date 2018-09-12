# -*- coding: utf-8 -*-
{
    'name': 'Referentiel',
    'version': '11.1',
    'author': 'IP-TECH',
    'summary': 'Configuration de Base',
    'description': """
Configuration de base
==========================
Ce module permet la consultation du referentiel Wilaya , Mougathaa, commune, des DREN, des Annee scolaire, etc.
    """,
    'website': '',
    'images': [
        'static/src/img/default_image.png',
    ],
    'depends': ['base','mail','hr_recruitment','calendar','vneuron_workflow_odoo'],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/base_views.xml',
        'views/menu.xml',
        'views/year_scolarity_workflow.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
