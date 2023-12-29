'''nesi.globus.endpoint module implementation'''
import globus_sdk

from ansible.module_utils.basic import AnsibleModule

from ansible_collections.nesi.globus.plugins.module_utils import gcs_util # pylint: disable=import-error
from ansible_collections.nesi.globus.plugins.module_utils.gcs_util import Action # pylint: disable=import-error

def main():
    '''endpoint module implementation '''
    spec = gcs_util.common_spec() \
            | gcs_util.endpoint_spec()
    module = AnsibleModule(argument_spec= spec,
                                    supports_check_mode=True)
    try:
        spec = gcs_util.common_spec() \
            | gcs_util.endpoint_spec()
        module = AnsibleModule(argument_spec= spec,
                                    supports_check_mode=True)
        gcs_client = gcs_util.create_gcs_client(module)

        actual = get_endpoint_data(gcs_client)

        state = module.params["state"]
        if state == "absent":
            desired = None
        else:
            desired = gcs_util.read_keys(
                gcs_util.endpoint_spec().keys(),
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

    except globus_sdk.GlobusError as ex:
        module.fail_json(msg = str(ex))

@gcs_util.none_if_not_found
def get_endpoint_data(gcs_client):
    return gcs_client.get("endpoint").data["data"][0]

if __name__ == '__main__':
    main()
