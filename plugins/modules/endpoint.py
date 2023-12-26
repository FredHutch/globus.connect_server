import globus_sdk

from ansible.module_utils.basic import AnsibleModule

import ansible_collections.nesi.globus.plugins.module_utils.gcs_util as gcs_util # type: ignore
from ansible_collections.nesi.globus.plugins.module_utils.gcs_util import Action # type: ignore

def endpoint_spec():
    return dict(
        display_name = dict(type='str', required=False),
        organization = dict(type='str', required=False),
        department = dict(type='str', required=False),
        contact_email = dict(type='str', required=False),
        contact_info = dict(type='str', required=False),
        description = dict(type='str', required=False),
        subscription_id = dict(type='str', required=False),
        keywords = dict(type='list', required=False),
        max_concurrency = dict(type='int', required=False),
        max_parallelism = dict(type='int', required=False),
        preferred_concurrency = dict(type='int', required=False),
        preferred_parallelism = dict(type='int', required=False),
        public = dict(type='bool', required=False),
        allow_udt = dict(type='bool', required=False),
        network_use = dict(type='str', 
                        choices = ["normal", 
                                    "aggressive",
                                    "minimal",
                                    "custom"],
                            required=False),
        gridftp_control_channel_port = dict(type='int', 
                                            required = False)
    )

def main():
    try:
        spec = gcs_util.common_spec() | endpoint_spec()
        module = AnsibleModule(argument_spec= spec,
                                    supports_check_mode=True)
        gcs_client = gcs_util.create_gcs_client(module)

        id = module.params["endpoint_id"]
        actual = get_endpoint_data(gcs_client)

        state = module.params["state"]
        if state == "absent":
            desired = None
        else:
            desired = gcs_util.read_keys(
                endpoint_spec().keys(), 
                module
                )

        def nothing():
            module.exit_json(changed = False, data = actual)
        
        def delete():
            module.fail_json(
                msg = "endpoint deletion not supported"
                )

        def create():
            module.fail_json(
                msg = "endpoint creation not supported"
                )

        def update():
            desired["DATA_TYPE"] = "endpoint#1.2.0"
            gcs_client.patch("endpoint", 
                        encoding = "json", 
                        data = desired)
            data = get_endpoint_data(gcs_client)
            module.exit_json(changed = True, data = data)

        action_table = {Action.NOTHING: nothing,
                        Action.DELETE:  delete,
                        Action.UPDATE:  update,
                        Action.CREATE:  create}      
        
        action_table[gcs_util.plan(desired, actual)]()

    except globus_sdk.GlobusError as e:
        module.fail(msg = str(e))


@gcs_util.none_if_not_found
def get_endpoint_data(gcs_client):
    return gcs_client.get("endpoint").data["data"][0]

if __name__ == '__main__':
    main()