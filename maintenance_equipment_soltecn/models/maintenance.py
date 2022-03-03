from odoo import api, fields, models
from datetime import date, timedelta

class MaintenanceEquipment(models.Model):
    _inherit = 'maintenance.equipment'

    def _enviar_reporte_activos(self):
        return self.send_email_custom()

    @api.model
    def send_email_custom(self):
        for maintenance in self:
            template_id = maintenance.env['mail.template'].search([('id', '=', 13)], limit=1).id

            last_day_of_prev_month = date.today().replace(day=1) - timedelta(days=1)
            start_day_of_prev_month = date.today().replace(day=1) - timedelta(days=last_day_of_prev_month.day)
            maintenance_equipment_to_report = maintenance.search([('__last_update', '>=', start_day_of_prev_month),('__last_update', '<=', last_day_of_prev_month)])

            content, content_type = maintenance.env.ref('studio_customization.studio_report_docume_8f3425e2-e80d-4aca-8c43-e8d80dfbe347')._render(maintenance_equipment_to_report.ids)

            data_id = maintenance.env['ir.attachment'].create({
                'name': _("Reporte de activos (%s - %s).pdf", (str(last_day_of_prev_month), str(start_day_of_prev_month))),
                'type': 'binary',
                'datas': base64.encodebytes(content),
                'res_model': maintenance._name,
                'res_id': maintenance.id
            })

            template_id.attachment_ids = [(6, 0, [data_id.id])]
            maintenance.env['mail.template'].browse(template_id).send_mail(maintenance.id, force_send=True)
            # email_values = {'email_to': self.partner_id.email,
            #                 'email_from': self.env.user.email}
            # template_id.send_mail(self.id, email_values=email_values, force_send=True)
            template_id.attachment_ids = [(3, data_id.id)]
        return True