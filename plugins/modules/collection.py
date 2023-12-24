from ansible.module_utils.basic import AnsibleModule
import globus_sdk
from globus_sdk import GlobusError
from globus_sdk.services.auth.errors import AuthAPIError
import os

import ansible_collections.nesi.globus.plugins.module_utils.globus_util as globus_util # type: ignore

class CollectionModule(globus_util.GCSModule):

    def object_spec(self):
        return dict(
            allow_guest_collections = dict(type='bool', 
                                        required=False),
            authentication_timeout_mins = dict(type = 'int',
                                            required = False),
            collection_base_path = dict(type = 'str', required = False),
            collection_type = dict(type = 'str', 
                                choices = ["mapped", "guest"],
                                required = True),
            connector_id = dict(type = globus_util.gcs_get_connector_id,
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

    def create(self, new):
        return self.gcs_client.create_collection(new).data

    def update(self, new):
        id = self.module.params["id"]
        self.gcs_client.update_collection(id, new)
        return self.gcs_client.get_collection(id, 
                                query_params = { 
                                    "include": "private_policies"
                                }).data

    def delete(self):
        try:
            id = self.module.params["id"]
            result = self.gcs_client.delete_collection(id)
        except GlobusAPIError as e:
            if e.http_status == 404:
                return False
            raise e

    def old_state(self):
        id = self.module.params["id"]
        return self.gcs_client.get_collection(id, 
                                query_params = { 
                                    "include": "private_policies"
                                }).data

    def data_type(self):
        return "collection#1.9.0"  

def main():
    try:
        module = CollectionModule()
        module.execute()
    except GlobusError as e:
        module.fail(msg = str(e))

if __name__ == '__main__':
    main()