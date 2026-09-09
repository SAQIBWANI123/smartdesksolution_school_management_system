import base64
from datetime import date

from odoo import http
from odoo.http import request


class SchoolPortal(http.Controller):
    _MAX_DOCUMENT_SIZE = 5 * 1024 * 1024
    _MAX_DOCUMENTS = 10
    _ALLOWED_DOCUMENT_EXTENSIONS = {'.pdf', '.jpg', '.jpeg', '.png', '.doc', '.docx'}
    _FEE_STATE_LABELS = {
        'draft': 'Draft',
        'posted': 'Posted / Invoiced',
        'paid': 'Fully Paid',
        'partially_paid': 'Partially Paid',
        'cancelled': 'Cancelled',
    }

    def _admission_form_values(self, error=None):
        grades = request.env['school.grade'].sudo().search([], order='sequence, name')
        years = request.env['school.academic.year'].sudo().search([('active', '=', True)], order='date_start desc')
        values = {'grades': grades, 'years': years}
        if error:
            values['error'] = error
        return values

    @http.route('/school/admission', type='http', auth='public', website=True)
    def admission_form(self, **kw):
        return request.render(
            'SDS_school_management_system.portal_admission_form',
            self._admission_form_values(),
        )

    @http.route('/school/admission/submit', type='http', auth='public', methods=['POST'], website=True, csrf=True)
    def admission_submit(self, **post):
        required_fields = ('student_name', 'date_of_birth', 'gender', 'grade_id', 'guardian_name', 'guardian_email', 'guardian_phone')
        if any(not post.get(field) for field in required_fields):
            return request.render(
                'SDS_school_management_system.portal_admission_form',
                self._admission_form_values('Please complete all required fields.'),
                status=400,
            )

        try:
            grade = request.env['school.grade'].sudo().browse(int(post['grade_id']))
            academic_year = request.env['school.academic.year'].sudo().search([
                ('id', '=', int(post['academic_year_id'])), ('active', '=', True),
            ], limit=1) if post.get('academic_year_id') else False
            date.fromisoformat(post['date_of_birth'])
        except (TypeError, ValueError):
            grade = academic_year = False

        if not grade or not grade.exists() or (academic_year and not academic_year.exists()):
            return request.render(
                'SDS_school_management_system.portal_admission_form',
                self._admission_form_values('Please select a valid grade and academic year.'),
                status=400,
            )

        uploads = request.httprequest.files.getlist('documents')
        if len(uploads) > self._MAX_DOCUMENTS:
            return request.render(
                'SDS_school_management_system.portal_admission_form',
                self._admission_form_values('You can upload up to 10 documents.'),
                status=400,
            )

        values = {key: post.get(key) for key in ('student_name', 'date_of_birth', 'gender', 'guardian_name', 'guardian_relation', 'guardian_email', 'guardian_phone', 'address', 'notes')}
        values['grade_id'] = grade.id
        values['academic_year_id'] = academic_year.id if academic_year else False

        upload_data = []
        for uploaded in uploads:
            if not uploaded or not uploaded.filename:
                continue
            extension = '.' + uploaded.filename.rsplit('.', 1)[-1].lower() if '.' in uploaded.filename else ''
            content = uploaded.read(self._MAX_DOCUMENT_SIZE + 1)
            if extension not in self._ALLOWED_DOCUMENT_EXTENSIONS or len(content) > self._MAX_DOCUMENT_SIZE:
                return request.render(
                    'SDS_school_management_system.portal_admission_form',
                    self._admission_form_values('Documents must be PDF, Word, JPG or PNG files under 5 MB each.'),
                    status=400,
                )
            upload_data.append((uploaded.filename, content))

        admission = request.env['school.admission'].sudo().create(values)
        attachment_ids = []
        for filename, content in upload_data:
            attachment = request.env['ir.attachment'].sudo().create({
                    'name': filename, 'datas': base64.b64encode(content),
                    'res_model': 'school.admission', 'res_id': admission.id,
                })
            attachment_ids.append(attachment.id)
        if attachment_ids:
            admission.document_ids = [(6, 0, attachment_ids)]
        return request.render('SDS_school_management_system.portal_admission_success', {'admission': admission})

    @http.route('/my/school/fees', type='http', auth='user', website=True)
    def my_fees(self, **kw):
        parents = request.env['school.parent'].sudo().search([('user_id', '=', request.env.user.id)])
        students = request.env['school.student'].sudo().search([('parent_ids', 'in', parents.ids)])
        selected_student = students.filtered(lambda student: student.id == int(kw['student_id'])) if kw.get('student_id', '').isdigit() else students
        if kw.get('student_id') and not selected_student:
            return request.not_found()
        fees = request.env['school.student.fee'].sudo().search([('student_id', 'in', selected_student.ids)])
        return request.render('SDS_school_management_system.portal_fee_list', {
            'students': students,
            'fees': fees,
            'total_amount': sum(fee.amount_total for fee in fees),
            'total_paid': sum(fee.amount_paid for fee in fees),
            'total_due': sum(fee.amount_due for fee in fees),
            'fee_state_labels': self._FEE_STATE_LABELS,
        })

    def _portal_students(self):
        parents = request.env['school.parent'].sudo().search([('user_id', '=', request.env.user.id)])
        return request.env['school.student'].sudo().search([('parent_ids', 'in', parents.ids)], order='name')

    @http.route('/my/school/students', type='http', auth='user', website=True)
    def my_students(self, **kw):
        return request.render('SDS_school_management_system.portal_student_list', {
            'students': self._portal_students(),
        })

    @http.route('/my/school/students/<int:student_id>', type='http', auth='user', website=True)
    def my_student_detail(self, student_id, **kw):
        student = self._portal_students().filtered(lambda record: record.id == student_id)
        if not student:
            return request.not_found()
        student = student[0]
        attendance = request.env['school.attendance.line'].sudo().search([
            ('student_id', '=', student.id), ('attendance_id.state', '=', 'done'),
        ], order='attendance_id.date desc')
        results = request.env['school.exam.result'].sudo().search([
            ('student_id', '=', student.id),
        ], order='exam_id.date_start desc')
        return request.render('SDS_school_management_system.portal_student_detail', {
            'student': student,
            'attendance': attendance,
            'results': results,
        })

    @http.route('/my/school/fees/<int:fee_id>', type='http', auth='user', website=True)
    def my_fee_detail(self, fee_id, **kw):
        parents = request.env['school.parent'].sudo().search([('user_id', '=', request.env.user.id)])
        students = request.env['school.student'].sudo().search([('parent_ids', 'in', parents.ids)])
        fee = request.env['school.student.fee'].sudo().search([
            ('id', '=', fee_id), ('student_id', 'in', students.ids),
        ], limit=1)
        if not fee:
            return request.not_found()
        return request.render('SDS_school_management_system.portal_fee_detail', {
            'fee': fee,
            'fee_state_labels': self._FEE_STATE_LABELS,
        })
