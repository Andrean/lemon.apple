__author__ = 'Andrean'

import controllers.agent as agentsController


ROUTES = [
    [   'GET',   r'^/commands$', agentsController.commands.get                       ],
    [   'POST',  r'^/commands$', agentsController.commands.send                      ],
    [   'POST',  r'^/data$', agentsController.data_chunk.push                  ]
]
