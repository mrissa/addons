# -*- coding: utf-8 -*-
# © 2011, 2013 Michael Telahun Makonnen <mmakonnen@gmail.com>
# © 2016 OpenSynergy Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    'name': 'Employee ID',
    'version': '11.0',
    'author': 'IP-TECH',
    'license': 'AGPL-3',
    'category': 'Generic Modules/Human Resources',
    'depends': [
        'hr','employee'
    ],
    'data': [
        'views/res_config_views.xml',
        'views/hr_employee_views.xml',
        'data/hr_employee_sequence.xml',
    ],
    'installable': True,
}
