'''
(4, 7) All status and readings of one channel
The status and readings of “Chan” channel will be returned.
'''
read_status_msg = {
                    'jsonrpc': '2.0', 
                    'method': 'MacNet', 
                    'params':
                    {
                        'FClass': 4, 
                        'FNum': 7,
                        'Chan': -1
                    },
                    'id': 1987 
                }


