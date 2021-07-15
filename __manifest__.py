# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name' : 'Invoice From Picking',
    'version' : '1.0',
    'author':'Craftsync Technologies',
    'category': 'Stock',
    'maintainer': 'Craftsync Technologies',
    'summary': """Create Invoice From picking""",
    'website': 'https://www.craftsync.com/',
    'license': 'OPL-1',
    'support':'info@craftsync.com',
    'depends' : ['account','stock'],
    'data': [

        'views/stock_picking.xml'
    ],
    
    'installable': True,
    'application': True,
    'auto_install': False,
    'images': ['static/description/main_screen.png'],
    'price': 9.00,
    'currency': 'EUR',

}
