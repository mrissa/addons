# -*- coding: utf-8 -*-
# Copyright 2016, 2017 Openworx
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

{
    "name": "Theme SIGE",
    'version': '11.1',
    'author': 'IP-TECH',
    "category": "Themes/Backend",
	"description": """
		Template Specifique pour SIGE .
    """,
	'images':[
        'images/screen.png'
	],
    "license": "LGPL-3",
    "installable": True,
    "depends": [
	'web_responsive',
    ],
    "data": [
        'views/assets.xml',
        'views/res_company_view.xml',
        'views/users.xml',
        #'views/sidebar.xml',
    ],
}

