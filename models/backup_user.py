from odoo import models, fields

class backup_user(models.Model):
    _name = 'autonsi.server_user'
    _description = 'autonsi_server.autonsi_server_user'
   
    partner_id = fields.Many2one(
        comodel_name='res.partner',
        string='Partner',
        help='Select a partner',
    )