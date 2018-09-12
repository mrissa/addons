# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
import base64
import threading
import logging
import random
import string
from odoo import api, fields, models
from odoo import tools, _
from odoo.exceptions import ValidationError
from odoo.modules.module import get_module_resource


_logger = logging.getLogger(__name__)

class StudStudent(models.Model):

    _name = "stud.student"
    _description = "Stud Student"
    _order = 'name'
    _inherit = ['mail.thread']

    @api.model
    def _default_image(self):
        if getattr(threading.currentThread(), 'testing', False) or self._context.get('install_mode'):
            return False
        colorize, img_path, image = False, False, False
        img_path = get_module_resource('student', 'static/src/img', 'default_image.png')
        if img_path:
            with open(img_path, 'rb') as f:
                image = f.read()
        if image and colorize:
            image = tools.image_colorize(image)
        return tools.image_resize_image_big(base64.b64encode(image))

    name = fields.Char(string="Last name and first name", translate=True, required=True)
    active = fields.Boolean('Active', default=True)
    country_id = fields.Many2one('res.country', string='Nationality')
    identification_id = fields.Char(string='National Matricule', copy=False)
    nni = fields.Char(string='NNI', copy=False, required=True)
    birthday = fields.Date('Date of Birth')
    place_birth = fields.Text('Place of birth', translate=True)
    town_birth = fields.Many2one('nmcl.town')
    town_residence = fields.Many2one('nmcl.town')
    gender = fields.Selection([
        ('male', 'Male'),
        ('female', 'Female')
    ])
    address = fields.Text('Adress' , translate=True)
    notes = fields.Text('Notes', translate=True)
    color = fields.Integer('Color Index', default=0)
    # image: all image fields are base64 encoded and PIL-supported
    image = fields.Binary("Photo", default=_default_image, attachment=True,
        help="This field holds the image used as photo for the student, limited to 1024x1024px.")
    image_medium = fields.Binary("Medium-sized photo", attachment=True,
        help="Medium-sized photo of the sudent. It is automatically "
             "resized as a 128x128px image, with aspect ratio preserved. "
             "Use this field in form views or some kanban views.")
    image_small = fields.Binary("Small-sized photo", attachment=True,
        help="Small-sized photo of the student. It is automatically "
             "resized as a 64x64px image, with aspect ratio preserved. "
             "Use this field anywhere a small image is required.")
    situation_pro_fadher = fields.Selection(
        selection=[
            ('unemployed', 'unemployed'),
            ('salaried', 'salaried'),
            ('independent', 'independent'),
            ('other', 'other'),
        ],
        string="Profesional situation of the father"
    )
    other_father = fields.Char(string='Other Father', translate=True)
    situation_pro_mother = fields.Selection(
        selection=[
            ('unemployed', 'unemployed'),
            ('salaried', 'salaried'),
            ('independent', 'independent'),
            ('other', 'other'),
        ],
        string="Profesional situation of the mother"
    )
    name_father = fields.Char(string='Name father', translate=True)
    name_mother = fields.Char(string='Name mother', translate=True)
    tel_mother = fields.Char(string='Tel mother')
    tel_father = fields.Char(string='Tel father')
    other_mother = fields.Char(string='Other Mother', translate=True)
    revenue_father = fields.Float(string="Revenue father")
    revenue_mother = fields.Float(string="Revenue mother")
    number = fields.Integer(string="student/foyer room")
    electricity = fields.Boolean('Presence of electricity')
    water = fields.Boolean('Presence of water')
    leisure = fields.Boolean('Existence leisure place')
    distance = fields.Float(string="Distance housing and educational institution")
    comment = fields.Text('Notes', translate=True)
    etranger = fields.Boolean('Etranger')
    boursier = fields.Boolean('Boursier')
    state = fields.Selection([('draft', 'Draft'), ('not_affect', 'Not Affect'), ('actif', 'Actif'), ('inactif', 'Inactif'), ('scolarity_terminated', 'Scolarity termineted')],
                             string='State', default='draft',readonly=True)
    company_id = fields.Many2one('res.company', string='Company', index=True,
                                 default=lambda self: self.env.user.company_id.id)
    pv_id = fields.Many2one('stud.student.pv', string='Pv de sortie')
    etab_origine_id = fields.Many2one('educa.establishment', string='Etablissement Origine')
    establishment_id = fields.Many2one('educa.establishment', string='Etablissement', readonly=True)
    scholarly_id = fields.Many2one('year.scholarly', string='Year Scholarly', readonly=True)
    state_inscription = fields.Selection(
        [('draft', 'Brouillon'), ('inscrit', 'Inscrit'), ('transfert', 'En Transfert'), ('abandonner', 'Abandonner'),
         ('exclu', 'Exclu'), ('admis', 'Admis'), ('redoublant', 'Redoublant')], 'State registration',
        readonly=True,)

    _sql_constraints = [
        ('identification_id_uniq', 'unique(identification_id)',
         'The Student Number must be unique across the company(s).'),
        ('nni_uniq', 'unique(nni)',
         'The NNI must be unique.')
    ]

    @api.multi
    def write(self, vals):
        tools.image_resize_images(vals)
        return super(StudStudent, self).write(vals)

    @api.model
    def create(self, vals):
        tools.image_resize_images(vals)
        return super(StudStudent, self).create(vals)

class StudStudentPV(models.Model):
    _name = "stud.student.pv"
    _description = "Import Student"
    _order = "scholarly_insc_id asc"

    @api.one
    @api.depends('type')
    def _get_type_structure(self):
        if self.type:
            if self.type=='pv_sortie':
                self.type_structure='first_level'

    name = fields.Char(string='Reference PV', required=True, copy=False)
    type = fields.Selection([('pv_sortie', 'PV de sortie'),('on_demande', 'On demande')], string='Type', required=True)
    scholarly_insc_id = fields.Many2one('year.scholarly', string='Year Scholarly inscription', required=True, domain="[('state','=','open'), ('niveau','=','central'), ('type','!=','central')]")
    structure_line_id = fields.Many2one('year.scholarly.line', string='Niveau scolaire', domain="[('scholarly_id', '=', scholarly_insc_id)]", required=True)
    structure = fields.Char(string='Structure', related='structure_line_id.name')
    student_ids = fields.One2many('stud.student', 'pv_id', 'Students')
    succes_year = fields.Date(string='Année de réussite')
    state = fields.Selection([('draft', 'Draft'), ('validate', 'Validate')],
                             string='State', default='draft')
    type_structure = fields.Selection([('first_level', 'First Level'),('not_first_level', 'Not first Level')], string='Type structure', compute='_get_type_structure')

    @api.multi
    def act_validate(self):
        inscrLine = self.env['stud.inscription']
        if self.type == 'pv_sortie':
            type='first_inscription_competition'
        if self.type == 'on_demande':
            type='first_request_inscription'
        for stud in self.student_ids:
            ins=inscrLine.create({
                'student_id': stud.id,
                'scholarly_id': self.scholarly_insc_id.id,
                'structure': self.structure,
                'etabli_origine': stud.etab_origine_id.id,
                'type': type,
            })
            stud.state='not_affect'
            stud.scholarly_id = self.scholarly_insc_id.id
            stud.establishment_id = stud.etab_origine_id.id
            stud.state_inscription = 'draft'
        self.state = 'validate'
