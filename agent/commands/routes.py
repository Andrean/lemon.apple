__author__ = 'Andrean'

import commands.controllers

Routes = [
    ['test',            commands.controllers.test.test                      ],
    ['test2',           commands.controllers.test.test2                     ],
    ['error',           commands.controllers.test.emulate_error             ],
    ['contractor.add',      commands.controllers.contractor.add_or_modify   ],
    ['contractor.delete',   commands.controllers.contractor.delete          ],
    ['contractor.run',      commands.controllers.contractor.run             ],
    ['contractor.kill',     commands.controllers.contractor.kill            ]
]
