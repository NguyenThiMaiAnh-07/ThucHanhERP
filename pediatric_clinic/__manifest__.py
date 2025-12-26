{
    'name': 'Pediatric Clinic',
    'version': '1.0',
    'category': 'Medical',
    'summary': 'Quản lý phòng khám Nhi',
    'author': 'Bạn',


    'depends': ['base', 'hr', 'calendar', 'mail'],

    'data': [
        'security/ir.model.access.csv',


        'views/parent_view.xml',                 
        'views/patient_view.xml',                
        'views/doctor_view.xml',                 
        'views/booking_view.xml',                
        'views/reception_queue_sequence.xml',    
        'views/reception_queue_view.xml',        
        'views/appointment_view.xml', 
         'views/receptionist_view.xml', 
        'views/specialty_view.xml',

        'views/menu.xml',
    ],

    'installable': True,
    'application': True,
    'license': 'LGPL-3',
}
