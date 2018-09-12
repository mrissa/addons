# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Student Exam',
    'version': '11.0',
    'category': 'Human Resources',
    'author': 'IP-TECH',
    'summary': '',
    'description': """
Student Exam Management
==========================
    """,
    'website': '',
    'images': [],
    'depends': [
        'etablissement',
        'student'
    ],
    'data': [

        'views/student_exam_view.xml',
    ],
    'demo': [
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
    'qweb': [],
}
