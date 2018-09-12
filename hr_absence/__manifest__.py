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
    'name': 'Absence Management',
    'version': '11.0',
    'category': 'Generic Modules/Human Resources',
    'author': "IP-TECH",
    'license': 'AGPL-3',
    'description': """
		Ce module permet la gestion des absences et des suspensions des employés .
    """,
    'depends': [
        'hr','base_config','hr_assignment','hr_recrutement'
    ],
    'data': [
        #'security/ir.model.access.csv',
        #'wizard/import_employee_wizard.xml',
        'data/absence_sequence.xml',
        'views/hr_absence_view.xml',
    ],
    'installable': True,
}
