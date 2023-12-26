from datetime import datetime
from odoo import http
from odoo.http import Response, request
import json
class Home(http.Controller):

    def _serialize_module(self, module):
        serialized_module = {
            'name': module.name,
            'dependent_module': [],
        }

        for dependent in module.dependent_module:
            serialized_module['dependent_module'].append(self._serialize_module(dependent))

        return serialized_module

    @http.route('/customers/date-of-use', type='http', auth="public", methods=['GET'], csrf=False)
    def customers_by_token(self, **kwargs):
        token = kwargs.get('token')
        print(token)
        if not token:
            return Response(json.dumps({'error': 'Token is required'}), content_type='application/json')

        server = request.env['autonsi.server_server'].sudo().search([('token', '=', token)])
        if not server:
            return Response(json.dumps({'error': 'Invalid token'}), content_type='application/json')

        customer_data = {
            "dateOfUse" : server.end_contract_date.isoformat()
        }
        status = 200
        if server.end_contract_date < datetime.now().date():
            status = 403
        return Response(json.dumps(customer_data), content_type='application/json', status=status)