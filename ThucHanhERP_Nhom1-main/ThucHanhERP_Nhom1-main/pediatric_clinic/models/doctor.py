
from odoo import models, fields, api


class PediatricDoctor(models.Model):
    _name = 'pediatric.doctor'
    _description = 'Bàn làm việc Bác sĩ'


    _inherits = {'hr.employee': 'employee_id'}


    employee_id = fields.Many2one(
        'hr.employee',
        required=True,
        ondelete='cascade',
        string="Hồ sơ nhân viên",
        domain="['|', ('department_id.name', 'ilike', 'Bác sĩ'), "
               "('department_id.name', 'ilike', 'Doctor')]",
        help="Chọn nhân viên thuộc phòng ban Bác sĩ / Doctor"
    )


    partner_id = fields.Many2one(
        'res.partner',
        related='employee_id.user_id.partner_id',
        readonly=True,
        store=True,
        string="Liên hệ hệ thống"
    )

    @api.model
    def default_get(self, fields_list):
        res = super(PediatricDoctor, self).default_get(fields_list)

        department = self.env['hr.department'].search([
            '|', ('name', 'ilike', 'Bác sĩ'), ('name', 'ilike', 'Doctor')
        ], limit=1)
        if department:
            res['department_id'] = department.id
        return res

    specialty_id = fields.Many2one(
        'pediatric.specialty',
        string='Chuyên khoa',
        required=True,
        help="Chuyên khoa mà bác sĩ phụ trách"
    )


    specialization = fields.Char(
        string='Chuyên khoa chi tiết',
        help="Ví dụ: Nhi Hô hấp, Nhi Tim mạch..."
    )


    employee_code = fields.Char(
        string="Mã nhân viên",
        related='employee_id.barcode',
        store=True,
        readonly=False,
        help="Lấy từ Badge ID của nhân viên (Employee)"
    )

    degree = fields.Selection(
        [
            ('bs', 'Bác sĩ'),
            ('ths', 'Thạc sĩ'),
            ('ts', 'Tiến sĩ'),
            ('ck1', 'Chuyên khoa I'),
            ('ck2', 'Chuyên khoa II')
        ],
        string='Học vị / Học hàm'
    )

    license_number = fields.Char(string='Số chứng chỉ hành nghề')
    consultation_fee = fields.Float(string='Phí khám (VNĐ)')
    is_available = fields.Boolean(string='Đang nhận khám', default=True)

    phone_contact = fields.Char(
        string="Số điện thoại liên hệ",
        related='employee_id.work_phone',
        store=True,
        readonly=False,
        help="Kế thừa từ Work Phone của nhân viên"
    )

    email_contact = fields.Char(
        string="Email liên hệ",
        related='employee_id.work_email',
        store=True,
        readonly=False,
        help="Kế thừa từ Work Email của nhân viên"
    )

    insurance_code = fields.Char(
        string="Mã số BHYT",
        related='employee_id.ssnid',
        store=True,
        readonly=False,
        help="Kế thừa từ SSN No của nhân viên"
    )


    insurance_start = fields.Date(string="Giá trị từ ngày")
    insurance_end = fields.Date(string="Giá trị đến ngày")


    issue_date = fields.Date(string="Ngày cấp")
    issue_place = fields.Char(string="Nơi cấp")

 
    morning_start = fields.Float(string="Giờ bắt đầu sáng", default=7.5)
    morning_end = fields.Float(string="Giờ kết thúc sáng", default=11.5)
    afternoon_start = fields.Float(string="Giờ bắt đầu chiều", default=13.5)
    afternoon_end = fields.Float(string="Giờ kết thúc chiều", default=17.0)
    evening_start = fields.Float(string="Giờ bắt đầu tối", default=18.0)
    evening_end = fields.Float(string="Giờ kết thúc tối", default=20.0)

    mon_morning = fields.Boolean(string="Thứ 2 sáng")
    mon_afternoon = fields.Boolean(string="Thứ 2 chiều")
    mon_evening = fields.Boolean(string="Thứ 2 tối")

    tue_morning = fields.Boolean(string="Thứ 3 sáng")
    tue_afternoon = fields.Boolean(string="Thứ 3 chiều")
    tue_evening = fields.Boolean(string="Thứ 3 tối")

    wed_morning = fields.Boolean(string="Thứ 4 sáng")
    wed_afternoon = fields.Boolean(string="Thứ 4 chiều")
    wed_evening = fields.Boolean(string="Thứ 4 tối")

    thu_morning = fields.Boolean(string="Thứ 5 sáng")
    thu_afternoon = fields.Boolean(string="Thứ 5 chiều")
    thu_evening = fields.Boolean(string="Thứ 5 tối")

    fri_morning = fields.Boolean(string="Thứ 6 sáng")
    fri_afternoon = fields.Boolean(string="Thứ 6 chiều")
    fri_evening = fields.Boolean(string="Thứ 6 tối")

    sat_morning = fields.Boolean(string="Thứ 7 sáng")
    sat_afternoon = fields.Boolean(string="Thứ 7 chiều")
    sat_evening = fields.Boolean(string="Thứ 7 tối")

    sun_morning = fields.Boolean(string="Chủ nhật sáng")
    sun_afternoon = fields.Boolean(string="Chủ nhật chiều")
    sun_evening = fields.Boolean(string="Chủ nhật tối")


    schedule_ids = fields.One2many(
        'pediatric.doctor.schedule',
        'doctor_id',
        string="Lịch làm việc theo ca"
    )

    appointment_ids = fields.One2many(
        'pediatric.appointment',
        'doctor_id',
        string='Lịch tái khám / đang điều trị'
    )

    booking_ids = fields.One2many(
        'pediatric.booking',
        'doctor_id',
        string='Yêu cầu đặt lịch'
    )

    total_appointments = fields.Integer(
        string='Tổng ca tái khám',
        compute='_compute_totals'
    )

    total_bookings = fields.Integer(
        string='Tổng lượt đặt lịch',
        compute='_compute_totals'
    )

    total_visits = fields.Integer(
        string='Tổng lịch khám',
        compute='_compute_totals'
    )

    @api.depends('appointment_ids', 'booking_ids')
    def _compute_totals(self):
        for rec in self:
            rec.total_appointments = len(rec.appointment_ids)
            rec.total_bookings = len(rec.booking_ids)
            rec.total_visits = rec.total_appointments + rec.total_bookings

    def action_open_doctor_calendar(self):
        self.ensure_one()
        return {
            'name': 'Lịch làm việc của bác sĩ',
            'type': 'ir.actions.act_window',
            'res_model': 'calendar.event',
            'view_mode': 'calendar,list,form',
            'domain': [('partner_ids', 'in', [self.partner_id.id])] if self.partner_id else [],
            'context': {'default_mode': 'week'}
        }

    def action_view_employee_profile(self):
        self.ensure_one()
        return {
            'name': 'Hồ sơ nhân sự',
            'type': 'ir.actions.act_window',
            'res_model': 'hr.employee',
            'res_id': self.employee_id.id,
            'view_mode': 'form',
            'target': 'current',
        }


class PediatricDoctorSchedule(models.Model):
    _name = 'pediatric.doctor.schedule'
    _description = 'Lịch làm việc Bác sĩ theo ca'

    doctor_id = fields.Many2one(
        'pediatric.doctor',
        string="Bác sĩ",
        ondelete='cascade'
    )

    weekday = fields.Selection(
        [
            ('mon', 'Thứ 2'),
            ('tue', 'Thứ 3'),
            ('wed', 'Thứ 4'),
            ('thu', 'Thứ 5'),
            ('fri', 'Thứ 6'),
            ('sat', 'Thứ 7'),
            ('sun', 'Chủ nhật'),
        ],
        string="Ngày làm việc",
        required=True,
    )

    shift = fields.Selection(
        [
            ('morning', 'Ca sáng'),
            ('afternoon', 'Ca chiều'),
            ('full', 'Cả ngày'),
        ],
        string="Ca làm việc",
        required=True,
    )

    time_start = fields.Float(string="Giờ bắt đầu", default=7.0)
    time_end = fields.Float(string="Giờ kết thúc", default=17.0)

    capacity = fields.Integer(
        string="Số bệnh nhân có thể tiếp nhận",
        default=0,
        help="Số bệnh nhân tối đa có thể tiếp nhận trong ca này"
    )

    @api.onchange('shift')
    def _onchange_shift(self):
        for rec in self:
            if rec.shift == 'morning':
                rec.time_start = 7.0   
                rec.time_end = 11.5    
            elif rec.shift == 'afternoon':
                rec.time_start = 13.0  
                rec.time_end = 17.0    
            elif rec.shift == 'full':
                rec.time_start = 7.0
                rec.time_end = 17.0
