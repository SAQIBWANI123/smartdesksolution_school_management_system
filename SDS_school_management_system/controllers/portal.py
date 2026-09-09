import base64

from odoo import http
from odoo.http import request


class SchoolPortal(http.Controller):
    @http.route('/school/admission', type='http', auth='public', website=True)
    def admission_form(self, **kw):
        grades = request.env['school.grade'].sudo().search([], order='sequence, name')
        years = request.env['school.academic.year'].sudo().search([('active', '=', True)])
        return request.render('SDS_school_management_system.portal_admission_form', {'grades': grades, 'years': years})

    @http.route('/school/admission/submit', type='http', auth='public', methods=['POST'], website=True, csrf=True)
    def admission_submit(self, **post):
        values = {key: post.get(key) for key in ('student_name', 'date_of_birth', 'gender', 'guardian_name', 'guardian_relation', 'guardian_email', 'guardian_phone', 'address', 'notes')}
        values['grade_id'] = int(post['grade_id'])
        values['academic_year_id'] = int(post['academic_year_id']) if post.get('academic_year_id') else False
        admission = request.env['school.admission'].sudo().create(values)
        attachments = request.env['ir.attachment']
        for uploaded in request.httprequest.files.getlist('documents'):
            if uploaded and uploaded.filename:
                attachments |= request.env['ir.attachment'].sudo().create({
                    'name': uploaded.filename, 'datas': base64.b64encode(uploaded.read()),
                    'res_model': 'school.admission', 'res_id': admission.id,
                })
        if attachments:
            admission.document_ids = [(6, 0, attachments.ids)]
        return request.render('SDS_school_management_system.portal_admission_success', {'admission': admission})

    @http.route('/my/school/fees', type='http', auth='user', website=True)
    def my_fees(self, **kw):
        email = request.env.user.partner_id.email
        parents = request.env['school.parent'].sudo().search([('email', '=', email)]) if email else request.env['school.parent']
        students = request.env['school.student'].sudo().search([('parent_ids', 'in', parents.ids)])
        fees = request.env['school.student.fee'].sudo().search([('student_id', 'in', students.ids)])
        return request.render('SDS_school_management_system.portal_fee_list', {'students': students, 'fees': fees})
