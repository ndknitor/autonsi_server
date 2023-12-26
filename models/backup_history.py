from odoo import models, fields

class backup_history(models.Model):
    _name = 'autonsi.server_backup_history'
    _description = 'autonsi_server.autonsi_server_history'

    date = fields.Date(string="Date")
    db_name = fields.Char(string="Database's name")
    device = fields.Char(string="Deivice")
    file_name = fields.Char(string="File name")
    status = fields.Boolean(string="Status", required=True)
