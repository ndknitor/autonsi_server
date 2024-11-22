import base64
import os
import subprocess
import uuid
from odoo.modules.module import get_module_path
from odoo.exceptions import ValidationError
from odoo import api, models, fields
from urllib.parse import urlparse, urlunparse

class server(models.Model):
    _name = 'autonsi.server_server'
    _description = 'autonsi_server_server'

    name = fields.Char(string="Name", required=True)
    company = fields.Many2one('res.partner', required=True)
    start_contract_date = fields.Date(string="Start contract date", required=True)
    end_contract_date = fields.Date(string="End contract date", required=True)
    contract_amount = fields.Integer(string="Contract amount", required=True)
    # amount = fields.Integer(string="amount", required=True)

    username = fields.Char(string="Username", required=True)
    private_key = fields.Binary(string="Private key", required=True)
    host = fields.Char(string="Host", required=True)
    addons_path = fields.Char(string="Addons path",required=True)
    database = fields.Char(string="Database's name", required=True)

    token = fields.Char(string="Token", unique=True)
    @api.model
    def create(self, vals):
        vals['token'] = str(uuid.uuid4())
        return super(server, self).create(vals)

    def action_install_modules(self):
        try :
            modules = self.env['autonsi_install_modules'].search([('servers', 'in', self.id)])
            key_path = os.path.join("/tmp", "privatekey"+self.name)
            with open(key_path, 'wb') as f:
                f.write(base64.b64decode(self.private_key))
            os.chmod(key_path, 0o600)
            for module in modules:
                try :
                    self.remote_install_module(module, self, key_path, True)
                except e :
                    print(e)
                    raise ValidationError(f"Install module {module.name} to server {self.name} failed")
            self.remote_restart_server(self, key_path)
        except subprocess.CalledProcessError as e:
            print(e)
            raise ValidationError(f"Git access to the repository failed")

    def remote_install_module(self, module, server, key_path, main_module = False):
        for dependent_module in module.dependent_module:
            self.remote_install_module(dependent_module, server, key_path)
        module_name = 'autonsi_server'
        bash_name = 'install_script.sh'
        bash_path = os.path.join(get_module_path(module_name), bash_name)
        github_dir = module.github_dir
        if (github_dir == False) :
            github_dir = ""
        command = ["bash", bash_path, server.username, key_path, server.host, server.addons_path, self.token_url(module.github_url), server.database, module.name, server.name, main_module.__str__(),github_dir]
        print(command)
        subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)

    def remote_restart_server(self, server, key_path):
        command = ["ssh", '-o', "StrictHostKeyChecking=no" ,"-i", key_path, f'{server.username}@{server.host}', f"docker compose restart -f {server.addons_path}/docker-compose.yaml"]
        subprocess.run( command,check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)

    def token_url(self,github_url):
        github_token = self.env['ir.config_parameter'].sudo().get_param('autonsi_install_modules.setting_github_token')
        if github_token is False:
            return github_url
        url_parts = urlparse(github_url)

        netloc_parts = url_parts.netloc.split('.')
        if url_parts.netloc != 'github.com' and len(netloc_parts) > 1:
            netloc_parts[0] = github_token
            url_parts = url_parts._replace(netloc='.'.join(netloc_parts))
        else:
            url_parts = url_parts._replace(netloc=f"{github_token}@github.com")

        clone_url = urlunparse(url_parts)

        return clone_url