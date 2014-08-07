__author__ = 'Andrean'

import controllers.agent_controller as agentsController


ROUTES = [
    [   'GET',    r'^/commands$', agentsController.commands['get']      ],
    [   'POST',   r'^/commands$', agentsController.commands['post']     ],
]
