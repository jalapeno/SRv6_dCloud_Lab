import json

data = {'fields': \
    {'allocation_type': 'dynamic', 'create_timestamp_age_in_nano_seconds': 108516, \
        'create_timestamp_time_in_nano_seconds': 1674251690656744119, 'has_forwarding': 'true', \
            'locator': 'MyLocator', 'owner_owner': 'bgp-65000', 'sid': 'fc00:0:1111:e008::', \
                'sid_behavior_description': 'uDT4', 'sid_behavior_type': 'udt4', \
                    'sid_context_application_data': '00:00:00:00:00:00:00:00', 'sid_context_key_sid_context_type': 'udt4', \
                        'sid_context_key_u_dt4_u_dt_base_ctx_table_id': 3758096384, 'sid_functionvalue': 57352, 'state': 'in-use'}, \
    'name': 'Cisco-IOS-XR-segment-routing-srv6-oper:srv6_active_locator-all-sids_locator-all-sid', \
    'tags': {'host': 'telegraf', 'locator_name': 'MyLocator', \
                'path': 'Cisco-IOS-XR-segment-routing-srv6-oper:srv6_active_locator-all-sids_locator-all-sid', \
                    'sid_opcode': '57352', 'source': 'xrd01', 'subscription': 'base_metrics'}, \
    'timestamp': 1674360206}

print("Type:", type(data))
print("\nfields:", data['fields'])
print("\nfields:", data['allocation_type'])

data2 =     {'allocation_type': 'dynamic', 'create_timestamp_age_in_nano_seconds': 108516, \
        'create_timestamp_time_in_nano_seconds': 1674251690656744119, 'has_forwarding': 'true', \
            'locator': 'MyLocator', 'owner_owner': 'bgp-65000', 'sid': 'fc00:0:1111:e008::', \
                'sid_behavior_description': 'uDT4', 'sid_behavior_type': 'udt4', \
                    'sid_context_application_data': '00:00:00:00:00:00:00:00', 'sid_context_key_sid_context_type': 'udt4', \
                        'sid_context_key_u_dt4_u_dt_base_ctx_table_id': 3758096384, 'sid_functionvalue': 57352, 'state': 'in-use'}
  
print("Type:", type(data2))
print("\nfields:", data2['sid'])
print("\nfields:", data2['locator'])