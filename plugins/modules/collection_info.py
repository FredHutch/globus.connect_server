import globus_sdk

from ansible.module_utils.basic import AnsibleModule

import ansible_collections.nesi.globus.plugins.module_utils.gcs_util as gcs_util # type: ignore
from ansible_collections.nesi.globus.plugins.module_utils.gcs_util import Action # type: ignore

def main():
    try:
        spec = gcs_util.common_spec() \
            | gcs_util.collection_spec()
        del spec["state"]
        module = AnsibleModule(argument_spec = spec,
                                    supports_check_mode =True)
        
        filter = gcs_util.read_keys(
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
        for g in collections:
            if not gcs_util.is_changed(g, filter):
                results += [g]
        module.exit_json(changed = False, results = results)

    except globus_sdk.GlobusError as e:
        module.fail_json(msg = str(e))

if __name__ == '__main__':
    main()