__author__ = 'Andrean'

import commands.controllers

Routes = [
    ['test', commands.controllers.test     ],
    ['test2', commands.controllers.test2   ],
    ['error', commands.controllers.emulate_error]
]
