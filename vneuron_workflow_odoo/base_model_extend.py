from odoo import api, fields, models, _
import logging
from odoo.exceptions import ValidationError
_logger = logging.getLogger(__name__)
_schema = logging.getLogger(__name__ + '.schema')
_unlink = logging.getLogger(__name__ + '.unlink')
from odoo.models import BaseModel,api
from odoo.exceptions import AccessError, MissingError, ValidationError, UserError
 
class BaseModelExtend(models.AbstractModel):
        _name = 'basemodel.extend'
        @api.model_cr
        def _register_hook(self): 
                origin_ids = models.AbstractModel.ids
                origin_create = models.AbstractModel._create
                origin_write = models.AbstractModel._write
                originunlink = models.AbstractModel.unlink
                @api.model
                @api.returns('self', lambda value: value.id)
                def _create(self, vals):
                    result=[]
                    res = origin_create(self, vals) 
                    result.append(res)
                    self.create_workflow(result)
                    return res
                @api.model
                @api.returns('self', lambda value: value.id)
                def _write(self, vals):
                    result=[]
                    res = origin_write(self, vals)
                    self.step_workflow()
                    return res
                
                @api.model
                @api.returns('self', lambda value: value.id)
                @api.multi
                def unlink(self):
                    """ unlink()
            
                    Deletes the records of the current set
            
                    :raise AccessError: * if user has no unlink rights on the requested object
                                        * if user tries to bypass access rules for unlink on the requested object
                    :raise UserError: if the record is default property for other records
            
                    """
                    if not self:
                        return True
            
                    # for recomputing fields
                    self.modified(self._fields)
            
                    self._check_concurrency()
            
                    self.check_access_rights('unlink')
            
                    # Check if the records are used as default properties.
                    refs = ['%s,%s' % (self._name, i) for i in self.ids]
                    if self.env['ir.property'].search([('res_id', '=', False), ('value_reference', 'in', refs)]):
                        raise UserError(_('Unable to delete this document because it is used as a default property'))
            
                    # Delete the records' properties.
                    with self.env.norecompute():
                        self.env['ir.property'].search([('res_id', 'in', refs)]).unlink()
                        self.delete_workflow()
                        self.check_access_rule('unlink')
                        
                        cr = self._cr
                        Data = self.env['ir.model.data'].sudo().with_context({})
                        Defaults = self.env['ir.default'].sudo()
                        Attachment = self.env['ir.attachment']
            
                        for sub_ids in cr.split_for_in_conditions(self.ids):
                            query = "DELETE FROM %s WHERE id IN %%s" % self._table
                            cr.execute(query, (sub_ids,))
            
                            # Removing the ir_model_data reference if the record being deleted
                            # is a record created by xml/csv file, as these are not connected
                            # with real database foreign keys, and would be dangling references.
                            #
                            # Note: the following steps are performed as superuser to avoid
                            # access rights restrictions, and with no context to avoid possible
                            # side-effects during admin calls.
                            data = Data.search([('model', '=', self._name), ('res_id', 'in', sub_ids)])
                            if data:
                                data.unlink()
            
                            # For the same reason, remove the defaults having some of the
                            # records as value
                            Defaults.discard_records(self.browse(sub_ids))
            
                            # For the same reason, remove the relevant records in ir_attachment
                            # (the search is performed with sql as the search method of
                            # ir_attachment is overridden to hide attachments of deleted
                            # records)
                            query = 'SELECT id FROM ir_attachment WHERE res_model=%s AND res_id IN %s'
                            cr.execute(query, (self._name, sub_ids))
                            attachments = Attachment.browse([row[0] for row in cr.fetchall()])
                            if attachments:
                                attachments.unlink()
            
                        # invalidate the *whole* cache, since the orm does not handle all
                        # changes made in the database, like cascading delete!
                        self.invalidate_cache()
            
                    # recompute new-style fields
                    if self.env.recompute and self._context.get('recompute', True):
                        self.recompute()
                    # auditing: deletions are infrequent and leave no trace in the database
                    _unlink.info('User #%s deleted %s records with IDs: %r', self._uid, self._name, self.ids)
                    return True
                
                @api.model
                def create_meee2(self,):
                    #res = origin_create(self, vals) 
                    return True
                @api.multi
                def create_workflow(self,res):
                    """ Create a workflow instance for the given records. """
                    from odoo.addons.vneuron_workflow_odoo import workflow
                    for res_id in res:
                        _logger.info("________________THIS IS OK create_workflow  %s",self._name)
                        workflow.trg_create(self._uid, self._name, res_id, self._cr)
                    return True
            
                @api.multi
                def delete_workflow(self):
                    """ Delete the workflow instances bound to the given records. """
            #         from odoo import workflow
                    from odoo.addons.vneuron_workflow_odoo import workflow
                    for res_id in self.ids:
                        workflow.trg_delete(self._uid, self._name, res_id, self._cr)
                    self.invalidate_cache()
                    return True
            
                @api.multi
                def step_workflow(self):
                    """ Reevaluate the workflow instances of the given records. """
                    from odoo.addons.vneuron_workflow_odoo import workflow
                    for res_id in self.ids:
                        workflow.trg_write(self._uid, self._name, res_id, self._cr)
                    return True
            
                @api.multi
                def signal_workflow(self, signal):
                    """ Send the workflow signal, and return a dict mapping ids to workflow results. """
                    _logger.info('----- -------mrissa-------signal_workflow signal %s:',signal)
                    from odoo.addons.vneuron_workflow_odoo import workflow
                    result = {}
                    _logger.info('----- -------mrissa-------signal_workflow signal %s:',self.ids)
                    for res_id in self.ids:
                        result[res_id] = workflow.trg_validate(self._uid, self._name, res_id, signal, self._cr)
                    return result
            
                @api.model
                def redirect_workflow(self, old_new_ids):
                    """ Rebind the workflow instance bound to the given 'old' record IDs to
                        the given 'new' IDs. (``old_new_ids`` is a list of pairs ``(old, new)``.
                    """
                    from odoo.addons.vneuron_workflow_odoo import workflow
                    for old_id, new_id in old_new_ids:
                        workflow.trg_redirect(self._uid, self._name, old_id, new_id, self._cr)
                    self.invalidate_cache()
                    return True
                @api.model
                def _set_states_wkf(self):
                    _wkf = self.env['workflow'].search([('osv', '=', str(self._name))])
                    states=[]
                    for state in _wkf.activities:
                        x= (str(state.code), str(str(state.name)) )
                        states.append(x)
                    _logger.info('----- -------mrissa-------signal_workflow signal %s:',states)   
                    """ Override me in order to add new states in the server action. Please
                    note that the added key length should not be higher than already-existing
                    ones. """
                    return states
                
                models.AbstractModel._write = _write    
                models.AbstractModel.unlink = unlink
                models.AbstractModel._create = _create
                models.AbstractModel.create_meee2 = create_meee2
                models.AbstractModel.create_workflow = create_workflow
                models.AbstractModel.delete_workflow = delete_workflow
                models.AbstractModel.step_workflow = step_workflow
                models.AbstractModel.signal_workflow = signal_workflow
                models.AbstractModel._set_states_wkf =_set_states_wkf
                models.AbstractModel.redirect_workflow = redirect_workflow
                return super(BaseModelExtend, self)._register_hook()