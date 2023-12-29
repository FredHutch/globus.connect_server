import globus_sdk

from ansible.module_utils.basic import AnsibleModule

from ansible_collections.nesi.globus.plugins.module_utils import gcs_util # pylint: disable=import-error

def main():
    '''storage_gateway_info ansible module implementation'''
    spec = gcs_util.common_spec() \
        | gcs_util.storage_gateway_spec()
    del spec["state"]
    module = AnsibleModule(argument_spec= spec,
                                supports_check_mode=True)
    try:
        keys = list(gcs_util.storage_gateway_spec().keys())
        filter_ = gcs_util.read_keys(
                    keys + ["id"],
                    module
                  )
        gcs_client = gcs_util.create_gcs_client(module)

        gateways = gcs_client.get_storage_gateway_list(
                    include = "private_policies"
                   )

        results = []
        for gateway in gateways:
            if not gcs_util.is_changed(gateway, filter_):
                results += [gateway]
        module.exit_json(changed = False, results = results)

    except globus_sdk.GlobusError as ex:
        module.fail_json(msg = str(ex))

if __name__ == '__main__':
    main()
