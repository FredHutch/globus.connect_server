from ansible.module_utils.basic import AnsibleModule
import globus_sdk
from globus_sdk import GlobusError
from globus_sdk.services.auth.errors import AuthAPIError

import ansible_collections.nesi.globus.plugins.module_utils.globus_util as globus_util # type: ignore

import os

class EndpointModule(globus_util.GCSModule):

    def __init__(self):
        super().__init__()
        self.module.params["id"] = self.module.params["endpoint_id"]

    def object_spec(self):
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

    def create(self, new):
        id = self.module.params["id"]
        msg = (
            f"Endpoint with id {id} does not exist. "
            "This module doesn't know how to create new endpoints"
        )
        raise NotImplementedError(msg)

    def update(self, new):
        return self.gcs_client.patch("endpoint", 
                        encoding = "json", 
                        data = new).data

    def delete(self):
        msg = "This module doesn't know how to delete endpoints"
        raise NotImplementedError(msg)        

    def old_state(self):
        return self.gcs_client.get("endpoint").data["data"][0]

    def data_type(self):
        return "endpoint#1.2.0"

def main():
    try:
        module = EndpointModule()
        module.execute()
    except GlobusError as e:
        module.fail(msg = str(e))

if __name__ == '__main__':
    main()