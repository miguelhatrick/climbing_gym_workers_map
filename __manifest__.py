# -*- coding: utf-8 -*-
{
    'name': "Climbing gym workers automatic MAP assigner",
    # climbing_gym_workers_map
    'summary': """
        Climbing gym workers automatic MAP assigner""",

    'description': """
        Climbing gym workers automatic MAP assigner
    """,

    'author': "Miguel Hatrick",
    'website': "http://www.dacosys.com",

    'category': 'Climbing Gym',
    'version': '12.0.2',

    # any module necessary for this one to work correctly
    'depends': ['base',
                'mail',
                'hr',
                'climbing_gym',
                ],

    # always loaded
    'data': [
            'security/ir.model.access.csv',

            'data/cron_jobs.xml',

            'views/worker_access_package.xml',
            'views/menu.xml'

    ],
    # only loaded in demonstration mode
    'demo': [
        # 'demo/demo.xml',
    ],
}

