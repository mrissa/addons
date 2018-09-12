import odoo
from odoo import api, fields, models, tools, SUPERUSER_ID, _
from odoo.exceptions import MissingError, UserError, ValidationError, AccessError
from odoo.tools.safe_eval import safe_eval, test_python_expr
from odoo.tools import pycompat
from odoo.http import request
import os
from  odoo.addons.vneuron_workflow_odoo import workflow
import base64
from collections import defaultdict
import datetime
import dateutil
import logging
import time

from pytz import timezone

_logger = logging.getLogger(__name__)


class IrActions2Server(models.Model):
    
    _name = 'ir.actions.server'
    _inherit = 'ir.actions.server'
    _table = 'ir_act_server'
    
     ##########################
    # Client Action
    menu_ir_values_id = fields.Many2one('ir.values', string='More Menu entry', readonly=True,
                                        help='More menu entry.', copy=False)
    # Client Action
    action_id = fields.Many2one('ir.actions.actions', string='Client Action',
                                help="Select the client action that has to be executed.")
    # Workflow signal
    use_relational_model = fields.Selection([('base', 'Use the base model of the action'),
                                             ('relational', 'Use a relation field on the base model')],
                                            string='Relational Target Model', default='base', required=True)
    wkf_transition_id = fields.Many2one('workflow.transition', string='Signal to Trigger',
                                        help="Select the workflow signal to trigger.")
    wkf_model_id = fields.Many2one('ir.model', string='Target Model',
                                   help="The model that will receive the workflow signal. Note that it should have a workflow associated with it.")
    wkf_model_name = fields.Char(string='Target Model Name', related='wkf_model_id.model', store=True, readonly=True)
    wkf_field_id = fields.Many2one('ir.model.fields', string='Relation Field',
                                   oldname='trigger_obj_id', help="The field on the current object that links to the target object record (must be a many2one, or an integer field with the record ID)")
     # Create/Copy/Write
    use_create = fields.Selection([('new', 'Create a new record in the Base Model'),
                                   ('new_other', 'Create a new record in another model'),
                                   ('copy_current', 'Copy the current record'),
                                   ('copy_other', 'Choose and copy a record in the database')],
                                  string="Creation Policy", default='new', required=True)
     
    ref_object = fields.Reference(string='Reference record', selection='_select_objects', oldname='copy_object')
    link_new_record = fields.Boolean(string='Attach the new record',
                                     help="Check this if you want to link the newly-created record "
                                          "to the current record on which the server action runs.")
     
    use_write = fields.Selection([('current', 'Update the current record'),
                                  ('expression', 'Update a record linked to the current record using python'),
                                  ('other', 'Choose and Update a record in the database')],
                                 string='Update Policy', default='current', required=True)
    write_expression = fields.Char(string='Expression', oldname='write_id',
                                   help="Provide an expression that, applied on the current record, gives the field to update.")
    
    ############################
    
    @api.model
    def _get_states(self):
        """ Override me in order to add new states in the server action. Please
        note that the added key length should not be higher than already-existing
        ones. """
        return [('code', 'Execute Python Code'),
                ('trigger', 'Trigger a Workflow Signal'),
                ('client_action', 'Run a Client Action'),
                ('object_create', 'Create or Copy a new Record'),
                ('object_write', 'Write on a Record'),
                ('multi', 'Execute several actions')]
        
    @api.constrains('write_expression', 'model_id')
    def _check_write_expression(self):
        for record in self:
            if record.write_expression and record.model_id:
                correct, model_name, message = self._check_expression(record.write_expression, record.model_id)
                if not correct:
                    _logger.warning('Invalid expression: %s' % message)
                    raise ValidationError(_('Incorrect Write Record Expression'))
                
    state = fields.Selection([
        ('code', 'Execute Python Code'),
        ('trigger', 'Trigger a Workflow Signal'),
        ('client_action', 'Run a Client Action'),
        ('object_create', 'Create a new Record'),
        ('object_write', 'Update the Record'),
        ('multi', 'Execute several actions')], string='Action To Do',
        default='object_write', required=True,
        help="Type of server action. The following values are available:\n"
             "- 'Execute Python Code': a block of python code that will be executed\n"
             "- 'Create or Copy a new Record': create a new record with new values, or copy an existing record in your database\n"
             "- 'Write on a Record': update the values of a record\n"
             "- 'Execute several actions': define an action that triggers several other server actions\n"
             "- 'Add Followers': add followers to a record (available in Discuss)\n"
             "- 'Send Email': automatically send an email (available in email_template)")
    
     
   
    
    
    @api.onchange('model_id')
    def _onchange_model_id(self):
        """ When changing the action base model, reset workflow and crud config
        to ease value coherence. """
        self.use_create = 'new'
        self.use_write = 'current'
        self.use_relational_model = 'base'
        self.wkf_model_id = self.model_id
        self.wkf_field_id = False
        self.crud_model_id = self.model_id

    @api.onchange('use_relational_model', 'wkf_field_id')
    def _onchange_wkf_config(self):
        """ Update workflow type configuration

         - update the workflow model (for base (model_id) /relational (field.relation))
         - update wkf_transition_id to False if workflow model changes, to force
           the user to choose a new one
        """
        if self.use_relational_model == 'relational' and self.wkf_field_id:
            field = self.wkf_field_id
            self.wkf_model_id = self.env['ir.model'].search([('model', '=', field.relation)])
        else:
            self.wkf_model_id = self.model_id

    @api.onchange('wkf_model_id')
    def _onchange_wkf_model_id(self):
        """ When changing the workflow model, update its stored name also """
        self.wkf_transition_id = False

    @api.onchange('use_create', 'use_write', 'ref_object')
    def _onchange_crud_config(self):
        """ Wrapper on CRUD-type (create or write) on_change """
        if self.state == 'object_create':
            self._onchange_create_config()
        elif self.state == 'object_write':
            self._onchange_write_config()

    def _onchange_create_config(self):
        """ When changing the object_create type configuration:

         - `new` and `copy_current`: crud_model_id is the same as base model
         - `new_other`: user choose crud_model_id
         - `copy_other`: disassemble the reference object to have its model
         - if the target model has changed, then reset the link field that is
           probably not correct anymore
        """
        crud_model_id = self.crud_model_id

        if self.use_create == 'new':
            self.crud_model_id = self.model_id
        elif self.use_create == 'new_other':
            pass
        elif self.use_create == 'copy_current':
            self.crud_model_id = self.model_id
        elif self.use_create == 'copy_other' and self.ref_object:
            ref_model = self.ref_object._name
            self.crud_model_id = self.env['ir.model'].search([('model', '=', ref_model)])

        if self.crud_model_id != crud_model_id:
            self.link_field_id = False

    def _onchange_write_config(self):
        """ When changing the object_write type configuration:

         - `current`: crud_model_id is the same as base model
         - `other`: disassemble the reference object to have its model
         - `expression`: has its own on_change, nothing special here
        """
        crud_model_id = self.crud_model_id

        if self.use_write == 'current':
            self.crud_model_id = self.model_id
        elif self.use_write == 'other' and self.ref_object:
            ref_model = self.ref_object._name
            self.crud_model_id = self.env['ir.model'].search([('model', '=', ref_model)])
        elif self.use_write == 'expression':
            pass

        if self.crud_model_id != crud_model_id:
            self.link_field_id = False
    
    @api.model
    def run_action_trigger(self, action, eval_context=None):
        """ Trigger a workflow signal, depending on the use_relational_model:

         - `base`: base_model_pool.signal_workflow(cr, uid, context.get('active_id'), <TRIGGER_NAME>)
         - `relational`: find the related model and object, using the relational
           field, then target_model_pool.signal_workflow(cr, uid, target_id, <TRIGGER_NAME>)
        """
        # weird signature and calling -> no self.env, use action param's
        record = action.env[action.model_id.model].browse(self._context['active_id'])
        if action.use_relational_model == 'relational':
            record = getattr(record, action.wkf_field_id.name)
            if not isinstance(record, models.BaseModel):
                record = action.env[action.wkf_model_id.model].browse(record)

        record.signal_workflow(action.wkf_transition_id.signal)

#     @api.model
#     def _get_eval_context(self, action=None):
#         """ Prepare the context used when evaluating python code, like the
#         python formulas or code server actions.
# 
#         :param action: the current server action
#         :type action: browse record
#         :returns: dict -- evaluation context given to (safe_)safe_eval """
#         def log(message, level="info"):
#             with self.pool.cursor() as cr:
#                 cr.execute("""
#                     INSERT INTO ir_logging(create_date, create_uid, type, dbname, name, level, message, path, line, func)
#                     VALUES (NOW() at time zone 'UTC', %s, %s, %s, %s, %s, %s, %s, %s, %s)
#                 """, (self.env.uid, 'server', self._cr.dbname, __name__, level, message, "action", action.id, action.name))
# 
#         eval_context = super(IrActionsServer, self)._get_eval_context(action=action)
#         model_name = action.model_id.sudo().model
#         model = self.env[model_name]
#         record = None
#         records = None
#         if self._context.get('active_model') == model_name and self._context.get('active_id'):
#             record = model.browse(self._context['active_id'])
#         if self._context.get('active_model') == model_name and self._context.get('active_ids'):
#             records = model.browse(self._context['active_ids'])
#         if self._context.get('onchange_self'):
#             record = self._context['onchange_self']
#         eval_context.update({
#             # orm
#             'env': self.env,
#             'model': model,
#             # Exceptions
#             'Warning': odoo.exceptions.Warning,
#             # record
#             'record': record,
#             'records': records,
#             # TODO: REMOVE ME IN saas-14
#             'workflow': workflow,
#             # deprecated use record, records
#             'object': record,
#             'obj': record,
#             # Deprecated use env or model instead
#             'pool': self.pool,
#             'cr': self._cr,
#             'context': self._context,
#             'user': self.env.user,
#             # helpers
#             'log': log,
#         })
#         return eval_context