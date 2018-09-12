# -*- coding: utf-8 -*-
# Copyright 2013 Savoir-faire Linux (<http://www.savoirfairelinux.com>).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Evaluation Management",
    'version': '11.0',
    'author': 'IP-TECH',
    'description': """
		Ce module permet la gestion des évaluations pédagogiques et administratives des employés .
    """,
    "license": "AGPL-3",
    "category": "Human Resources",
    "depends": ["hr", "hr_recrutement"],
    "data": [
        "views/hr_evaluation_view.xml",
    ],
    'installable': True
}
