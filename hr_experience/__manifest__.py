# -*- coding: utf-8 -*-
# Copyright 2013 Savoir-faire Linux (<http://www.savoirfairelinux.com>).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Experience Management",
    'version': '11.0',
    'author': 'IP-TECH',
    'description': """
		Ce module permet la gestion des experiences des employés .
    """,
    "license": "AGPL-3",
    "category": "Human Resources",
    "depends": ["hr", "hr_recrutement"],
    "data": [
        "security/ir.model.access.csv",
        "security/hr_security.xml",
        "views/hr_employee_view.xml",
        "views/hr_academic_view.xml",
        "views/hr_professional_view.xml",
        "views/hr_certification_view.xml",
    ],
    'installable': True
}
