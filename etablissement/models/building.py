import base64
import threading
from odoo import api, fields, models
from odoo import tools, _
from odoo.modules.module import get_module_resource

class EducaBuilding(models.Model):
    _name = "educa.building"
    _description = "Educational Building"
    _order = 'name'
    _inherit = ['mail.thread']

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

    @api.multi
    def _salle_count(self):
        for each in self:
            salle_ids = self.env['educa.classroom'].search([('building_id', '=', each.id)])
            each.salle_count = len(salle_ids)

    @api.multi
    def salle_view(self):
        self.ensure_one()
        domain = [
            ('building_id', '=', self.id)]
        return {
            'name': _('classroom'),
            'domain': domain,
            'res_model': 'educa.classroom',
            'type': 'ir.actions.act_window',
            'view_id': False,
            'view_mode': 'tree,form',
            'view_type': 'form',
            'help': _('''<p class="oe_view_nocontent_create">
                                       Click to Create New Building
                                    </p>'''),
            'limit': 80,
        }

    name = fields.Char(string="Code Of building", translate=True, copy=False, readonly=True)
    establishment_id = fields.Many2one('educa.establishment', string='Establishment',required="1")
    active = fields.Boolean(string=" Active",default=True)
    designation = fields.Char(string="Name Of building", translate=True)
    street = fields.Char(string="Street", translate=True)
    state_id = fields.Many2one('nmcl.state', string='State', ondelete='restrict')
    country_id = fields.Many2one('res.country', string='Country')
    city = fields.Char(string='City', translate=True)
    common_place = fields.Char(string="Common Place", translate=True)
    state = fields.Selection([('under_construction', 'Under construction'), ('operational', 'Operational'), ('not_operational', 'Not Operational')],
                                 string='State')
    note_state = fields.Text(string="Why", translate=True)
    type_building = fields.Selection([('class', 'Class'), ('warehouse', 'Warehouse'),
                                        ('workshop', 'workshop'),('other','Other')], string='Type of Building')
    notes = fields.Text('Notes')
    length = fields.Float(string="length")
    width = fields.Float(string="width")
    height = fields.Float(string="height")
    eets = fields.Selection([('water', 'Water'), ('electricity', 'Electricity'),
                                        ('tel', 'Tel'),('sanitary','Sanitary')], string='EETS')
    water = fields.Boolean('Water')
    electricity = fields.Boolean('Electricity')
    tel = fields.Boolean('Tel', )
    sanitary = fields.Boolean('Sanitary')
    internet = fields.Boolean('Internet', )
    # image: all image fields are base64 encoded and PIL-supported
    image = fields.Binary("Photo", default=_default_image, attachment=True,
                          help="This field holds the image used as photo for the building, limited to 1024x1024px.")
    image_medium = fields.Binary("Medium-sized photo", attachment=True)
    image_small = fields.Binary("Small-sized photo", attachment=True)
    salle_count = fields.Integer(compute='_salle_count', string='classroom')
    company_id = fields.Many2one('res.company', string='Company', index=True,
                                 default=lambda self: self.env.user.company_id.id)

    _sql_constraints = [
            ('code_uniq', 'unique (name)', "The code must be unique per Building!"),
        ]

    @api.model
    def create(self, vals):
        """Generate a sequence number"""
        number_id = self.env['educa.establishment'].search([('id', '=', vals['establishment_id'])]).number_id
        name = self.search([('establishment_id', '=', vals['establishment_id'])], order="name desc", limit=1).name
        if name:
            num = str(name).split('/')
            start_num =(int(num[0]))
            end_num = int(num[1])
            final_name=str(start_num) +'/' +str(end_num+1)
            vals['name'] = final_name
        else:
            vals['name'] = str(number_id) +'/' +'1'
        return super(EducaBuilding, self).create(vals)