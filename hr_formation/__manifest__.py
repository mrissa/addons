# -*- encoding: utf-8 -*-
###############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2013 Savoir-faire Linux (<http://www.savoirfairelinux.com>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program. If not, see <http://www.gnu.org/licenses/>.
#
###############################################################################

{
    "name": "Training Management",
    'version': '11.0',
    'author': 'IP-TECH',
    "category": "Human Resources",
    "description": """
		Ce module permet la gestion des formations contenues des employés .
    """,
    "license": "AGPL-3",
    "depends": [
        "hr",
        "event",
        "hr_recrutement"
    ],
    'data': [
        #'security/ir.model.access.csv',
        'views/hr_formation_view.xml',
    ],
    "demo": [],
    "test": [],
    'installable': True,
    "auto_install": False,
    "images": [],
}
