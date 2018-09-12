# -*- coding: utf-8 -*-
# Copyright 2013 Savoir-faire Linux
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Skill Management",
    "version": "11.0",
    "category": "Human Resources",
    "license": "AGPL-3",
    "author": "IP-TECH",
    'description': """
		Ce module permet la gestion des disciplines des employés .
    """,
    "depends": ["hr"],
    'data': [
        "security/ir.model.access.csv",
        "views/hr_skill.xml",
        "views/hr_employee.xml",

    ],
    'installable': True,
}
