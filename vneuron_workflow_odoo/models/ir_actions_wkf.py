# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from werkzeug import urls

from odoo import api, fields, models
from odoo.http import request


class ServerWkfAction(models.Model):
    """ Add website option in server actions. """

    _name = 'ir.actions.server'
    _inherit = 'ir.actions.server'

    website_path = fields.Char('Website Path')