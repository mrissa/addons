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
    'name': 'Asignment Management',
    'version': '11.0',
    'category': 'Generic Modules/Human Resources',
    'author': "IP-TECH",
    'description': """
		Ce module permet la gestion des affectations des employés .
    """,
    'license': 'AGPL-3',
    'depends': [
        'hr','base','base_config','hr_recrutement'
    ],
    'data': [
        #'security/ir.model.access.csv',
        'wizard/import_employee_wizard.xml',
        'views/hr_assignment_view.xml',
        'data/assignement_sequence.xml',

    ],
    'installable': True,
}
