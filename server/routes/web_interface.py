__author__ = 'Andrean'

import controllers.web  as webController

#####################################################################################
#    Routes for routing request from WEB-Server as web-interface
#####################################################################################
ROUTES = [
    [   'GET',  r'^/entities[?=%&_\-\+\w\.,]*$', webController.entity_manager['get_entities']   ],
    [   'PUT',  r'^/entities[?=%&_\-\+\w\.,]*$', webController.entity_manager['add_entity']     ],
    [   'POST',  r'^/entities[?=%&_\-\+\w\.,]*$', webController.entity_manager['modify_entity'] ],
    [   'DELETE',  r'^/entities[?=%&_\-\+\w\.,]*$', webController.entity_manager['del_entity']  ],
    [   'GET',  r'^/agents[?=%&_\-\+\w,\.]*$', webController.agents.get_agents                  ],
    [   'GET',  r'^/contractors[?=%&_\-\+\w\.,]*$', webController.contractors.get               ],
    [   'PUT',  r'^/contractors[?=%&_\-\+\w\.,]*$', webController.contractors.add               ],
    [   'DELETE',  r'^/contractors[?=%&_\-\+\w\.,]*$', webController.contractors.remove         ],
    [   'GET',  r'^/data/items[?=%&_\-\+\w\.,]*$', webController.data_items.get                 ],
    [   'POST',  r'^/data/items[?=%&_\-\+\w\.,]*$', webController.data_items.set                ],
    [   'DELETE',  r'^/data/items[?=%&_\-\+\w\.,]*$', webController.data_items.remove           ],
    [   'GET',  r'^/data/chunk[?=%&_\-\+\w\.,]*$', webController.data_chunks.get                ],
    [   'GET',  r'^/data/chunk/count[?=%&_\-\+\w\.,]*$', webController.data_chunks.count        ],
    [   'GET',  r'^/commands/send[?=%&_\-\+\w\.,]*$', webController.commands.send_to            ],
    [   'POST', r'^/commands/send[?=%&_\-\+\w\.,]*$', webController.commands.send_to            ],
    [   'GET',  r'^/agents/commands[?=%&_\-\+\w\.,]*$', webController.agents.get_agent_commands ]
]

