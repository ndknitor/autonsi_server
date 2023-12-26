import psycopg2
import http.client as http_client
from odoo import models, fields

class server_history(models.Model):
    _name = 'autonsi.server_server_history'
    _description = 'autonsi_server.autonsi_server_server_history'

    name = fields.Char(string="Name")
    date = fields.Date(string="Date")
    host = fields.Char(string="Server's host")
    status = fields.Boolean(string="Status")
    description = fields.Char(string="Description")

    def scheduleTask(self):
        backup_records = self.env['autonsi.server_server'].search([])
        if not backup_records:
            return

        for group in backup_records:
            host = group['host']
            status = self.check_server_status(host)
            name = group['name']
            values = {
                'name' : name,
                'date': fields.Datetime.now(),
                'host': host,
                'status': status,
                'description': "OK" if status else "Down",
            }
            self.create(values)

    def check_server_status(self, host):
        conn = http_client.HTTPConnection(f'{host}:8069',)
        endpoint = f"/check"
        try:
            conn.request("GET", endpoint)
            response = conn.getresponse()
            if response.status != 200:
                return False
            return True
        except Exception as e:
            return False
        finally:
            conn.close()