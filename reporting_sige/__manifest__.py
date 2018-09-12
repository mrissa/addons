# -*- coding:utf-8 -*-
#
#
#    Copyright (C) 2011,2013 Michael Telahun Makonnen <mmakonnen@gmail.com>.
#    All Rights Reserved.
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#

{
    'name': 'Sige Reporting Analyse DATA',
    'version': '11.0',
    'category': 'Generic Modules/Human Resources',
    'author': "IP-TECH",
    'license': 'AGPL-3',
    'depends': [
        'hr','employee','hr_assignment',
    ],
    'data': [
        # 'security/security.xml',
        # 'security/ir.model.access.csv',
        # 'views/hr_report.xml',
        'report_etab/report_views.xml',
          'report_etab/etab_report_views.xml',
        'report_emp/report_views.xml',
        'report_emp/enpmloyee_report_views.xml',
        'report_emp/assignement_report_views.xml',
#         'report_emp/affectation_report_views.xml',
 
         'report_elve/report_views.xml',
        'report_elve/elve_report_views.xml',
        
        'report_demd/report_views.xml',
        'report_demd/demd_report_views.xml',
        
        'report_scola/report_views.xml',
        'report_scola/scola_report_views.xml',
        
    ],
    'installable': True,
}
