{
    'name': 'Printing Job Management',

    'version': '19.0.1.0.0',

    'category': 'Operations',

    'summary': 'Manage Printing Jobs',

    'depends': [
        'base',
    ],

    'data': [
        'security/ir.model.access.csv',
        'views/printing_job_views.xml',
    ],

    'installable': True,

    'application': True,
}