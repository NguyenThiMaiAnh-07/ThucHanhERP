
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from datetime import datetime, timedelta, time


class PediatricBooking(models.Model):
    _name = "pediatric.booking"
    _description = "Đặt lịch hẹn khám Nhi khoa"
    _order = "appointment_date desc, booking_time desc"



    specialty_id = fields.Many2one(
        'pediatric.specialty',
        string="Chuyên khoa",
        help="Chuyên khoa mà lịch hẹn này thuộc về"
    )

    doctor_id = fields.Many2one(
        'pediatric.doctor',
        string="Bác sĩ khám",
        domain="[('specialty_id', '=', specialty_id)]",
        help="Bác sĩ khám được chọn"
    )

    estimated_fee = fields.Float(
        string="Phí khám dự kiến",
        readonly=True,
        help="Tự động lấy phí khám từ bác sĩ được chọn"
    )

    patient_id = fields.Many2one(
        'pediatric.patient',
        string="Bệnh nhi",
        ondelete='set null'
    )

    family_member_id = fields.Many2one(
        'pediatric.family.member',
        string="Hồ sơ người nhà"
    )

    receptionist_id = fields.Many2one(
        'pediatric.receptionist',
        string="Lễ tân xử lý",
        ondelete='set null',
    )


    parent_name = fields.Char(string="Họ tên phụ huynh", required=True)
    parent_birth_date = fields.Date(string="Ngày sinh")
    parent_phone = fields.Char(string="Số điện thoại", required=True)
    parent_gender = fields.Selection([
        ('male', 'Nam'),
        ('female', 'Nữ'),
    ], string="Giới tính")
    parent_email = fields.Char(string="Email")

    relationship = fields.Selection([
        ('father', 'Cha'),
        ('mother', 'Mẹ'),
        ('grandfather', 'Ông'),
        ('grandmother', 'Bà'),
        ('uncle', 'Cậu/Chú/Bác'),
        ('aunt', 'Dì/Cô'),
        ('brother', 'Anh/Em trai'),
        ('sister', 'Chị/Em gái'),
        ('guardian', 'Người giám hộ'),
        ('other', 'Khác'),
    ], string="Quan hệ với trẻ")


    child_name = fields.Char(string="Tên bệnh nhi", required=True)
    child_birth_date = fields.Date(string="Ngày sinh")
    child_gender = fields.Selection([
        ('male', 'Nam'),
        ('female', 'Nữ'),
    ], string="Giới tính")
    weight = fields.Float(string="Cân nặng (kg)")
    height = fields.Float(string="Chiều cao (cm)")



    booking_method = fields.Selection([
        ('by_doctor', 'Đặt lịch với bác sĩ'),
        ('by_department', 'Đặt lịch theo chuyên khoa'),
    ], string="Phương thức đặt lịch", required=True, default='by_doctor')

    appointment_date = fields.Date(string="Ngày khám mong muốn", required=True)

    session = fields.Selection([
        ('morning', 'Buổi sáng'),
        ('afternoon', 'Buổi chiều'),
    ], string="Buổi khám", required=True)

    department = fields.Selection([
        ('general', 'Khám tổng quát'),
        ('respiratory', 'Hô hấp'),
        ('digestive', 'Tiêu hóa'),
        ('dermatology', 'Da liễu'),
        ('infectious', 'Nhiễm trùng'),
        ('neurology', 'Thần kinh'),
        ('other', 'Khác'),
    ], string="Chuyên khoa", default='general')

    doctor_name = fields.Char(string="Tên bác sĩ dự kiến")

    priority_level = fields.Selection([
        ('normal', 'Thường'),
        ('urgent', 'Khẩn'),
        ('followup', 'Tái khám'),
    ], string="Mức độ ưu tiên", default='normal')

    visit_type = fields.Selection([
        ('first', 'Khám lần đầu'),
        ('followup', 'Tái khám'),
    ], default='first')

    state = fields.Selection(
        [
            ('draft', 'Mới tạo'),
            ('confirmed', 'Đã xác nhận'),
            ('cancel', 'Đã hủy'),
        ],
        string="Trạng thái",
        default='draft'
    )

    booking_time = fields.Datetime(
        string="Thời điểm đặt lịch",
        default=fields.Datetime.now
    )

    can_edit = fields.Boolean(
        string="Có thể chỉnh sửa/hủy",
        compute="_compute_can_edit",
        store=True
    )

    @api.depends('booking_time')
    def _compute_can_edit(self):
        for r in self:
            r.can_edit = bool(
                r.booking_time
                and datetime.now() <= (r.booking_time + timedelta(hours=24))
            )

    def unlink(self):
        for r in self:
            if not r.can_edit:
                raise ValidationError("Bạn chỉ có thể hủy lịch trong vòng 24h kể từ khi đặt.")
        return super().unlink()

    def write(self, vals):

        for r in self:
            if 'can_edit' in vals and len(vals) == 1:
                continue
            if not r.can_edit:
                raise ValidationError("Bạn chỉ có thể chỉnh sửa lịch trong vòng 24h kể từ khi đặt.")
        res = super().write(vals)

        sync_fields = {
            'appointment_date',
            'session',
            'doctor_id',
            'patient_id',
            'child_name',
            'parent_name',
        }
        if sync_fields.intersection(vals.keys()):
            self._sync_calendar_event()
        return res



    reason = fields.Text(string="Lý do khám")
    symptoms = fields.Text(string="Triệu chứng ban đầu")
    condition_at_registration = fields.Text(string="Tình trạng hiện tại")
    preliminary_diagnosis = fields.Char(string="Chẩn đoán sơ bộ")


    @api.onchange('family_member_id')
    def _onchange_family(self):
        if self.family_member_id:
            fm = self.family_member_id
            self.parent_name = fm.name
            self.parent_birth_date = fm.date_of_birth
            self.parent_phone = fm.phone
            self.parent_gender = fm.gender
            self.parent_email = fm.email
            self.relationship = fm.relationship

    @api.onchange('patient_id')
    def _onchange_patient(self):
        if self.patient_id:
            p = self.patient_id
            self.child_name = p.name
            self.child_birth_date = p.date_of_birth
            self.child_gender = p.gender

            if p.doctor_id and not self.doctor_id:
                self.doctor_id = p.doctor_id
                self.doctor_name = p.doctor_id.name
                self.estimated_fee = p.doctor_id.consultation_fee or 0.0
                if p.doctor_id.specialty_id:
                    self.specialty_id = p.doctor_id.specialty_id

    @api.onchange('doctor_id')
    def _onchange_doctor(self):
        if self.doctor_id:
            self.doctor_name = self.doctor_id.name
            self.estimated_fee = self.doctor_id.consultation_fee or 0.0
            self.specialty_id = self.doctor_id.specialty_id.id

    @api.onchange('specialty_id', 'booking_method')
    def _onchange_specialty(self):
        if self.booking_method == 'by_department' and self.specialty_id:
            return {
                'domain': {
                    'doctor_id': [('specialty_id', '=', self.specialty_id.id)]
                }
            }
        return {'domain': {'doctor_id': []}}


    @api.constrains('doctor_id', 'appointment_date', 'session')
    def _check_schedule(self):
        for rec in self:
            if not rec.doctor_id or not rec.appointment_date:
                continue

            weekday = [
                'mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun'
            ][rec.appointment_date.weekday()]

            shifts = ['full']
            if rec.session == 'morning':
                shifts.append('morning')
            if rec.session == 'afternoon':
                shifts.append('afternoon')

            exists = self.env['pediatric.doctor.schedule'].search_count([
                ('doctor_id', '=', rec.doctor_id.id),
                ('weekday', '=', weekday),
                ('shift', 'in', shifts)
            ])

            if not exists:
                raise ValidationError(
                    "Bác sĩ %s không có lịch rảnh buổi %s ngày %s."
                    % (
                        rec.doctor_id.name,
                        "sáng" if rec.session == 'morning' else "chiều",
                        rec.appointment_date.strftime('%d/%m/%Y')
                    )
                )


    queue_ids = fields.One2many(
        'reception.queue',
        'booking_id',
        string="Hàng chờ"
    )
    queue_count = fields.Integer(
        compute="_compute_queue_count"
    )

    @api.depends('queue_ids')
    def _compute_queue_count(self):
        for rec in self:
            rec.queue_count = len(rec.queue_ids)



    def action_create_queue(self):
        self.ensure_one()
        if not self.id:
            raise UserError("Vui lòng lưu phiếu trước.")

        vals = {
            'booking_id': self.id,

            'booking_method': self.booking_method,
            'specialty_id': self.specialty_id.id if self.specialty_id else False,
            'doctor_id': self.doctor_id.id if self.doctor_id else False,
            'doctor_name': self.doctor_name or (self.doctor_id and self.doctor_id.name) or False,
            'estimated_fee': self.estimated_fee,
            'appointment_date': self.appointment_date,
            'session': self.session,

            'patient_id': self.patient_id.id if self.patient_id else False,
            'patient_name': self.child_name,
            'patient_dob': self.child_birth_date,
            'patient_gender': self.child_gender,
            'weight': self.weight,
            'height': self.height,

            'parent_name': self.parent_name,
            'relationship': self.relationship,
            'contact_phone': self.parent_phone,
            'contact_email': self.parent_email,

            'contact_reason': self.reason,
            'symptoms': self.symptoms,
            'condition_at_registration': self.condition_at_registration,
            'preliminary_diagnosis': self.preliminary_diagnosis,

            'priority_level': self.priority_level,
            'state': 'waiting',
        }

        queue = self.env['reception.queue'].create(vals)

        return {
            'type': 'ir.actions.act_window',
            'res_model': 'reception.queue',
            'view_mode': 'form',
            'res_id': queue.id,
            'target': 'current',
        }

    def action_open_queues(self):
        self.ensure_one()
        if not self.id:
            raise UserError("Vui lòng lưu phiếu trước khi xem hàng chờ.")
        return {
            'type': 'ir.actions.act_window',
            'name': 'Hàng chờ khám',
            'res_model': 'reception.queue',
            'view_mode': 'list,form',
            'domain': [('booking_id', '=', self.id)],
            'target': 'current',
        }



    calendar_event_id = fields.Many2one(
        'calendar.event',
        string="Sự kiện lịch",
        readonly=True
    )

    def _get_calendar_start_end(self):
        """Dùng appointment_date + session để tạo start/end cho calendar."""
        self.ensure_one()
        if not self.appointment_date or not self.session:
            return False, False

        base_time = time(9, 0) if self.session == 'morning' else time(14, 0)
        start = datetime.combine(self.appointment_date, base_time)
        end = start + timedelta(minutes=30)
        return start, end

    def _sync_calendar_event(self):
        """Tạo hoặc cập nhật calendar.event tương ứng cho booking."""
        for rec in self:
            start, end = rec._get_calendar_start_end()
            if not start:
                continue

            partners = []
            if rec.doctor_id and getattr(rec.doctor_id, 'partner_id', False):
                partners.append(rec.doctor_id.partner_id.id)
            if rec.patient_id and getattr(rec.patient_id, 'partner_id', False):
                partners.append(rec.patient_id.partner_id.id)

            event_vals = {
                'name': f"Lịch khám: {rec.child_name or rec.patient_id.name or rec.parent_name}",
                'start': start,
                'stop': end,
                'allday': False,
                'partner_ids': [(6, 0, partners)] if partners else [],
                'description': rec.reason or rec.symptoms or '',
            }

            if rec.calendar_event_id:
                rec.calendar_event_id.write(event_vals)
            else:
                event = self.env['calendar.event'].create(event_vals)
                rec.calendar_event_id = event.id

    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        records._sync_calendar_event()
        return records

    def action_open_calendar_event(self):
        """
        Smart button 'Sự kiện lịch':
        - Mở dạng lưới Calendar
        - Chỉ hiển thị đúng sự kiện lịch của booking này
        """
        self.ensure_one()
        if not self.calendar_event_id:
            
            self._sync_calendar_event()
        if not self.calendar_event_id:
            raise UserError("Chưa đủ dữ liệu (Ngày khám / Buổi khám) để tạo sự kiện lịch.")

        return {
            'type': 'ir.actions.act_window',
            'name': 'Sự kiện lịch khám',
            'res_model': 'calendar.event',
            'view_mode': 'calendar,form,list',
            'domain': [('id', '=', self.calendar_event_id.id)],
            'target': 'current',
            'context': {
                'default_start': self.calendar_event_id.start,
            },
        }