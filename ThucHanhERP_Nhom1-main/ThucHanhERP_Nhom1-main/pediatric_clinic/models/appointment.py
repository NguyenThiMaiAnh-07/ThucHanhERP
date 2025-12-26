
from odoo import models, fields, api, exceptions, _
from datetime import datetime, timedelta, time
import random
import string


class PediatricAppointment(models.Model):
    _name = 'pediatric.appointment'
    _description = 'Lịch tái khám'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'appointment_date desc, appointment_datetime desc'

    name = fields.Char(
        string='Mã phiếu',
        readonly=True,
        copy=False,
        default=lambda self: _('New')
    )

    patient_id = fields.Many2one(
        'pediatric.patient',
        string='Bệnh nhi',
        required=True,
        ondelete='cascade',
        tracking=True
    )

    family_member_id = fields.Many2one(
        'pediatric.family.member',
        string="Người nhà / Người giám hộ",
        ondelete='set null',
        tracking=True,
    )

    doctor_id = fields.Many2one(
        'pediatric.doctor',
        string='Bác sĩ phụ trách',
        tracking=True
    )

    specialty_id = fields.Many2one(
        'pediatric.specialty',
        string='Chuyên khoa',
        related='doctor_id.specialty_id',
        store=True,
        readonly=True,
    )

    fee = fields.Float(string="Phí khám", tracking=True)

    @api.onchange('doctor_id')
    def _onchange_doctor_id(self):
        for rec in self:
            if rec.doctor_id:
                rec.fee = rec.doctor_id.consultation_fee

    appointment_date = fields.Date(
        string='Ngày khám',
        required=True,
        tracking=True
    )

    session = fields.Selection(
        [
            ('morning', 'Buổi sáng'),
            ('afternoon', 'Buổi chiều'),
        ],
        string='Buổi khám',
        required=True,
        tracking=True
    )

    appointment_datetime = fields.Datetime(
        string='Thời gian hẹn',
        compute='_compute_appointment_datetime',
        store=True
    )

    duration = fields.Integer(string='Thời lượng (phút)', default=15)

    @api.depends('appointment_date', 'session')
    def _compute_appointment_datetime(self):
        for rec in self:
            if rec.appointment_date and rec.session:
                base_time = time(9, 0) if rec.session == 'morning' else time(14, 0)
                rec.appointment_datetime = datetime.combine(rec.appointment_date, base_time)
            else:
                rec.appointment_datetime = False

    visit_type = fields.Selection(
        [
            ('first', 'Khám lần đầu'),
            ('followup', 'Tái khám'),
        ],
        default='followup',
        tracking=True
    )

    date_end = fields.Datetime(compute='_compute_date_end', store=True)

    @api.depends('appointment_datetime', 'duration')
    def _compute_date_end(self):
        for rec in self:
            if rec.appointment_datetime:
                rec.date_end = rec.appointment_datetime + timedelta(
                    minutes=rec.duration or 15
                )
            else:
                rec.date_end = False

    @api.onchange('patient_id')
    def _onchange_patient_id(self):
        for rec in self:
            if rec.patient_id and rec.patient_id.family_member_id:
                fam = rec.patient_id.family_member_id
                rec.family_member_id = fam
                rec.parent_name = fam.name or False
                rec.parent_phone = fam.phone or False
                rec.parent_email = fam.email or False

    @api.constrains('doctor_id', 'appointment_date', 'session')
    def _check_doctor_schedule(self):
        for rec in self:
            if not rec.doctor_id or not rec.appointment_date or not rec.session:
                continue

            weekday = ['mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun'][rec.appointment_date.weekday()]
            shifts = ['full']
            shifts.append('morning' if rec.session == 'morning' else 'afternoon')

            exists = self.env['pediatric.doctor.schedule'].search_count([
                ('doctor_id', '=', rec.doctor_id.id),
                ('weekday', '=', weekday),
                ('shift', 'in', shifts),
            ])

            if not exists:
                raise exceptions.ValidationError(
                    _("Bác sĩ %s không có lịch rảnh buổi %s ngày %s.")
                    % (rec.doctor_id.name,
                       "sáng" if rec.session == 'morning' else "chiều",
                       rec.appointment_date.strftime('%d/%m/%Y'))
                )

    @api.constrains('doctor_id', 'appointment_datetime', 'duration')
    def _check_doctor_availability(self):
        for rec in self:
            if rec.doctor_id and rec.appointment_datetime and rec.state not in ['cancel', 'done']:
                domain = [
                    ('id', '!=', rec.id),
                    ('doctor_id', '=', rec.doctor_id.id),
                    ('state', 'in', ['confirmed', 'waiting', 'in_consult']),
                    ('appointment_datetime', '<', rec.date_end),
                    ('date_end', '>', rec.appointment_datetime),
                ]
                if self.search_count(domain) > 0:
                    raise exceptions.ValidationError(
                        _("Bác sĩ %s đã bận trong khung giờ này!") % rec.doctor_id.name
                    )

    state = fields.Selection(
        [
            ('draft', 'Nháp'),
            ('confirmed', 'Đã xác nhận'),
            ('waiting', 'Đang chờ'),
            ('in_consult', 'Đang khám'),
            ('done', 'Hoàn tất'),
            ('cancel', 'Hủy'),
        ],
        default='draft',
        tracking=True
    )

    queue_id = fields.Many2one('reception.queue', string="Nguồn hàng chờ", readonly=True)

    weight = fields.Float()
    height = fields.Float()
    temperature = fields.Float()
    pulse = fields.Integer()
    respiration = fields.Integer()
    blood_pressure = fields.Char()
    symptoms = fields.Text()
    diagnosis = fields.Text()
    previous_diagnosis = fields.Text()
    treatment = fields.Text()
    medications = fields.Text()
    allergies = fields.Text()
    lab_results = fields.Text()
    imaging_results = fields.Text()
    followup_instructions = fields.Text()
    vaccination_status = fields.Text()

    parent_name = fields.Char()
    parent_phone = fields.Char()
    parent_email = fields.Char()
    emergency_contact = fields.Char()
    notes = fields.Text()
    referral = fields.Char()
    insurance = fields.Char()
    room = fields.Char()
    payment_status = fields.Selection(
        [('unpaid', 'Chưa thanh toán'), ('paid', 'Đã thanh toán')]
    )
    priority = fields.Selection(
        [('low', 'Thấp'), ('medium', 'Trung bình'), ('high', 'Cao')]
    )
    diet = fields.Text()
    activity_level = fields.Text()
    notes_doctor = fields.Text()
    next_followup_date = fields.Datetime()

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', _('New')) == _('New'):
                vals['name'] = self._generate_unique_code()
        return super().create(vals_list)

    def _generate_unique_code(self):
        for _ in range(100):
            code = 'PK-' + ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
            if not self.search([('name', '=', code)], limit=1):
                return code
        raise exceptions.UserError(_('Không thể tạo mã, vui lòng thử lại.'))


    def action_confirm(self):
        for rec in self:
            rec._check_doctor_availability()
            rec.state = 'confirmed'
        return True

    def action_start_consult(self):
        for rec in self:
            rec.state = 'in_consult'

    def action_finish_consult(self):
        for rec in self:
            rec.state = 'done'
            if rec.queue_id:
                rec.queue_id.state = 'done'

    def action_cancel(self):
        for rec in self:
            rec.state = 'cancel'
            if rec.queue_id:
                rec.queue_id.state = 'cancel'
