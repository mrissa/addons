# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Student',
    'version': '11.0',
    'author': 'IP-TECH',
    'summary': 'Students Details',
    'description': """
        Gestion des Elèves : Application de gestion des Eleves.
    """,
    'images': [
        'static/src/img/default_image.png',
    ],
    'depends': [
        'mail','base','base_config',
    ],
    'data': [
        #'security/hr_security.xml',
        #'security/ir.model.access.csv',
        'wizard/import_student_wizard.xml',
        'data/hr_student_sequence.xml',
        'views/student_view.xml',
        'student_menu.xml',
        'report.xml',
        'views/report_student.xml',
    ],
    'demo': [
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
    'qweb': [],
}
