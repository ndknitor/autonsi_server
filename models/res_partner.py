from odoo import models, fields

class ResPartnerCustom(models.Model):
    _inherit = 'res.partner'
        
    service_file = fields.Binary(string="Service file")
    folder_id = fields.Char(string="Folder Id")
    # project_id = fields.Char(string="Project's Id")
    # private_key_id = fields.Char(string="Private key Id")
    # private_key = fields.Char(string="Private key")
    # client_email = fields.Char(string="Client email")
    # client_id = fields.Char(string="Client id")