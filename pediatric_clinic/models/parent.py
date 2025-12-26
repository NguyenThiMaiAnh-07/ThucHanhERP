
from odoo import models, fields, api
from datetime import date


class PediatricFamilyMember(models.Model):
    _name = "pediatric.family.member"
    _description = "Người nhà / Người giám hộ bệnh nhi"


    name = fields.Char(string="Họ tên", required=True)

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
    ], string="Mối quan hệ với trẻ")

    is_primary_guardian = fields.Boolean(
        string="Người giám hộ chính",
        help="Đánh dấu nếu đây là người chịu trách nhiệm chính cho trẻ."
    )

    is_emergency_contact = fields.Boolean(
        string="Liên hệ khẩn cấp",
        help="Ưu tiên liên lạc người này khi có sự cố."
    )

    gender = fields.Selection([
        ('male', 'Nam'),
        ('female', 'Nữ'),
        ('other', 'Khác')
    ], string="Giới tính")

    date_of_birth = fields.Date(string="Ngày sinh")

    age = fields.Integer(
        string="Tuổi",
        compute="_compute_age",
        store=True
    )


    id_type = fields.Selection([
        ('id_card', 'CMND/CCCD'),
        ('passport', 'Hộ chiếu'),
        ('other', 'Khác'),
    ], string="Loại giấy tờ")

    id_number = fields.Char(string="Số giấy tờ")
    id_issue_date = fields.Date(string="Ngày cấp")
    id_issue_place = fields.Char(string="Nơi cấp")


    phone = fields.Char(string="Số điện thoại chính")
    phone_alt = fields.Char(string="Điện thoại phụ")
    email = fields.Char(string="Email")

    preferred_contact_method = fields.Selection([
        ('phone', 'Gọi điện'),
        ('sms', 'SMS'),
        ('zalo', 'Zalo'),
        ('email', 'Email'),
    ], string="Kênh liên lạc ưu tiên")

    preferred_language = fields.Selection([
        ('vi', 'Tiếng Việt'),
        ('en', 'Tiếng Anh'),
        ('other', 'Khác'),
    ], string="Ngôn ngữ ưu tiên")


    address = fields.Char(string="Địa chỉ")
    city = fields.Char(string="Thành phố/Tỉnh")
    district = fields.Char(string="Quận/Huyện")
    ward = fields.Char(string="Phường/Xã")
    zipcode = fields.Char(string="Mã bưu điện")

    lives_with_child = fields.Boolean(
        string="Sống cùng trẻ",
        help="Đánh dấu nếu người này sống cùng trẻ."
    )

    custody_notes = fields.Text(
        string="Ghi chú quyền nuôi dưỡng",
        help="VD: cha mẹ ly thân, hạn chế tiếp xúc, người được phép ký giấy tờ…"
    )


    occupation = fields.Char(string="Nghề nghiệp")
    workplace_name = fields.Char(string="Nơi làm việc")
    workplace_phone = fields.Char(string="Điện thoại nơi làm việc")


    consent_general_care = fields.Boolean(
        string="Đồng ý điều trị",
        help="Người này đồng ý cho phép thăm khám & điều trị."
    )

    consent_share_info = fields.Boolean(
        string="Đồng ý chia sẻ thông tin y tế",
        help="Cho phép chia sẻ thông tin y tế của trẻ với người này."
    )

    note = fields.Text(string="Ghi chú thêm")


    child_ids = fields.One2many(
        'pediatric.patient',
        'family_member_id',
        string="Trẻ liên quan"
    )

    booking_ids = fields.One2many(
        'pediatric.booking',
        'family_member_id',
        string="Lịch khám đã đặt"
    )


    appointment_ids = fields.One2many(
        'pediatric.appointment',
        'family_member_id',
        string="Lịch tái khám"
    )


    @api.depends('date_of_birth')
    def _compute_age(self):
        for rec in self:
            if rec.date_of_birth:
                today = date.today()
                rec.age = (
                    today.year - rec.date_of_birth.year
                    - ((today.month, today.day) <
                       (rec.date_of_birth.month, rec.date_of_birth.day))
                )
            else:
                rec.age = 0
