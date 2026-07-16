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
                line.model,
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



    @api.model
    def send_email_disponible_custom(self):
        template_id = self.env['mail.template'].search([('id', '=', 37)], limit=1)

        self.env.cr.flush()

        maintenance_equipment_to_report = self.env["maintenance.equipment"].browse(
            self.env["maintenance.equipment"].search([
                ('x_studio_estado', '=', 'Disponible'),
            ]).ids
        )

        self.env.cr.execute("""
            SELECT id, name FROM maintenance_equipment
            WHERE id IN %s
        """, (tuple(maintenance_equipment_to_report.ids),))
        names_dict = dict(self.env.cr.fetchall())
        
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        worksheet = workbook.add_worksheet(_("Reporte de activos disponibles - %s" % str(date.today())))
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
                line.model,
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
            'name': _("Reporte de activos disponibles - %s.xlsx" % str(date.today())),
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
    def send_email_custom_tracking_old(self):
        template_id = self.env['mail.template'].search([('id', '=',36)], limit=1)

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
        worksheet = workbook.add_worksheet(_("Reporte de activos disponibles (Tranking)  - %s" % str(date.today())))
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
                ('tracking_value_ids.field_id.name', '=', 'x_studio_detalle_ubicacin_activo'),
            ], order='create_date desc')

            # Iteramos buscando el último cambio DESDE una ubicación llamada "Tienda"
            #tienda_location = self.env['x_detalleubicacionacti'].search([('x_name', 'ilike', 'TIENDA%')], limit=1)
            tienda_location = self.env['x_detalleubicacionacti'].search([('x_studio_ubicacion.x_name', 'ilike', 'TIENDA%')])
            line_last_loc_in_shop = False
            line_last_loc_in_shop_date = False

            for msg in messages:
                for track in msg.tracking_value_ids:
                    if track.field_id.name == 'x_studio_detalle_ubicacin_activo' and int(track.old_value_integer or 0) in tienda_location.ids:
                        line_last_loc_in_shop = tienda_location.filtered(lambda x: x.id == int(track.old_value_integer))
                        line_last_loc_in_shop_date = msg.create_date.strftime('%d/%m/%Y')
                        break
                if line_last_loc_in_shop_date:
                    break

            if not line_last_loc_in_shop:
                for msg in messages:
                    for track in msg.tracking_value_ids:
                        if track.field_id.name == 'x_studio_detalle_ubicacin_activo' and int(track.new_value_integer or 0) in tienda_location.ids:
                            if track.new_value_integer != line.x_studio_detalle_ubicacin_activo.id:
                                line_last_loc_in_shop = tienda_location.filtered(lambda x: x.id == int(track.new_value_integer))
                                line_last_loc_in_shop_date = msg.create_date.strftime('%d/%m/%Y')
                                break
                    if line_last_loc_in_shop_date:
                        break

            #raise UserError(str(line_name))
            rows.append((
                line_name,
                line.x_studio_marca,
                line.model,
                line.serial_no,
                line.x_studio_estado,
                line_last_loc_in_shop_date or 'NO',
                line_last_loc_in_shop.x_name if line_last_loc_in_shop else 'NO',
                line.x_studio_detalle_ubicacin_activo.x_name or 'NO',
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
            'name': _("Reporte de activos disponibles (Tranking)  - %s.xlsx" % str(date.today())),
            'type': 'binary',
            'datas': base64.encodebytes(data),
            'res_model': self._name,
            'res_id': self.id
        })

        template_id.attachment_ids = [(6, 0, [data_id.id])]
        self.env['mail.template'].browse(template_id.id).send_mail(self.id, force_send=True)
        template_id.attachment_ids = [(3, data_id.id)]


    # METODO
    @api.model
    def send_email_custom_tracking(self):
        template_id = self.env['mail.template'].browse(36)

        # 🔹 Flush para asegurar consistencia
        self.env.cr.flush()

        # 🔹 Obtener equipos directamente (sin browse innecesario)
        equipments = self.env["maintenance.equipment"].search([
            ('x_studio_estado', 'in', ['Disponible', 'Asignado', 'Baja']),
        ])

        # 🔹 Obtener ubicaciones UNA SOLA VEZ
        tienda_location = self.env['x_detalleubicacionacti'].search([])
        tienda_location_ids = set(tienda_location.ids)

        tienda_main_location = self.env['x_ubicacionactivo'].search([])
        tienda_main_location_ids = set(tienda_main_location.ids)

        # 🔹 Obtener TODOS los mensajes en una sola query
        messages = self.env['mail.message'].search([
            ('model', '=', 'maintenance.equipment'),
            ('res_id', 'in', equipments.ids),
            ('tracking_value_ids.field_id.name', 'in', [
                'x_studio_detalle_ubicacin_activo',
                'x_studio_ubicacin_activo'
            ])
        ], order='create_date desc')

        # 🔹 Agrupar mensajes por res_id (equipo)
        messages_by_equipment = {}
        for msg in messages:
            messages_by_equipment.setdefault(msg.res_id, []).append(msg)

        # 🔹 Función helper reutilizable
        def get_last_location(messages, field_name, valid_ids, current_id):
            """
            Busca la última ubicación basada en tracking.
            """
            for msg in messages:
                for track in msg.tracking_value_ids:
                    if track.field_id.name != field_name:
                        continue

                    old_val = int(track.old_value_integer or 0)
                    new_val = int(track.new_value_integer or 0)

                    # Convertir fecha a zona horaria del usuario
                    local_date = fields.Datetime.context_timestamp(msg, msg.create_date)

                    # 🔹 Caso 1: old_value válido
                    if old_val:
                        return old_val, local_date.strftime('%d/%m/%Y'), track.old_value_char

                    # 🔹 Caso 2: new_value válido pero distinto al actual
                    if new_val and new_val != current_id:
                        return new_val, local_date.strftime('%d/%m/%Y'), track.new_value_char

            return False, False, False
        # 🔹 Excel
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        worksheet = workbook.add_worksheet(
            _("Reporte de activos disponibles (Tracking) - %s" % str(date.today()))
        )

        style_highlight = workbook.add_format({
            'bold': True, 'pattern': 1, 'bg_color': '#E0E0E0', 'align': 'center'
        })
        style_normal = workbook.add_format({'align': 'center'})

        headers = [
            "Nombre del equipo",
            "Marca / Modelo",
            "N° de serie",
            "Estado",
            "Fecha Últ. Movimiento",
            "Ultima ubicación",
            "Detalle Últ. Ubicación",
            "Ubicación Actual",
            "Detalle Ubicación Actual",
            "Numero de activo",
        ]

        # 🔹 Escribir headers
        for col, header in enumerate(headers):
            worksheet.write(0, col, header, style_highlight)
            worksheet.set_column(col, col, 30)

        # 🔹 Procesar filas
        row = 1
        for eq in equipments:
            eq_messages = messages_by_equipment.get(eq.id, [])

            # 🔹 Obtener tracking optimizado
            last_detail_id, last_detail_date , last_detail_char = get_last_location(
                eq_messages,
                'x_studio_detalle_ubicacin_activo',
                tienda_location_ids,
                eq.x_studio_detalle_ubicacin_activo.id
            )

            last_main_id, last_main_date, last_main_char = get_last_location(
                eq_messages,
                'x_studio_ubicacin_activo',
                tienda_main_location_ids,
                eq.x_studio_ubicacin_activo.id
            )

            # 🔹 Obtener nombres sin filtered (más rápido)
            last_detail = tienda_location.browse(last_detail_id) if last_detail_id else False
            if not last_detail and last_detail_char:
                last_detail = tienda_location.filtered(lambda l: l.x_name == last_detail_char)[:1]

            last_main = tienda_main_location.browse(last_main_id) if last_main_id else False
            if not last_main and last_main_char:
                last_main = tienda_main_location.filtered(lambda l: l.x_name == last_main_char)[:1]

            if not last_main and last_detail:
                last_main = last_detail.x_studio_ubicacion

            if not last_detail:
                last_detail = eq.x_studio_detalle_ubicacin_activo

            if not last_main:
                last_main = eq.x_studio_ubicacin_activo

            if not last_detail_date:
                if eq.create_date:
                    local_creation = fields.Datetime.context_timestamp(eq, eq.create_date)
                    last_detail_date = local_creation.strftime('%d/%m/%Y')
                else:
                    last_detail_date = 'NO'

            worksheet.write_row(row, 0, [
                eq.with_context(lang='es_PE').name,
                "%s / %s" % (eq.x_studio_marca, eq.model) if eq.model else eq.x_studio_marca,
                eq.serial_no,
                eq.x_studio_estado,
                last_detail_date or 'NO',
                last_main.x_name if last_main else 'NO',
                last_detail.x_name if last_detail else 'NO',
                eq.x_studio_ubicacin_activo.x_name or 'NO',
                eq.x_studio_detalle_ubicacin_activo.x_name or 'NO',
                eq.x_studio_nmero_de_activo or "",
            ], style_normal)

            row += 1

        workbook.close()
        data = output.getvalue()

        # 🔹 Adjuntar archivo
        attachment = self.env['ir.attachment'].create({
            'name': _("Reporte de activos disponibles (Tracking) - %s.xlsx" % str(date.today())),
            'type': 'binary',
            'datas': base64.encodebytes(data),
            'res_model': self._name,
            'res_id': self.id
        })

        template_id.attachment_ids = [(6, 0, [attachment.id])]
        template_id.send_mail(self.id, force_send=True)
        template_id.attachment_ids = [(3, attachment.id)]

    def _compute_field_value(self, field):
        if self._name == 'maintenance.equipment':
            self = self.with_context(tracking_disable=False)

        return super()._compute_field_value(field)
