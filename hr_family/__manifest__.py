{
    'name': 'Employee Family Information',
    'version': '11.0',
    'author': 'IP-TECH',
    'description': """
		Ce module permet la gestion des données de la famille pour chaque employé .
    """,
    'category': 'Generic Modules/Human Resources',
    'license': 'AGPL-3',
    'depends': [
        'hr','hr_recrutement'
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/hr_children.xml',
        'views/hr_employee.xml',
    ],
    'installable': True,
}
