# Copyright 2016 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'vneuron_workflow_odoo',
    'summary': """
        Vneuron workflow for odoo 11 """,
    'version': '11.0',
    'description': 'Ce module permet la gestion du workflow',
    'license': 'AGPL-3',
    'author': ' IP-TECH',
    'depends': [
        'base',
         
    ],
    'data': [
        'views/workflow_view.xml',
        'views/assets.xml',
        'security/ir.model.access.csv',
    ],
     
}
