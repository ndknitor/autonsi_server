import base64
import os
import subprocess
from urllib.parse import urlparse, urlunparse
from odoo import models, fields, api, tools
from odoo.exceptions import ValidationError
from odoo.modules.module import get_module_path

class install_modules(models.Model):

    _name = 'autonsi_install_modules'
    _description = 'Module'

    name = fields.Char(string="Module's name", required=True)
    last_upgrade_date = fields.Date(string="Last upgrade date", readonly=True)
    user = fields.Many2one('res.users',string="User")
    dependent_module = fields.Many2many('autonsi_install_modules', 'module_dependent_rel', 'module_id', 'dependent_module_id', string="Dependent Module")
    github_url = fields.Char(string="Github Url", required=True)
    github_dir = fields.Char(string="Github's Directory")
    github_branch = fields.Char(string="Github's Branch", default="main")
    servers = fields.Many2many(
        comodel_name='autonsi.server_server',
        relation='autonsi_install_modules_rel',
        column1='module_id',
        column2='server_id',
        string='Servers',
    )

    _sql_constraints = [
        ('name_unique', 'unique(name)', "Module's name must be uniqued")
    ]

    def action_install_modules(self):
        try :
            subprocess.run(["git","ls-remote", self.token_url(self.github_url)], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
            for record in self:
                try:
                    for server in record.servers :
                        key_path = os.path.join("/tmp", "privatekey"+server.name)
                        with open(key_path, 'wb') as f:
                            f.write(base64.b64decode(server.private_key))
                        os.chmod(key_path, 0o600)
                        self.remote_install_module(record, server, key_path, True)
                        self.remote_restart_server(server, key_path)
                except e :
                    print(e)
                    raise ValidationError(f"Install module {record.name} to server {server.name} failed")
        except subprocess.CalledProcessError as e:
            print(e)
            raise ValidationError(f"Git access to the repository failed")

    def action_uninstall_module(self):
        try:
            for record in self:
                for server in record.servers :
                    key_path = os.path.join("/tmp", "privatekey"+server.name)
                    with open(key_path, 'wb') as f:
                        f.write(base64.b64decode(server.private_key))
                    os.chmod(key_path, 0o600)
                    self.remote_uninstall_module(record, server, key_path)
                    self.remote_restart_server(server, key_path)
        except subprocess.CalledProcessError as e:
            print(e)
            raise ValidationError(f"Uninstall module failed")

    def remote_install_module(self, module, server, key_path, main_module = False):
        for dependent_module in module.dependent_module:
            self.remote_install_module(dependent_module, server, key_path)
        module_name = 'autonsi_server'
        bash_name = 'remote_install_module.sh'
        bash_path = os.path.join(get_module_path(module_name), bash_name)
        github_dir = module.github_dir
        if (github_dir == False) :
            github_dir = ""
        command = ["bash", bash_path, server.username, key_path, server.host, server.addons_path, self.token_url(module.github_url), server.database, module.name,module.github_branch, main_module.__str__(),github_dir]
        print(command)
        subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)

    def remote_restart_server(self, server, key_path):
        command = ["ssh", '-o', "StrictHostKeyChecking=no" ,"-i", key_path, f'{server.username}@{server.host}', "sudo service odoo-server restart"]
        subprocess.run( command,check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)

    def remote_uninstall_module(self, module,server, key_path) :
        module_name = 'autonsi_server'
        bash_name = 'remote_uninstall_module.sh'
        bash_path = os.path.join(get_module_path(module_name), bash_name)
        command = ["bash", bash_path, server.username, key_path, server.host, server.addons_path,server.database, module.name]
        print(command)
        subprocess.run(command, stderr=subprocess.PIPE, stdout=subprocess.PIPE,check=True)

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

    @api.constrains('dependent_module')
    def _check_circular_dependency(self):
        for record in self:
            if self._has_circular_dependency(record, set()):
                raise ValidationError("Circular dependencies are not allowed")

    def _has_circular_dependency(self, module, visited_modules):
        visited_modules.add(module)
        for dependent in module.dependent_module:
            if dependent in visited_modules or self._has_circular_dependency(dependent, visited_modules):
                return True
        visited_modules.remove(module)
        return False


