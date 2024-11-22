{
    'name': "autonsi_server",

    'summary': """
        Can be used to install module from git, check for server status, backup and restore server""",

    'description': """
        Long description of module's purpose
    """,

    'author': "My Company",
    'website': "https://www.autonsi.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/views.xml',
    ],
    'demo': [
        'demo/demo.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
    # only loaded in demonstration mode
}

