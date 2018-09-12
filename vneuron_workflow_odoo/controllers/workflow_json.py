# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import http
from odoo.http import request
import odoo
import logging

_logger = logging.getLogger(__name__)
from odoo.addons.web.controllers.main import DataSet


class WorkflowController(DataSet):

    @http.route('/web/dataset/exec_workflow', type='json', auth="user")
    def exec_workflow(self, model, id, signal):
        _logger.info('----- -------WorkflowController-------act_open model %s:',model)
        _logger.info('----- -------WorkflowController-------act_open id %s:',id)
        request.session.check_security()
        return request.env[model].browse(id).signal_workflow(signal)[id]