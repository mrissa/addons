# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import werkzeug

from odoo import http
from odoo.http import request
import odoo

class WebsiteDOCUrl(http.Controller):
    @http.route('/doc/api/v1', type='http', auth="public", website=True)
    def website_doc(self):
        try:
            request.website.get_template('vneuron_restful_api.rest_info').name
        except Exception as e:
            return request.env['ir.http']._handle_exception(e, 404)
        Module = request.env['ir.module.module'].sudo()
        apps = Module.search([('state', '=', 'installed'), ('application', '=', True)])
        modules = Module.search([('state', '=', 'installed'), ('application', '=', False)])
        
        Modele = request.env['ir.model'].sudo()
        modeles = Modele.search([('state', '=', 'base'), ('transient', '=', False)])
        values = {
            'apps': apps,
            'modules': modules,
            'modeles':modeles,
            'version': odoo.service.common.exp_version()
        }
        return request.render('vneuron_restful_api.rest_info', values)