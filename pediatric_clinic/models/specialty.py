
from odoo import models, fields, api
class PediatricSpecialty(models.Model):
    _name = 'pediatric.specialty'
    _description = 'Danh mục Chuyên khoa Nhi'
    _rec_name = 'name'
    _order = 'sequence, name'

    name = fields.Char(string="Tên chuyên khoa", required=True, translate=True)
    code = fields.Char(string="Mã khoa", required=True)
    sequence = fields.Integer(string="Thứ tự hiển thị", default=10)
    description = fields.Text(string="Mô tả chuyên môn")
 
    predefined_name = fields.Selection([
        ('general', 'Nhi Tổng quát'),
        ('respiratory', 'Nhi Hô hấp'),
        ('digestive', 'Nhi Tiêu hóa'),
        ('ent', 'Tai Mũi Họng'),
        ('allergy', 'Dị ứng & Miễn dịch'),
        ('nutrition', 'Nhi Dinh dưỡng'),
        ('dermatology', 'Da liễu Nhi'),
        ('neurology', 'Nhi Thần kinh'),
        ('cardiology', 'Tim mạch Nhi'),
        ('infectious', 'Bệnh Truyền nhiễm'),
        ('endocrinology', 'Nội tiết & Chuyển hóa'),
        ('nephrology', 'Thận - Tiết niệu'),
        ('hematology', 'Huyết học - Ung bướu'),
        ('ophthalmology', 'Mắt Nhi'),
        ('dentistry', 'Răng Hàm Mặt'),
        ('psychology', 'Tâm lý & Sức khỏe tâm thần'),
        ('rehab', 'Phục hồi chức năng'),
        ('neonatology', 'Sơ sinh'),
        ('surgery', 'Ngoại Nhi'),
        ('emergency', 'Cấp cứu & Hồi sức')
    ],
        string="Tên chuyên khoa",           
        help="Chọn tên chuyên khoa"        
    )

    @api.onchange('predefined_name')
    def _onchange_predefined_name(self):
        if self.predefined_name:
            selection_dict = dict(self._fields['predefined_name'].selection)
            self.name = selection_dict.get(self.predefined_name)
            self.code = self.predefined_name.upper()[:4]

    doctor_ids = fields.One2many('pediatric.doctor', 'specialty_id', string="Danh sách Bác sĩ")
    booking_ids = fields.One2many('pediatric.booking', 'specialty_id', string="Lịch đặt liên quan")
