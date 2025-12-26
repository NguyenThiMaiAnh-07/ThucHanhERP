
from odoo import models, fields, api
from datetime import date

class PediatricPatient(models.Model):
    _name = 'pediatric.patient'
    _description = 'Bệnh nhân nhi khoa'

    name = fields.Char(string='Họ và tên', required=True)

    family_member_id = fields.Many2one(
        'pediatric.family.member',
        string="Người nhà"
    )

    gender = fields.Selection([
        ('male', 'Nam'),
        ('female', 'Nữ'),
    ], string='Giới tính')

    date_of_birth = fields.Date(string='Ngày sinh')
    age = fields.Integer(string='Tuổi', compute='_compute_age', store=True)


    phone = fields.Char(string='Số điện thoại')
    address = fields.Char(string='Địa chỉ')
    doctor_id = fields.Many2one('pediatric.doctor', string='Bác sĩ phụ trách')
    medical_history = fields.Text(string='Tiền sử bệnh')
    note = fields.Text(string='Ghi chú')

    blood_group = fields.Selection([
        ('a+', 'A+'),
        ('a-', 'A-'),
        ('b+', 'B+'),
        ('b-', 'B-'),
        ('ab+', 'AB+'),
        ('ab-', 'AB-'),
        ('o+', 'O+'),
        ('o-', 'O-'),
        ('unknown', 'Chưa rõ'),
    ], string="Nhóm máu", default='unknown')

    
    bhyt_code = fields.Char(string="Mã số BHYT")
    bhyt_valid_from = fields.Date(string="Giá trị từ ngày")
    bhyt_valid_to = fields.Date(string="Giá trị đến ngày")

    
    queue_ids = fields.One2many(
        'reception.queue', 'patient_id',
        string="Các lượt vào hàng chờ"
    )
    queue_count = fields.Integer(
        compute='_compute_queue_count',
        string="Số lượt hàng chờ"
    )


    booking_ids = fields.One2many(
        'pediatric.booking', 'patient_id',
        string="Phiếu đặt lịch"
    )
    booking_count = fields.Integer(
        compute='_compute_booking_count',
        string="Số phiếu đặt lịch"
    )


    appointment_ids = fields.One2many(
        'pediatric.appointment', 'patient_id',
        string="Lịch tái khám"
    )
    appointment_count = fields.Integer(
        compute='_compute_appointment_count',
        string="Số lịch tái khám"
    )

  
    @api.depends('queue_ids')
    def _compute_queue_count(self):
        for r in self:
            r.queue_count = len(r.queue_ids)

    @api.depends('booking_ids')
    def _compute_booking_count(self):
        for r in self:
            r.booking_count = len(r.booking_ids)

    @api.depends('appointment_ids')
    def _compute_appointment_count(self):
        for r in self:
            r.appointment_count = len(r.appointment_ids)

    @api.depends('date_of_birth')
    def _compute_age(self):
        for rec in self:
            if rec.date_of_birth:
                today = date.today()
                rec.age = today.year - rec.date_of_birth.year - (
                    (today.month, today.day) < (rec.date_of_birth.month, rec.date_of_birth.day)
                )
            else:
                rec.age = 0


    def action_open_queues(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Hàng chờ của bệnh nhi',
            'res_model': 'reception.queue',
            'view_mode': 'list,form',
            'domain': [('patient_id', '=', self.id)],
            'context': {'default_patient_id': self.id},
            'target': 'current',
        }

    def action_open_bookings(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Phiếu đặt lịch của bệnh nhi',
            'res_model': 'pediatric.booking',
            'view_mode': 'list,form',
            'domain': [('patient_id', '=', self.id)],
            'context': {'default_patient_id': self.id},
            'target': 'current',
        }

    def action_open_appointments(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Lịch tái khám của bệnh nhi',
            'res_model': 'pediatric.appointment',
            'view_mode': 'list,form',
            'domain': [('patient_id', '=', self.id)],
            'context': {'default_patient_id': self.id},
            'target': 'current',
        }
