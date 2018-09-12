# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import base64
import threading
import random
import string
import logging
from odoo import api, fields, models
from odoo import tools, _
from odoo.exceptions import ValidationError
from odoo.modules.module import get_module_resource


class EducaEstablishmentCategory(models.Model):
    _name = "educa.establishment.category"
    _description = "Educa Establishment Category"

    name = fields.Char(string="establishment Tag", required=True)
    color = fields.Integer(string='Color Index')
    establishment_ids = fields.Many2many('educa.establishment', 'establishment_category_rel', 'category_id', 'establishment_id', string='Establishment')

    _sql_constraints = [
        ('name_uniq', 'unique (name)', "Tag name already exists !"),
    ]

class EducaEstablishmentType(models.Model):
    _name = "educa.establishment.type"
    _description = "Establishment Type"

    name = fields.Char(string="School type", required=True, translate=True)
    type = fields.Selection([('fondamentale', 'Fondamentale'), ('secondaire', 'Secondaire')], string='Type', required=True)
    cycle_ids = fields.Many2many('educa.establishment.cycle', 'type_enseig_cycle_rel', 'cycle_id', 'type_id', string="Cycles", domain="[('type','=',type)]")

class EducaestablishmentCycle(models.Model):
    _name = "educa.establishment.cycle"
    _description = "Establishment Cycle"

    name = fields.Char(string="Cycle", required=True, translate=True)
    type = fields.Selection([('fondamentale', 'Fondamentale'), ('secondaire', 'Secondaire')], string='Type',)
    establishment_id = fields.Many2one('educa.establishment', string='Establishment')

class EducaEstablishment(models.Model):
    _name = "educa.establishment"
    _description = "education establishment"
    _order = 'name'
    _inherit = ['mail.thread']

    @api.multi
    @api.depends('salle_ids')
    def _salle_count(self):
        surface = 0.0
        for each in self:
            salle_ids = self.env['educa.classroom'].search([('establishment_id', '=', each.id)])
            salle_conform_ids = self.env['educa.classroom'].search([('establishment_id', '=', each.id), ('state', '=', 'compliant')])
            salle_not_conform_ids = self.env['educa.classroom'].search([('establishment_id', '=', each.id), ('state', '=', 'not_compliant')])
            each.salle_count = len(salle_ids)
            each.classroom_count = len(salle_ids)
            each.classroom_conform_count = len(salle_conform_ids)
            each.classroom_not_conform_count = len(salle_not_conform_ids)
            if salle_ids:
                for salle in salle_ids:
                    surface = surface+salle.surface
            each.remaining_surface = each.surface - surface

    @api.multi
    def _building_count(self):
        for each in self:
            building_ids = self.env['educa.building'].search([('establishment_id', '=', each.id)])
            each.building_count = len(building_ids)

    @api.model
    def _default_image(self):
        if getattr(threading.currentThread(), 'testing', False) or self._context.get('install_mode'):
            return False
        colorize, img_path, image = False, False, False
        img_path = get_module_resource('etablissement', 'static/src/img', 'company_image.png')
        if img_path:
            with open(img_path, 'rb') as f:
                image = f.read()
        if image and colorize:
            image = tools.image_colorize(image)
        return tools.image_resize_image_big(base64.b64encode(image))

    @api.one
    @api.depends('type_school.type')
    def _get_type_school(self):
        if self.type_school.type:
            self.type = self.type_school.type

    number_id = fields.Char(string='Code', copy=False, translate=True,)
    name = fields.Char(string="Name" ,required=True, copy=False, translate=True)
    parent_id = fields.Many2one('educa.establishment', string='Etablissement Mére' )
    type_etablissement = fields.Selection(
        [('dren', 'DREN'), ('enseignement', 'Enseignement'), ('administratif', 'Administratif'), ('hors_men', 'Hors Ministère')],
        string='Type Etablissement', )
    state_id = fields.Many2one("nmcl.state", string='State', ondelete='restrict', required=True)
    city_id = fields.Many2one('nmcl.city', string='City', domain="[('state_id', '=', state_id)]", required=True)
    town_id = fields.Many2one('nmcl.town', string='Town', domain="[('city_id', '=', city_id)]", required=True)
    type_school = fields.Many2one('educa.establishment.type', string="Type Enseignement")
    school_plan = fields.Selection([('mixte', 'Mixte'), ('no_mixte', 'No Mixte')], string='Mixte/Non mixte')
    cycle = fields.One2many('educa.establishment.cycle', 'establishment_id', string="Cycle",)
    dren_id = fields.Many2one('nmcl.dren', string="DREN")
    user_id = fields.Char(string="Property", translate=True)
    state = fields.Selection([('pending_approval', 'In progress to approve'), ('open', 'Open'), ('standby', 'Standby'), ('close', 'Close')],
                             string='State', default='open')
    type = fields.Selection([('fondamentale', 'Fondamentale'), ('secondaire', 'Secondaire')],
                             string='Type', compute='_get_type_school', store=True)
    categorie = fields.Selection([('excellence', 'Excellence'), ('normal', 'Normal'), ('pilote', 'Pilote')],
                             string='Categorie', default='normal')
    phone = fields.Char(string="Phone")
    fax = fields.Char(string="Fax")
    email = fields.Char(string="Email")
    street = fields.Text(string="Adress", translate=True)
    school_state = fields.Selection([('prived', 'Prived'), ('public', 'Public')], string='Prive/Public')
    ecological_situation = fields.Selection([('rural', 'Rural'),('citadin', 'Citadin')],string='Ecological situation' )
    distance_km_state = fields.Float(string="Distance Km State")
    notes = fields.Text('Notes')
    date = fields.Date(string="Date")
    # image: all image fields are base64 encoded and PIL-supported
    image = fields.Binary("Photo", default=_default_image, attachment=True,
                          help="This field holds the image used as photo for the employee, limited to 1024x1024px.")
    image_medium = fields.Binary("Medium-sized photo", attachment=True)
    image_small = fields.Binary("Small-sized photo", attachment=True)
    # etablissement privé
    date_agrement = fields.Date(string="Date Agrement")
    lieu_agrement = fields.Char(string="Lieu Agrement", translate=True)
    legal_form = fields.Char(string="Legal Form", translate=True)
    nature_of_the_service = fields.Char(string="Nature Of The Sevice", translate=True)
    manager = fields.Many2one('res.users', string="Manager")
    last_date = fields.Date(string="Last Date")
    # etablissement Smart buttons
    building_ids = fields.One2many('educa.building', 'establishment_id', string='Blocs')
    building_count = fields.Integer(compute='_building_count', string='Building')
    salle_count = fields.Integer(compute='_salle_count', string='Classroms')
    classroom_count = fields.Integer(compute='_salle_count', string='Number of pieces')
    classroom_conform_count = fields.Integer(compute='_salle_count', string='Total classroom conform')
    classroom_not_conform_count = fields.Integer(compute='_salle_count', string='Total classroom not conform')
    surface = fields.Float(string='Surface')
    remaining_surface = fields.Float(compute='_get_remaining_surface', string='Remaining surface')
    internal_hosting = fields.Boolean(string='Internal Hosting', default=False)
    salle_ids = fields.One2many('educa.classroom', 'establishment_id', string="Classrooms")
    equipement_ids = fields.One2many('instruction.line', 'establishment_id', string="Equipements")
    company_id = fields.Many2one('res.company', string='Company', index=True,
                                 default=lambda self: self.env.user.company_id.id)

    _sql_constraints = [
        ('code_uniq', 'unique (number_id)', "The code must be unique per establishment!"),
    ]

    @api.model
    def create(self, vals):
        tools.image_resize_images(vals)
        code_state=self.env['nmcl.state'].search([('id','=',vals['state_id'])]).code
        code_city=self.env['nmcl.city'].search([('id','=',vals['city_id'])]).code
        code_town=self.env['nmcl.town'].search([('id','=',vals['town_id'])]).code
        establishments = self.search([])
        if establishments:
            number=len(establishments)+1
        else:
            number=1
        if code_city and code_state and code_town:
            vals['number_id'] = str(code_state)+str(code_city)+str(code_town)+'/'+str(number)
        else:
            vals['number_id'] = '000000'+'/' + str(number)
        return super(EducaEstablishment, self).create(vals)

    @api.multi
    def act_open(self):
        self.state = 'open'

    @api.multi
    def act_close(self):
        self.state = 'close'

class EducaClassroom(models.Model):
    _name = "educa.classroom"
    _description = "Educa Classroom"
    _inherit = ['mail.thread']

    @api.multi
    def _equipement_count(self):
        for each in self:
            salle_ids = self.env['instruction.line'].search([('affectation_id.classroom_id', '=', each.id)])
            each.equipement_count = len(salle_ids)

    @api.one
    @api.depends('largeur', 'longueur')
    def _get_surface(self):
        if self.largeur and self.longueur:
            self.surface = self.longueur * self.largeur

    @api.one
    @api.depends('surface')
    def _get_state(self):
        if self.surface:
            if self.surface>50:
                self.state = 'compliant'
            else:
                self.state = 'not_compliant'

    name = fields.Char(string="Code", readonly=True, copy=False)
    establishment_id = fields.Many2one('educa.establishment', string='Establishment', required="1")
    building_id = fields.Many2one('educa.building', string='Batiment',required="1", domain="[('establishment_id', '=', establishment_id)]")
    nb_eleve = fields.Integer(string='Nombre maximum Eleve')
    longueur = fields.Float(string='Longueur')
    largeur = fields.Float(string='Largeur')
    surface = fields.Float(string='Surface', compute="_get_surface")
    state = fields.Selection([('compliant', 'Compliant'), ('not_compliant', 'Not compliant')],
                             string='State', compute='_get_state')
    classification = fields.Many2one('classification.classroom', string='Classification')
    note = fields.Char('Commentaires', translate=True)
    equipement_count = fields.Integer(compute='_equipement_count', string='Equipements')
    company_id = fields.Many2one('res.company', string='Company', index=True,
                                 default=lambda self: self.env.user.company_id.id)
    _sql_constraints = [
        ('code_uniq', 'unique (name)', "The code must be unique!"),
    ]

    @api.model
    def create(self, vals):
        """Generate a sequence number"""
        number_id = self.env['educa.establishment'].search([('id', '=', vals['establishment_id'])]).number_id
        code = self.search([('establishment_id', '=', vals['establishment_id'])], order="name desc", limit=1).name
        if code:
            num = str(code).split('/')
            start_num =(int(num[0]))
            end_num = int(num[1])
            final_name=str(start_num) +'/' +str(end_num+1)
            vals['name'] = final_name
        else:
            vals['name'] = str(number_id) +'/' +'1'
        return super(EducaClassroom, self).create(vals)

class ClassificationClassroom(models.Model):
    _name = "classification.classroom"
    _description = "Classification Classroom"

    name = fields.Char(string="Nom", translate=True, required=True)