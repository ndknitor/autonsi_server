from odoo import api, models, fields

class install_module_setting(models.TransientModel):
    _name = 'autonsi_install_modules.settings'
    _description = 'autonsi_install_modules.settings'
    github_token = fields.Char(string="Github's token")
    def setting(self):
        self.env['ir.config_parameter'].set_param('autonsi_install_modules.setting_github_token', self.github_token)

        # def _compute_port(self):
    #     port = self.env['ir.config_parameter'].sudo().get_param('autonsi_server.setting_port')
    #     if (port is False)  :
    #         return 9000
    #     return port
    # def _compute_remote_controlled(self):
    #     flag = self.env['ir.config_parameter'].sudo().get_param('autonsi_server.setting_remote_controlled')
    #     if (flag is False)  :
    #         return False
    #     return flag
    
    
    # port = fields.Integer(string="Port", default=_compute_port)
    # remote_controlled = fields.Boolean(string="Remote controlled", default=_compute_remote_controlled)

    # def _auto_init(self):
    #     if self.env.context.get('models_to_check'):
    #         print(self.env.context.get('models_to_check'))
    #         self.startRPC()

    # def startRPC(self):
    #     server_port = self._compute_port()
    #     server = SimpleXMLRPCServer(('0.0.0.0', server_port))
    #     server.register_function(self.clone_and_install_module, 'clone_and_install_module')
    #     server_thread = threading.Thread(target=server.serve_forever)
    #     server_thread.daemon = True
    #     server_thread.start()
    #     return True
    
    # def clone_and_install_module(self, module_name):
    #     addons_path = tools.config['addons_path']
    #     # install_path = os.path.join(addons_path, module_name)
    #     # subprocess.run(['git', 'clone', '-b', github_branch, github_url, install_path])
    #     # # Install the module in Odoo
    #     # self.env['ir.module.module'].button_immediate_install([module_name])

    # def setting(self):
    #     self.env['ir.config_parameter'].set_param('autonsi_server.setting_port', self.port)
    #     self.env['ir.config_parameter'].set_param('autonsi_server.setting_remote_controlled_', self.remote_controlled)
    
    # def open_doc(self) :
    #     url = "/autonsi_server/static/guideline.pdf"
    #     # Open the URL in a new browser tab/window
    #     return {
    #         'type': 'ir.actions.act_url',
    #         'url': url,
    #         'target': 'new',
    #     }