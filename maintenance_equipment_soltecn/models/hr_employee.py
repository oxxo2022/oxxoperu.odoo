from datetime import date, datetime, time
from pytz import timezone

from odoo import _, api, fields, models
from odoo.osv import expression
from odoo.addons.resource.models.resource import Intervals
from odoo.exceptions import UserError


class Employee(models.Model):
    _inherit = "hr.employee"

    image_global_protect = fields.Image(string="Imagen Global Protect")

    image_cortex = fields.Image(string="Imagen Cortex")