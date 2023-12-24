from ansible.module_utils.basic import AnsibleModule
import globus_sdk
from globus_sdk import GlobusError, GlobusAPIError
from globus_sdk.services.auth.errors import AuthAPIError
import os

import ansible_collections.nesi.globus.plugins.module_utils.globus_util as globus_util # type: ignore

class StorageGatewayModule(globus_util.GCSModule):

    def object_spec(self):
        return dict(
            admin_managed_credentials = dict(type='bool',
                                            required=False),
            allowed_domains = dict(type='list', required = False),
            authentication_timeout_mins = dict(type='int', 
                                            required = False),
            connector_id = dict(type = globus_util.gcs_get_connector_id,
                                required=False),
            display_name = dict(type='str', required=False),
            high_assurance = dict(type='bool', required=False),
            identity_mappings = dict(type='list', required=False),
            load_dsi_module = dict(type='string', required=False),
            policies = dict(type='dict', required=False),
            process_user = dict(type='string', required=False),
            require_mfa = dict(type='bool', required=False),
            restrict_paths = dict(type='dict', required=False),
            users_allow = dict(type='list', required=False),
            users_deny = dict(type='list', required=False)
        )

    def create(self, new):
        return self.gcs_client.create_storage_gateway(new).data

    def update(self, new):
        id = self.module.params["id"]
        self.gcs_client.update_storage_gateway(id, new)
        return self.gcs_client.get_storage_gateway(id, 
                        include = "private_policies").data

    def delete(self):
        try:
            id = self.module.params["id"]
            result = self.gcs_client.delete_storage_gateway(id)
        except GlobusAPIError as e:
            if e.http_status == 404:
                return False
            raise e

    def old_state(self):
        id = self.module.params["id"]
        return self.gcs_client.get_storage_gateway(id, 
                      include = "private_policies").data

    def data_type(self):
        return "storage_gateway#1.2.0"  

def main():
    try:
        module = StorageGatewayModule()
        module.execute()
    except GlobusError as e:
        module.fail(msg = str(e))

if __name__ == '__main__':
    main()
