# -*- coding: utf-8 -*-
# from odoo import http


# class PediatricClinic(http.Controller):
#     @http.route('/pediatric_clinic/pediatric_clinic', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/pediatric_clinic/pediatric_clinic/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('pediatric_clinic.listing', {
#             'root': '/pediatric_clinic/pediatric_clinic',
#             'objects': http.request.env['pediatric_clinic.pediatric_clinic'].search([]),
#         })

#     @http.route('/pediatric_clinic/pediatric_clinic/objects/<model("pediatric_clinic.pediatric_clinic"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('pediatric_clinic.object', {
#             'object': obj
#         })

