import globus_sdk

from ansible.module_utils.basic import AnsibleModule

from ansible_collections.nesi.globus.plugins.module_utils import gcs_util # # pylint: disable=import-error
from ansible_collections.nesi.globus.plugins.module_utils.gcs_util import Action # pylint: disable=import-error

def main():
    '''storage_gateway_info ansible module implementation'''
    spec = gcs_util.common_spec() \
        | gcs_util.storage_gateway_spec()
    module = AnsibleModule(argument_spec = spec,
                                supports_check_mode = True)

    try:

        gcs_client = gcs_util.create_gcs_client(module)

        @gcs_util.none_if_not_found
        def get_storage_gateway_data(id_):
            return gcs_client.get_storage_gateway(
                storage_gateway_id = id_,
                include = "private_policies"
            ).data

        id_ = module.params["id"]
        if id_ is None:
            actual = None
        else:
            actual = get_storage_gateway_data(id_)

        state = module.params["state"]
        if state == "absent":
            desired = None
        else:
            desired = gcs_util.read_keys(
                gcs_util.storage_gateway_spec().keys(),
                module
                )

        def nothing():
            module.exit_json(changed = False, data = actual)

        def delete():
            gcs_client.delete_storage_gateway(id_)
            module.exit_json(changed = True, data = {"id": id_})

        def create():
            desired["DATA_TYPE"] = "storage_gateway#1.2.0"
            data = gcs_client.create_storage_gateway(desired).data
            module.exit_json(changed = True, data = data)

        def update():
            desired["DATA_TYPE"] = "storage_gateway#1.2.0"
            gcs_client.update_storage_gateway(id_,
                                              data = desired)
            data = get_storage_gateway_data(id_)
            module.exit_json(changed = True, data = data)

        action_table = {Action.NOTHING: nothing,
                        Action.DELETE:  delete,
                        Action.UPDATE:  update,
                        Action.CREATE:  create}

        action_table[gcs_util.plan(desired, actual)]()

    except globus_sdk.GlobusError as ex:
        module.fail_json(msg = str(ex))

if __name__ == '__main__':
    main()
