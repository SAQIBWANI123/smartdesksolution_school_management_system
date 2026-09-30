from odoo import models, fields, api, _

class GradeScale(models.Model):
    _name = 'school.grade.scale'
    _description = 'Grade Scale System'
    _order = 'min_per desc'

    name = fields.Char(string='Grade Letter', required=True) # e.g. A+, A, B, C, F
    min_per = fields.Float(string='Minimum %', required=True)
    max_per = fields.Float(string='Maximum %', required=True)
    gpa = fields.Float(string='GPA Points', required=True) # e.g. 4.0, 3.5
    remarks = fields.Char(string='Remarks / Evaluation') # e.g. Outstanding, Excellent, Pass, Fail


class SchoolExam(models.Model):
    _name = 'school.exam'
    _description = 'School Examination'
    _order = 'date_start desc'

    name = fields.Char(string='Exam Name', required=True) # e.g. Midterm 2026, Final Exam 2026
    code = fields.Char(string='Exam Code', readonly=True, copy=False, default='New')
    academic_year_id = fields.Many2one('school.academic.year', string='Academic Year', required=True)
    term_id = fields.Many2one('school.academic.term', string='Term', domain="[('academic_year_id', '=', academic_year_id)]")
    grade_id = fields.Many2one('school.grade', string='Grade Level', required=True)
    date_start = fields.Date(string='Start Date', required=True)
    date_end = fields.Date(string='End Date', required=True)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('ongoing', 'Ongoing'),
        ('completed', 'Completed'),
    ], string='Status', default='draft')
    description = fields.Text(string='Instructions / Notes')

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('code', 'New') == 'New':
                vals['code'] = self.env['ir.sequence'].next_by_code('school.exam') or 'EXM/0001'
        return super(SchoolExam, self).create(vals_list)


class ExamResult(models.Model):
    _name = 'school.exam.result'
    _description = 'Student Exam Report Card'
    _order = 'exam_id, student_id'

    name = fields.Char(string='Reference', compute='_compute_name', store=True)
    exam_id = fields.Many2one('school.exam', string='Exam', required=True)
    student_id = fields.Many2one('school.student', string='Student', required=True)
    class_id = fields.Many2one('school.class', string='Class / Section', related='student_id.class_id', store=True)
    line_ids = fields.One2many('school.exam.result.line', 'result_id', string='Subject Marks')
    
    total_max_marks = fields.Float(string='Total Max Marks', compute='_compute_scores', store=True)
    total_obtained_marks = fields.Float(string='Total Obtained Marks', compute='_compute_scores', store=True)
    percentage = fields.Float(string='Percentage (%)', compute='_compute_scores', store=True)
    final_grade = fields.Char(string='Grade Letter', compute='_compute_scores', store=True)
    overall_result = fields.Selection([
        ('pass', 'Passed'),
        ('fail', 'Failed'),
    ], string='Result Status', compute='_compute_scores', store=True)
    teacher_comments = fields.Text(string='Teacher Comments')

    @api.depends('exam_id.name', 'student_id.name')
    def _compute_name(self):
        for rec in self:
            if rec.exam_id and rec.student_id:
                rec.name = f"Report Card: {rec.student_id.name} - {rec.exam_id.name}"
            else:
                rec.name = "New Exam Result"

    @api.depends('line_ids.obtained_marks', 'line_ids.max_marks', 'line_ids.result')
    def _compute_scores(self):
        for rec in self:
            tot_max = sum(line.max_marks for line in rec.line_ids)
            tot_obt = sum(line.obtained_marks for line in rec.line_ids)
            rec.total_max_marks = tot_max
            rec.total_obtained_marks = tot_obt
            per = (tot_obt / tot_max * 100.0) if tot_max > 0 else 0.0
            rec.percentage = per
            
            # Check Grade Scale
            scale = self.env['school.grade.scale'].search([('min_per', '<=', per), ('max_per', '>=', per)], limit=1)
            rec.final_grade = scale.name if scale else ('F' if per < 40 else 'A')

            # Overall pass if no line failed
            has_failed_line = any(line.result == 'fail' for line in rec.line_ids)
            rec.overall_result = 'fail' if has_failed_line else 'pass'

    def action_generate_lines(self):
        self.ensure_one()
        self.line_ids.unlink()
        if not self.student_id or not self.student_id.grade_id:
            return
        subjects = self.student_id.grade_id.subject_ids
        lines = []
        for sub in subjects:
            lines.append((0, 0, {
                'subject_id': sub.id,
                'max_marks': sub.max_mark or 100.0,
                'pass_marks': sub.pass_mark or 40.0,
                'obtained_marks': 0.0,
            }))
        self.write({'line_ids': lines})


class ExamResultLine(models.Model):
    _name = 'school.exam.result.line'
    _description = 'Exam Result Marks Line'

    result_id = fields.Many2one('school.exam.result', string='Report Card', ondelete='cascade')
    subject_id = fields.Many2one('school.subject', string='Subject', required=True)
    max_marks = fields.Float(string='Max Marks', default=100.0)
    pass_marks = fields.Float(string='Pass Marks', default=40.0)
    obtained_marks = fields.Float(string='Obtained Marks', default=0.0)
    result = fields.Selection([
        ('pass', 'Pass'),
        ('fail', 'Fail'),
    ], string='Status', compute='_compute_line_result', store=True)

    @api.depends('obtained_marks', 'pass_marks')
    def _compute_line_result(self):
        for rec in self:
            rec.result = 'pass' if rec.obtained_marks >= rec.pass_marks else 'fail'
