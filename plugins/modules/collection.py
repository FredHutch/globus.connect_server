import globus_sdk

from ansible.module_utils.basic import AnsibleModule

import ansible_collections.nesi.globus.plugins.module_utils.gcs_util as gcs_util # type: ignore
from ansible_collections.nesi.globus.plugins.module_utils.gcs_util import Action # type: ignore

def collection_spec():
    return dict(
        allow_guest_collections = dict(type='bool', 
                                    required=False),
        authentication_timeout_mins = dict(type = 'int',
                                        required = False),
        collection_base_path = dict(type = 'str', required = False),
        collection_type = dict(type = 'str', 
                            choices = ["mapped", "guest"],
                            required = True),
        connector_id = dict(type = gcs_util.get_connector_id,
                            required=False),
        contact_email = dict(type = 'str', required = False),
        contact_info = dict(type = 'str', required = False),
        default_directory = dict(type = 'str', required = False),
        delete_protected = dict(type = 'bool', required = False),
        department = dict(type = 'str', required = False),
        disable_anonymous_writes = dict(type = 'bool', 
                                        required = False),
        disable_verify = dict(type = 'bool', required = False),
        display_name = dict(type = 'str', required = False),
        domain_name = dict(type = 'str', required = False),
        enable_https = dict(type = 'bool', required = False),
        force_encryption = dict(type = 'bool', required = False),
        force_verify = dict(type = 'bool', required = False),
        guest_auth_policy_id = dict(type = 'str', required = False),
        high_assurance = dict(type = 'bool', required = False),
        info_link = dict(type = 'str', required = False),
        keywords = dict(type='list', required=False),
        mapped_collection_id = dict(type = 'str', required = False),
        organization = dict(type = 'str', required = False),
        policies = dict(type='dict', required=False),
        public = dict(type = 'bool', required = False),
        require_mfa = dict(type = 'bool', required = False),
        root_path = dict(type = 'str', required = False),
        sharing_restrict_paths = dict(type='dict', required=False),
        sharing_users_allow = dict(type='list', required=False),
        sharing_users_deny = dict(type='list', required=False),
        storage_gateway_id = dict(type='str', required=False),
        user_credential_id = dict(type='str', required=False),
        user_message = dict(type='str', required=False),
        user_message_link = dict(type='str', required=False),
    )

def main():
    try:
        spec = gcs_util.common_spec() | collection_spec()
        module = AnsibleModule(argument_spec= spec,
                                    supports_check_mode=True)
        gcs_client = gcs_util.create_gcs_client(module)

        id = module.params["id"]
        if (id is None):
            actual = None
        else:
            actual = get_collection_data(gcs_client, id)

        state = module.params["state"]
        if state == "absent":
            desired = None
        else:
            desired = gcs_util.read_keys(
                collection_spec().keys(), 
                module
                )
            
        def nothing():
            module.exit_json(changed = False, data = actual)
        
        def delete():
            gcs_client.delete_collection(id)
            module.exit_json(changed = True, data = {"id": id})

        def create():
            desired["DATA_TYPE"] = "collection#1.9.0"
            data = gcs_client.create_collection(desired).data
            module.exit_json(changed = True, data = data)

        def update():
            desired["DATA_TYPE"] = "collection#1.9.0"
            gcs_client.update_collection(id, desired)
            data = get_collection_data(gcs_client, id)
            module.exit_json(changed = True, data = data)

        action_table = {Action.NOTHING: nothing,
                        Action.DELETE:  delete,
                        Action.UPDATE:  update,
                        Action.CREATE:  create}      
        
        action_table[gcs_util.plan(desired, actual)]()
          
    except globus_sdk.GlobusError as e:
        module.fail(msg = str(e))

@gcs_util.none_if_not_found
def get_collection_data(gcs_client, id):
    return gcs_client.get_collection(
        id, 
        query_params = { 
            "include": "private_policies"
            }
        ).data

if __name__ == '__main__':
    main()

