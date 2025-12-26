
from odoo import models, fields, api
from datetime import date
class ReceptionQueue(models.Model):
    _name = 'reception.queue'
    _description = 'Tiếp nhận và xếp hàng khám nhi'
    _order = 'priority_level desc, queue_number asc'


    receptionist_id = fields.Many2one(
        'pediatric.receptionist',
        string="Nhân viên lễ tân phụ trách",
        ondelete='set null',
    )


    booking_id = fields.Many2one(
        'pediatric.booking',
        string="Phiếu đặt lịch",
        ondelete='set null',
    )


    booking_method = fields.Selection(
        [
            ('by_doctor', 'Đặt lịch với bác sĩ'),
            ('by_department', 'Đặt lịch theo chuyên khoa'),
            
        ],
        string="Phương thức đặt lịch",
        help="Mặc định lấy từ phiếu đặt lịch, có thể điều chỉnh lại khi tiếp nhận.",
    )


    specialty_id = fields.Many2one(
        'pediatric.specialty',
        string="Chuyên khoa",
        ondelete='set null',
    )

    doctor_id = fields.Many2one(
        'pediatric.doctor',
        string="Bác sĩ khám",
        ondelete='set null',
    )

    doctor_name = fields.Char(string="Bác sĩ phụ trách")

    estimated_fee = fields.Float(
        string="Phí khám dự kiến"
    )


    patient_id = fields.Many2one(
        'pediatric.patient',
        string="Bệnh nhi",
        ondelete='set null',
        help="Nếu đã có hồ sơ bệnh nhi trong hệ thống thì chọn ở đây.",
    )


    patient_name = fields.Char(string="Tên bệnh nhi", required=True)
    patient_gender = fields.Selection(
        [
            ('male', 'Nam'),
            ('female', 'Nữ'),
            ('other', 'Khác'),
        ],
        string="Giới tính",
    )
    patient_dob = fields.Date(string="Ngày sinh")
    patient_age = fields.Integer(
        string="Tuổi",
        compute="_compute_patient_age",
        store=True,
    )

    weight = fields.Float(string="Cân nặng (kg)")
    height = fields.Float(string="Chiều cao (cm)")

    @api.depends('patient_dob')
    def _compute_patient_age(self):
        for rec in self:
            if rec.patient_dob:
                today = date.today()
                rec.patient_age = (
                    today.year
                    - rec.patient_dob.year
                    - ((today.month, today.day) < (rec.patient_dob.month, rec.patient_dob.day))
                )
            else:
                rec.patient_age = 0


    parent_name = fields.Char(string="Tên phụ huynh")
    relationship = fields.Selection(
        [
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
        ],
        string="Mối quan hệ với bệnh nhi",
    )
    contact_phone = fields.Char(string="SĐT liên hệ")
    contact_email = fields.Char(string="Email (nếu có)")
    contact_reason = fields.Text(string="Lý do đến khám / Ghi chú của phụ huynh")


    queue_number = fields.Char(
        string="Số thứ tự",
        required=True,
        copy=False,
        default=lambda self: self.env['ir.sequence'].next_by_code('reception.queue') or 'New',
    )
    registration_date = fields.Datetime(
        string="Ngày giờ tiếp nhận",
        default=fields.Datetime.now,
    )


    appointment_date = fields.Date(string="Ngày khám (theo lịch hẹn)")

    session = fields.Selection(
        [
            ('morning', 'Buổi sáng'),
            ('afternoon', 'Buổi chiều'),
        ],
        string="Buổi khám",
    )

    condition_at_registration = fields.Text(
        string="Tình trạng khi tiếp nhận (VD: sốt, ho, nôn...)"
    )
    symptoms = fields.Text(string="Triệu chứng ban đầu")
    preliminary_diagnosis = fields.Char(string="Chuẩn đoán ban đầu (nếu có)")
    disease_category = fields.Selection(
        [
            ('respiratory', 'Hô hấp'),
            ('digestive', 'Tiêu hóa'),
            ('dermatology', 'Da liễu'),
            ('infectious', 'Nhiễm trùng'),
            ('neurology', 'Thần kinh'),
            ('other', 'Khác'),
        ],
        string="Phân loại bệnh",
    )

    has_chronic_disease = fields.Boolean(string="Có bệnh lý mãn tính?")
    chronic_disease_details = fields.Text(string="Chi tiết bệnh mãn tính")


    state = fields.Selection(
        [
            ('waiting', 'Đang chờ khám'),
            ('in_progress', 'Đang khám'),
            ('done', 'Đã khám'),
            ('cancelled', 'Hủy'),
        ],
        default='waiting',
        string="Trạng thái",
        index=True,
    )

    priority_level = fields.Selection(
        [
            ('normal', 'Thường'),
            ('urgent', 'Khẩn'),
            ('followup', 'Tái khám'),
        ],
        default='normal',
        string="Mức độ ưu tiên",
        index=True,
    )

    wait_time = fields.Float(string="Thời gian chờ (phút)", readonly=True)
    exam_room = fields.Char(string="Phòng khám")
    adjustment_plan = fields.Text(string="Phương án điều chỉnh riêng (nếu có)")


    followup_required = fields.Boolean(string="Cần tái khám?")
    followup_date = fields.Datetime(string="Ngày tái khám dự kiến")
    notes = fields.Text(string="Ghi chú thêm của nhân viên y tế")


    @api.onchange('booking_id')
    def _onchange_booking_id(self):
        for rec in self:
            if not rec.booking_id:
                continue

            b = rec.booking_id

            rec.booking_method = b.booking_method
            rec.appointment_date = b.appointment_date
            rec.session = b.session
            rec.priority_level = b.priority_level

            rec.specialty_id = b.specialty_id
            rec.doctor_id = b.doctor_id
            rec.doctor_name = b.doctor_name or (b.doctor_id and b.doctor_id.name) or False
            rec.estimated_fee = b.estimated_fee

            rec.patient_id = b.patient_id
            rec.patient_name = b.child_name
            rec.patient_dob = b.child_birth_date
            rec.patient_gender = b.child_gender
            rec.weight = b.weight
            rec.height = b.height

            rec.parent_name = b.parent_name
            rec.relationship = b.relationship
            rec.contact_phone = b.parent_phone
            rec.contact_email = b.parent_email
            rec.contact_reason = b.reason

            rec.symptoms = b.symptoms
            rec.condition_at_registration = b.condition_at_registration
            rec.preliminary_diagnosis = b.preliminary_diagnosis
