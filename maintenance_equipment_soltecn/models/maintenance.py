from odoo import api, fields, models, _
from datetime import date, timedelta
from odoo.exceptions import UserError, ValidationError
import base64

class MaintenanceEquipment(models.Model):
    _inherit = 'maintenance.equipment'

    x_studio_ubicacion_activo_name = fields.Char(related="x_studio_ubicacin_activo.x_name", string="Estado nombre")

    def _enviar_reporte_activos(self):
        return self.send_email_custom()

    @api.model
    def send_email_custom(self):
        template_id = self.env['mail.template'].search([('id', '=', 13)], limit=1)
        # last_day_of_prev_month = date.today().replace(day=1) - timedelta(days=1)
        # start_day_of_prev_month = date.today().replace(day=1) - timedelta(days=last_day_of_prev_month.day)
        maintenance_equipment_to_report = self.env["maintenance.equipment"].search([('x_studio_estado_name', '=', 'asignado'),('x_studio_ubicacion_activo_name', 'in', ('OS','TIENDA'))])
        # ,('x_studio_ubicacion_activo_name', 'in', ('OS','TIENDA'))
        raise ValidationError(len(maintenance_equipment_to_report))
        # ('id', 'in', [1578, 1579, 1580, 1581, 1582])
        # ('__last_update', '>=', start_day_of_prev_month),('__last_update', '<=', last_day_of_prev_month)

        data, data_format = self.env.ref('studio_customization.equipo_de_mantenimie_b2fb437d-6e04-4ef9-a3b8-242087bd633f').sudo()._render_qweb_pdf(maintenance_equipment_to_report.ids)
        
        data_id = self.env['ir.attachment'].create({
            'name': _("Reporte de activos - %s.pdf" % str(date.today())),
            'type': 'binary',
            'datas': base64.encodebytes(data),
            'res_model': self._name,
            'res_id': self.id
        })

        template_id.attachment_ids = [(6, 0, [data_id.id])]
        self.env['mail.template'].browse(template_id.id).send_mail(self.id, force_send=True)
        template_id.attachment_ids = [(3, data_id.id)]

        # for maintenance in self:
        # self.env['mail.template'].browse(template_id).send_mail(self.id, force_send=True)
                # data, data_format = self.env.ref('studio_customization.studio_report_docume_8f3425e2-e80d-4aca-8c43-e8d80dfbe347').sudo()._render_qweb_pdf(maintenance_equipment_to_report.ids)
        # result = base64.b64encode(result)

        # docids = maintenance_equipment_to_report.ids
        # docs = self.env['maintenance.equipment'].browse(docids)
        
        # docargs = {
        # 'doc_ids': docids,
        # 'doc_model': maintenance_equipment_to_report.model,
        # 'docs': docs,
        # 'data': None,
        # }
        
        # report_obj = self.env['report']
        # report = self.env['ir.actions.report']._get_report_from_name('studio_customization.studio_report_docume_8f3425e2-e80d-4aca-8c43-e8d80dfbe347')
        # report = report_obj._get_report_from_name(self._template)

        # docargs = {
        #     # 'get_formato':self.get_formato,
        #     'doc_ids': maintenance_equipment_to_report._ids,
        #     'doc_model': report.model,
        #     'docs': maintenance_equipment_to_report,
        # }
        
        # report = self.env['ir.actions.report']._get_report_from_name('studio_customization.studio_report_docume_8f3425e2-e80d-4aca-8c43-e8d80dfbe347')
        # report_values = report._get_report_values(docids=maintenance_equipment_to_report)

        # report_obj = self.env['ir.actions.report']
        # report = report_obj._get_report_from_name('studio_customization.studio_report_docume_8f3425e2-e80d-4aca-8c43-e8d80dfbe347')
        # docargs = {
        #     'doc_ids': maintenance_equipment_to_report._ids,
        #     'doc_model': report.model,
        #     'docs': maintenance_equipment_to_report,
        # }
        # content = report_obj.render('studio_customization.studio_report_docume_8f3425e2-e80d-4aca-8c43-e8d80dfbe347', docargs)
        # content = report._render_qweb_pdf(res_ids=maintenance_equipment_to_report._ids, data=None)

        # docargs = {
        #    'doc_ids': maintenance_equipment_to_report.ids,
        #    'doc_model': maintenance_equipment_to_report.model,
        #    'data': None,
        # }
        # content = self.env['report'].render('studio_customization.studio_report_docume_8f3425e2-e80d-4aca-8c43-e8d80dfbe347', docargs)
        # report.render('maintenance.equipment', docargs)

        # self.env['report'].render('module_name.report_name', docargs)
        # content = self.env.ref('studio_customization.studio_report_docume_8f3425e2-e80d-4aca-8c43-e8d80dfbe347')._render_qweb_pdf(maintenance_equipment_to_report.ids)[0]
        # content = self.env.ref('studio_customization.studio_report_docume_8f3425e2-e80d-4aca-8c43-e8d80dfbe347')._render(report_values)
        # _("Reporte de activos %s %s.pdf" % (str(last_day_of_prev_month), str(start_day_of_prev_month))),

                # email_values = {'email_to': self.partner_id.email,
        #                 'email_from': self.env.user.email}
        # template_id.send_mail(self.id, email_values=email_values, force_send=True)