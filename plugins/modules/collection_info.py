import globus_sdk

from ansible.module_utils.basic import AnsibleModule

from ansible_collections.nesi.globus.plugins.module_utils import gcs_util # pylint: disable=import-error

def main():
    '''collection_info module implementation '''
    spec = gcs_util.common_spec() \
        | gcs_util.collection_spec()
    del spec["state"]
    module = AnsibleModule(argument_spec = spec,
        supports_check_mode = True)

    try:
        filter_ = gcs_util.read_keys(
                    list(gcs_util.collection_spec().keys()) \
                          + ["id"],
                    module
                  )
        gcs_client = gcs_util.create_gcs_client(module)

        collections = gcs_client.get_collection_list(
                        query_params = {
                            "include": "private_policies"
                        }
                    )

        results = []
        for col in collections:
            if not gcs_util.is_changed(col, filter_):
                results += [col]
        module.exit_json(changed = False, results = results)

    except globus_sdk.GlobusError as ex:
        module.fail_json(msg = str(ex))

if __name__ == '__main__':
    main()
