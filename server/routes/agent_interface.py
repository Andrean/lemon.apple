__author__ = 'Andrean'

import controllers.agent as agentsController


ROUTES = [
    [   'GET',   r'^/commands$', agentsController.commands.get                       ],
    [   'POST',  r'^/commands$', agentsController.commands.send                      ],
    [   'GET',   r'^/data/chunk[?=%&_\-\+\w\.,]*$', agentsController.data_chunk.get     ],
    [   'POST',  r'^/data/chunk$', agentsController.data_chunk.push                     ]
]
