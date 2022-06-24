# -*- coding: utf-8 -*-
# from odoo import http


# class CmsBc(http.Controller):
#     @http.route('/cms_bc/cms_bc/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/cms_bc/cms_bc/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('cms_bc.listing', {
#             'root': '/cms_bc/cms_bc',
#             'objects': http.request.env['cms_bc.cms_bc'].search([]),
#         })

#     @http.route('/cms_bc/cms_bc/objects/<model("cms_bc.cms_bc"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('cms_bc.object', {
#             'object': obj
#         })
