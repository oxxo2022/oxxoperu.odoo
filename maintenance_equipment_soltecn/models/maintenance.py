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

    # aux_name = fields.Char(string="Estado nombre",compute='_compute_aux_name')
    
    def _enviar_reporte_activos(self):
        return self.send_email_custom()

    # # @api.depends('name','serial_no')
    # def _compute_aux_name(self):
    #     for record in self:
    #             record.aux_name = record.name    

    # METODO
    @api.model
    def send_email_custom(self):
        template_id = self.env['mail.template'].search([('id', '=', 13)], limit=1)

        self.env.cr.flush()

        maintenance_equipment_to_report = self.env["maintenance.equipment"].browse(
            self.env["maintenance.equipment"].search([
                ('x_studio_estado', '=', 'Asignado'),
                ('x_studio_ubicacion_activo_name', 'ilike', 'TIENDA%')
            ]).ids
        )

        self.env.cr.execute("""
            SELECT id, name FROM maintenance_equipment
            WHERE id IN %s
        """, (tuple(maintenance_equipment_to_report.ids),))
        names_dict = dict(self.env.cr.fetchall())
        
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        worksheet = workbook.add_worksheet(_("Reporte de activos - %s" % str(date.today())))
        style_highlight = workbook.add_format({'bold': True, 'pattern': 1, 'bg_color': '#E0E0E0', 'align': 'center'})
        style_normal = workbook.add_format({'align': 'center'})
        row = 0
        #s
        headers = [
            "Nombre del equipo",
            "Marca",
            "Modelo",
            "N° de serie",
            "Estado",
            "Ubicación",
            "Ubicación detalle",
        ]

        rows = []
        for line in maintenance_equipment_to_report:
            line_name = names_dict.get(line.id, '').get('es_PE')
            #raise UserError(str(line_name))
            rows.append((
                line_name,
                line.x_studio_marca,
                line.model.name,
                line.serial_no,
                line.x_studio_estado,
                line.x_studio_ubicacin_activo.x_name,
                line.x_studio_detalle_ubicacin_activo.x_name,
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



    def _enviar_reporte_activos_tracking(self):
        return self.send_email_custom_tracking()

    # # @api.depends('name','serial_no')
    # def _compute_aux_name(self):
    #     for record in self:
    #             record.aux_name = record.name    

    # METODO
    @api.model
    def send_email_custom_tracking(self):
        template_id = self.env['mail.template'].search([('id', '=', 13)], limit=1)

        self.env.cr.flush()

        maintenance_equipment_to_report = self.env["maintenance.equipment"].browse(
            self.env["maintenance.equipment"].search([
                ('x_studio_estado', '=', 'Disponible'),
                #('x_studio_ubicacion_activo_name', 'ilike', 'TIENDA%')
            ]).ids
        )

        self.env.cr.execute("""
            SELECT id, name FROM maintenance_equipment
            WHERE id IN %s
        """, (tuple(maintenance_equipment_to_report.ids),))
        names_dict = dict(self.env.cr.fetchall())
        
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        worksheet = workbook.add_worksheet(_("Reporte de activos - %s" % str(date.today())))
        style_highlight = workbook.add_format({'bold': True, 'pattern': 1, 'bg_color': '#E0E0E0', 'align': 'center'})
        style_normal = workbook.add_format({'align': 'center'})
        row = 0
        #s
        headers = [
            "Nombre del equipo",
            "Marca",
            "Modelo",
            "N° de serie",
            "Estado",
            "Fecha de ultima ubicación en tienda",
            "Ultima ubicación en tienda",
            "Ubicación actual",
        ]

        rows = []
        for line in maintenance_equipment_to_report:
            line_name = names_dict.get(line.id, '').get('es_PE')
            line_last_loc_in_shop = False
            line_last_loc_in_shop_date = False

            messages = self.env['mail.message'].search([
                ('model', '=', line._name),
                ('res_id', '=', line.id),
                ('tracking_value_ids.field_id.name', '=', 'x_studio_ubicacin_activo'),
            ], order='create_date desc')

            # Iteramos buscando el último cambio DESDE una ubicación llamada "Tienda"
            tienda_location = self.env['x_ubicacionactivo'].search([('x_name', 'ilike', 'TIENDA%')], limit=1)
            line_last_loc_in_shop = False
            line_last_loc_in_shop_date = False

            for msg in messages:
                for track in msg.tracking_value_ids:
                    if track.field == 'x_studio_ubicacin_activo' and int(track.old_value_integer or 0) == tienda_location.id:
                        line_last_loc_in_shop = tienda_location
                        line_last_loc_in_shop_date = msg.create_date.strftime('%d/%m/%Y')
                        break
                if line_last_loc_in_shop_date:
                    break
            
            #raise UserError(str(line_name))
            rows.append((
                line_name,
                line.x_studio_marca,
                line.model.name,
                line.serial_no,
                line.x_studio_estado,
                line_last_loc_in_shop.x_name if line_last_loc_in_shop else 'NO',
                line_last_loc_in_shop_date or 'NO',
                line.x_studio_ubicacin_activo.x_name,
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