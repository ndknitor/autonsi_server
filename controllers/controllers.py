from datetime import datetime
from odoo import http
from odoo.http import Response, request
import json
class Home(http.Controller):

    @http.route('/customers/expired', type='http', auth="public", methods=['GET'], csrf=False)
    def customers_by_token(self, **kwargs):
        token = kwargs.get('token')
        if not token:
            return Response(json.dumps({'error': 'Token is required'}), content_type='application/json')

        server = request.env['autonsi.server_server'].sudo().search([('token', '=', token)])
        if not server:
            return Response(json.dumps({'error': 'Invalid token'}), content_type='application/json')

        data = {
            "expiredDate" : server.end_contract_date.isoformat()
        }
        status = 200
        if server.end_contract_date < datetime.now().date():
            status = 403
        return Response(json.dumps(data), content_type='application/json', status=status)