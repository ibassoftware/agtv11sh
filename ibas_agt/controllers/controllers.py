# -*- coding: utf-8 -*-
from odoo import http

# class IbasAgt(http.Controller):
#     @http.route('/ibas_agt/ibas_agt/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/ibas_agt/ibas_agt/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('ibas_agt.listing', {
#             'root': '/ibas_agt/ibas_agt',
#             'objects': http.request.env['ibas_agt.ibas_agt'].search([]),
#         })

#     @http.route('/ibas_agt/ibas_agt/objects/<model("ibas_agt.ibas_agt"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('ibas_agt.object', {
#             'object': obj
#         })