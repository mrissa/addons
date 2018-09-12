import logging

from odoo import api, fields, models
from odoo import tools, _
from odoo.exceptions import ValidationError
from odoo.modules.module import get_module_resource


class ProductTemplate(models.Model):
    _name = "product.template"
    _description = "Product"
    _inherit = ['product.template']

    categ_product = fields.Many2one('categ.equipement', string='Categorie equipement',required=True)
    type_id = fields.Many2one('type.equipement', string='Type equipement', domain="[('categ_id', '=', categ_product)]")

class CategEquipement(models.Model):
    _name = "categ.equipement"
    _description = "Categorie equipement"

    name = fields.Char('Categorie equipement', required=True, translate=True)
    type_ids = fields.One2many('type.equipement', 'categ_id', string='Type equipement')

class TypeEquipement(models.Model):
    _name = "type.equipement"
    _description = "Type Equipement"

    name = fields.Char('Type equipement', required=True, translate=True)
    categ_id = fields.Many2one('categ.equipement', string='Categorie equipement')

class affectation_instruction(models.Model):
    _name = "affectation.instruction"
    _description = "Instruction"
    _inherit = ['mail.thread']

    _mail_post_access = 'read'

    product_ids = fields.One2many('instruction.line','affectation_ins_id' ,string='Code Materiel')
    establishment_id = fields.Many2one('educa.establishment', string='Establishment')
    send_date = fields.Date('Date Envoi')
    notes = fields.Char('Notes', translate=True)

class instruction_line(models.Model):
    _name = "instruction.line"
    _description = "Instruction"
    _inherit = ['mail.thread']

    product_id = fields.Many2one('product.template', string='Equipement')
    etat = fields.Selection([('bon', 'Bon'), ('moyen', 'Moyen'), ('mauvais', 'Mauvais'), ('non_utilisable', 'Non Utilisable')],'Etat')
    quantity =fields.Float('Quantite')
    affectation_ins_id = fields.Many2one('affectation.instruction', string='Affectation')
    notes = fields.Char('Notes', translate=True)
    product_date = fields.Date('Date Production')
    establishment_id = fields.Many2one('educa.establishment', related='affectation_ins_id.establishment_id',
                                       string='Establishment')
