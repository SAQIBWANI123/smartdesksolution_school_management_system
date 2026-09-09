{
    'name': 'School Management System',
    'version': '19.0.1.2.0',
    'category': 'Education',
    'author': 'SmartDeskSolution',
    'maintainer': 'SmartDeskSolution',
    'summary': 'Complete School Management with Admissions, Fees and Parent Portal',
    'description': """
Comprehensive School Management System for Odoo 19.
Developed by SmartDeskSolution | www.smartdesksolution.com | info@smartdesksolution.com
Key Features:
- Academic Year, Terms, Grade Levels, Classes & Sections
- Student Admission, Online Application Portal & Profile Management
- Teacher & Staff Management
- Daily & Subject Attendance Tracking with Alerts
- Examinations, Grading Scale, Marks Entry & Report Cards
- Weekly Timetable & Class Schedules
- School Fee Structure, Student Invoices & Payment Tracking
- School Transport (Routes, Vehicles, Subscriptions)
- Hostel Management (Blocks, Rooms, Student Allocations)
- Library Management (Books Cataloging, Issue & Return tracking)
- Analytics Dashboard & Graphic Reports
- Print PDF Reports (Student ID Cards, Academic Transcripts, Fee Receipts)
    """,
    'website': 'https://www.smartdesksolution.com',
    'depends': ['base', 'mail', 'website', 'portal'],
    'data': [
        'security/school_security.xml',
        'security/ir.model.access.csv',
        'data/school_sequence_data.xml',
        'views/menus.xml',
        'views/admission_views.xml',
        'views/dashboard_views.xml',
        'views/academic_year_views.xml',
        'views/grade_level_views.xml',
        'views/school_class_views.xml',
        'views/subject_views.xml',
        'views/student_views.xml',
        'views/teacher_views.xml',
        'views/parent_views.xml',
        'views/attendance_views.xml',
        'views/exam_views.xml',
        'views/timetable_views.xml',
        'views/fee_views.xml',
        'views/transport_views.xml',
        'views/hostel_views.xml',
        'views/library_views.xml',
        'views/portal_templates.xml',
        'report/school_reports.xml',
        'report/report_student_id_card.xml',
        'report/report_student_report_card.xml',
        'report/report_fee_receipt.xml',
    ],
    'demo': [
        'demo/school_demo_data.xml',
    ],
    'images': [
        'static/description/icon.png',
        'static/description/banner.png',
    ],
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
}
