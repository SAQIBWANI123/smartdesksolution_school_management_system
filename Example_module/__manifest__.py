{
    'name': 'Example Module',
    'version': '19.0.1.0.0',
    'summary': 'Example module with a custom model and a list view',
    'description': """
Example Module
===============
A minimal Odoo 19 module demonstrating a custom model (example.model)
with a list view, form view, menu, and access rights.
""",
    'author': 'Your Name',
    'category': 'Uncategorized',
    'depends': ['base'],
    'data': [
        'security/ir.model.access.csv',
        'views/user_views.xml',
    ],
    'installable': True,
    'application': False,
    'license': 'LGPL-3',
}
