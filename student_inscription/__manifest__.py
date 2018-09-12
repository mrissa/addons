# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Student inscription',
    'version': '11.0',
    'category': 'Human Resources',
    'author': 'IP-TECH',
    'summary': '',
    'description': """
Student Inscription Management
==========================
    """,
    'website': '',
    'images': [],
    'depends': [
        'student',
    ],
    'data': [
        'data/insc_sequence.xml',
        #'wizard/import_insc_wizard.xml',
        'views/student_inscription_view.xml',
        #'views/student_affectation_view.xml',
        
    ],
    'demo': [
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
    'qweb': [],
}
