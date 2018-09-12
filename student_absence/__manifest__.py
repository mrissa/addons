# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Student Absences',
    'version': '11.0',
    'category': 'Human Resources',
    'author': 'IP-TECH',
    'summary': '',
    'description': """
Student Absences Management
==========================
    """,
    'website': '',
    'images': [],
    'depends': [
        'student',
    ],
    'data': [

        'views/student_absence_view.xml',
    ],
    'demo': [
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
    'qweb': [],
}
