
from odoo import models, fields, api
class PediatricReceptionist(models.Model):
    _name = 'pediatric.receptionist'
    _description = 'Lễ tân'

    employee_id = fields.Many2one(
        'hr.employee',
        string='Nhân viên lễ tân',
        ondelete='set null',
        domain=[('department_id.name', '=', 'Receptionist')],
        help="Chọn nhân viên lễ tân từ danh sách nhân sự"
    )

    partner_id = fields.Many2one(
        'res.partner',
        related='employee_id.user_id.partner_id',
        store=True,
        readonly=True,
        string="Liên hệ hệ thống"
    )

    name = fields.Char(
        related='employee_id.name',
        store=True,
        string="Họ tên",
        readonly=True,
    )

    employee_phone = fields.Char(
        related='employee_id.work_phone',
        store=True,
        string="Điện thoại nhân sự",
        readonly=True,
    )

    employee_email = fields.Char(
        related='employee_id.work_email',
        store=True,
        string="Email nhân sự",
        readonly=True,
    )

    employee_department = fields.Many2one(
        related='employee_id.department_id',
        store=True,
        string="Phòng ban",
        readonly=True,
    )

    employee_image = fields.Binary(
        related='employee_id.image_1920',
        string="Ảnh nhân sự",
        readonly=True,
    )

    date_of_birth = fields.Date(
        related='employee_id.birthday',
        store=True,
        string="Ngày sinh",
        readonly=True,
    )

    marital = fields.Selection(
        related='employee_id.marital',
        store=True,
        string="Hôn nhân",
        readonly=True,
    )

    children = fields.Integer(
        related='employee_id.children',
        store=True,
        string="Số con",
        readonly=True,
    )

    employee_code = fields.Char(
        string="Mã nhân viên",
        related='employee_id.barcode',
        store=True,
        readonly=True,
    )

    gender = fields.Selection(
        related='employee_id.gender',
        store=True,
        string="Giới tính",
        readonly=True,
    )

    place_of_birth = fields.Char(string="Nơi sinh")

    id_card = fields.Char(
        string="CMND/CCCD",
        related='employee_id.identification_id',
        store=True,
        readonly=True,
    )

    issue_date = fields.Date(string="Ngày cấp")
    issue_place = fields.Char(string="Nơi cấp")

    insurance_code = fields.Char(
        string="Mã số BHYT",
        related='employee_id.ssnid',
        store=True,
        readonly=True,
    )
    insurance_start = fields.Date(string="Giá trị từ ngày")
    insurance_end = fields.Date(string="Giá trị đến ngày")

    phone = fields.Char(string="Số điện thoại liên hệ")
    email = fields.Char(string="Email liên hệ")
    address = fields.Char(string="Địa chỉ")
    emergency_contact = fields.Char(string="Liên hệ khẩn cấp")
    emergency_phone = fields.Char(string="SĐT khẩn cấp")

    hire_date = fields.Date(string="Ngày vào làm")
    status = fields.Selection(
        [
            ('active', 'Đang làm'),
            ('inactive', 'Nghỉ việc')
        ],
        default='active',
        string="Trạng thái"
    )
    desk_number = fields.Char(string="Số quầy lễ tân")
    computer_code = fields.Char(string="Mã máy làm việc")

    schedule_ids = fields.One2many(
        'pediatric.receptionist.schedule',
        'receptionist_id',
        string="Lịch làm việc theo ca"
    )

    queue_ids = fields.One2many(
        'reception.queue',
        'receptionist_id',
        string="Bệnh nhân đã tiếp nhận"
    )

    handled_patients = fields.Integer(
        string="Tổng bệnh nhân đã tiếp nhận",
        compute='_compute_handled_patients',
        store=True
    )
    today_received = fields.Integer(
        string="Tiếp nhận hôm nay",
        compute='_compute_today_received',
        store=True
    )

    @api.depends('queue_ids.state')
    def _compute_handled_patients(self):
        for r in self:
            r.handled_patients = len(r.queue_ids.filtered(
                lambda q: q.state != 'cancel'
            ))

    @api.depends('queue_ids.registration_date', 'queue_ids.state')
    def _compute_today_received(self):
        today = fields.Date.today()
        for r in self:
            r.today_received = len(r.queue_ids.filtered(
                lambda q: q.state != 'cancel'
                and q.registration_date
                and q.registration_date.date() == today
            ))

    processed_booking_ids = fields.One2many(
        'pediatric.booking',
        'receptionist_id',
        string="Lịch sử duyệt Booking"
    )
    total_processed_bookings = fields.Integer(
        string="Tổng phiếu đã duyệt",
        compute='_compute_total_processed',
        store=True
    )

    @api.depends('processed_booking_ids')
    def _compute_total_processed(self):
        for rec in self:
            rec.total_processed_bookings = len(rec.processed_booking_ids)

    note_positive = fields.Text(string="Điểm mạnh")
    note_negative = fields.Text(string="Điểm cần cải thiện")

    leave_total = fields.Integer(string="Tổng ngày nghỉ phép/năm")
    leave_used = fields.Integer(string="Đã dùng")
    leave_remaining = fields.Integer(
        string="Còn lại",
        compute='_compute_leave_remaining',
        store=True
    )

    @api.depends('leave_total', 'leave_used')
    def _compute_leave_remaining(self):
        for r in self:
            r.leave_remaining = (r.leave_total or 0) - (r.leave_used or 0)

    notes = fields.Text(string="Ghi chú bổ sung")

    def action_view_my_bookings(self):
        """Xem danh sách Booking do chính mình duyệt"""
        self.ensure_one()
        return {
            'name': 'Booking đã duyệt bởi ' + (self.name or ''),
            'type': 'ir.actions.act_window',
            'res_model': 'pediatric.booking',
            'view_mode': 'list,form',
            'domain': [('receptionist_id', '=', self.id)],
            'context': {'default_receptionist_id': self.id},
        }

    def action_view_employee(self):
        """Mở hồ sơ nhân sự gốc"""
        self.ensure_one()
        return {
            'name': 'Hồ sơ Nhân sự',
            'type': 'ir.actions.act_window',
            'res_model': 'hr.employee',
            'res_id': self.employee_id.id,
            'view_mode': 'form',
            'target': 'current',
        }

    def action_open_receptionist_calendar(self):
        """Xem lịch làm việc trên Calendar"""
        self.ensure_one()
        if not self.partner_id:
            domain = []
        else:
            domain = [('partner_ids', 'in', [self.partner_id.id])]
        return {
            'name': 'Lịch làm việc của ' + (self.name or ''),
            'type': 'ir.actions.act_window',
            'res_model': 'calendar.event',
            'view_mode': 'calendar,list',
            'domain': domain,
            'context': {'default_mode': 'week'},
            'target': 'current',
        }

    def action_view_receptionist_queues(self):
        """Xem danh sách hồ sơ đã tiếp nhận"""
        self.ensure_one()
        return {
            'name': 'Hồ sơ đã tiếp nhận',
            'type': 'ir.actions.act_window',
            'res_model': 'reception.queue',
            'view_mode': 'list,form',
            'domain': [('receptionist_id', '=', self.id)],
            'target': 'current',
        }

    def action_open_followup_appointments(self):
        """Lễ tân mở màn hình Lịch tái khám để đặt lịch"""
        self.ensure_one()
        return {
            'name': 'Đặt lịch tái khám',
            'type': 'ir.actions.act_window',
            'res_model': 'pediatric.appointment',
            'view_mode': 'list,form',
            'domain': [],
            'context': {
                'default_visit_type': 'followup',
            },
            'target': 'current',
        }


class PediatricReceptionistSchedule(models.Model):
    _name = 'pediatric.receptionist.schedule'
    _description = 'Lịch làm việc lễ tân'

    receptionist_id = fields.Many2one(
        'pediatric.receptionist',
        string="Lễ tân",
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
