from odoo import models, fields

class contract_history(models.Model):
    _name = 'autonsi.server_contract_history'
    _description = 'autonsi_server.autonsi_server_history'

    date = fields.Date(string="Contract date")
    sale_order = fields.Char(string="Sale order")
    product = fields.Char(string="Product")
    description = fields.Char(string="Description")
    amount = fields.Integer(string="Amount")
    recevied_amount = fields.Integer(string="Recevied amount")