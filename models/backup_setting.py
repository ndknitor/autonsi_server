from odoo import  models, fields

class backup_setting(models.TransientModel):
    _name = 'autonsi_server.settings'
    _description = 'autonsi_server.autonsi_server_settings'
    github_token = fields.Char(string="Github's token")
        
    def setting(self):
        self.env['ir.config_parameter'].set_param('autonsi_server.setting_github_token', self.github_token)