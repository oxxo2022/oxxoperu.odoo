from odoo import api, fields, models, _
from datetime import date, timedelta
from odoo.exceptions import UserError, ValidationError
from odoo.tools import pycompat
import base64
import csv
import contextlib
import io
from odoo.tools.misc import xlsxwriter
class MaintenanceEquipment(models.Model):
    _inherit = 'maintenance.equipment'

    x_studio_ubicacion_activo_name = fields.Char(related="x_studio_ubicacin_activo.x_name", string="Estado nombre")
    x_studio_nombre_host=fields.Char(string="Nombre Host")
    x_studio_memoria_ram_1=fields.Char(string="Memoria RAM")
    x_studio_disco_duro_1=fields.Char(string="Disco Duro")
    x_studio_procesador_2=fields.Char(string="Procesador")
    x_studio_criticidad_1= fields.Selection(string="Criticidad",
        selection=[("Crítico", "Crítico"), ("No crítico", "No crítico")])
    x_studio_sistema_operativo_1=fields.Char(string="Sistema Operativo")
    
    def _enviar_reporte_activos(self):
        return self.send_email_custom()

    # METODO
    @api.model
    def send_email_custom(self):
        template_id = self.env['mail.template'].search([('id', '=', 13)], limit=1)
        maintenance_equipment_to_report = self.env["maintenance.equipment"].search([('x_studio_estado', '=', 'Asignado'),('x_studio_ubicacion_activo_name', 'in', ('TIENDA'))])

        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        worksheet = workbook.add_worksheet(_("Reporte de activos - %s" % str(date.today())))
        style_highlight = workbook.add_format({'bold': True, 'pattern': 1, 'bg_color': '#E0E0E0', 'align': 'center'})
        style_normal = workbook.add_format({'align': 'center'})
        row = 0

        headers = [
            "Activo",
            "Estado",
            "N° de serie",
            "Ubicación",
            "Ubicación detalle",
        ]

        rows = []
        for line in maintenance_equipment_to_report:
            rows.append((
                line.display_name,
                line.x_studio_estado,
                line.serial_no,
                line.x_studio_ubicacin_activo.x_name,
                line.x_studio_detalle_ubicacin_activo.x_name
            ))

        col = 0
        for header in headers:
            worksheet.write(row, col, header, style_highlight)
            worksheet.set_column(col, col, 30)
            col += 1

        row = 1
        for employee_row in rows:
            col = 0
            for employee_data in employee_row:
                worksheet.write(row, col, employee_data, style_normal)
                col += 1
            row += 1

        workbook.close()
        data = output.getvalue()

        data_id = self.env['ir.attachment'].create({
            'name': _("Reporte de activos - %s.xlsx" % str(date.today())),
            'type': 'binary',
            'datas': base64.encodebytes(data),
            'res_model': self._name,
            'res_id': self.id
        })

        template_id.attachment_ids = [(6, 0, [data_id.id])]
        self.env['mail.template'].browse(template_id.id).send_mail(self.id, force_send=True)
        template_id.attachment_ids = [(3, data_id.id)]