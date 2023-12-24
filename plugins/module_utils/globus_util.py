from globus_sdk import (
    ConfidentialAppAuthClient,
    ClientCredentialsAuthorizer,
    GCSClient
)

from abc import ABC, abstractmethod

def gcs_get_connector_id(id):
    connector_dict = {
        "Box": "7c100eae-40fe-11e9-95a3-9cb6d0d9fd63",
        "Ceph": "1b6374b0-f6a4-4cf7-a26f-f262d9c6ca72",
        "Google Cloud Storage": "56366b96-ac98-11e9-abac-9cb6d0d9fd63",
        "Google Drive":"976cf0cf-78c3-4aab-82d2-7c16adbcc281",
        "Posix": "145812c8-decc-41f1-83cf-bb2a85a2a70b",
        "S3": "7643e831-5f6c-4b47-a07f-8ee90f401d23",
        "SpectraLogic BlackPearl": "7e3f3f5e-350c-4717-891a-2f451c24b0d4"
    }
    return connector_dict[id]


from ansible.module_utils.basic import AnsibleModule

class GCSModule(ABC):

    def __init__(self):
        object_spec = self.object_spec()
        spec = self.common_spec() | object_spec
        self.object_spec = object_spec
        self.module = AnsibleModule(argument_spec=spec,
                                    supports_check_mode=True)
        self.gcs_client = self.create_gcs_client()

    def execute(self):
        id = self.module.params["id"]
        state = self.module.params["state"]
        
        if (state == "absent" and id is None):
            msg = "cannot delete entity without knowing its ID"
            self.module.fail_json(msg = msg)

        if (state == "absent"):
            changed = self.delete()
            self.module.exit_json(changed = changed, id = id)

        new = self.new_state()

        if (id is None):
            new = self.create(new)
            self.module.exit_json(changed = True, data = new)

        old = self.old_state()
        

        changed = GCSModule.compare(old, new)
        if changed:
            updated = self.update(new)
            self.module.exit_json(changed = True, data = updated)
        else:
            self.module.exit_json(changed = False, data = old)

    @abstractmethod
    def create(self, new):
        pass

    @abstractmethod
    def update(self, new):
        pass

    @abstractmethod
    def delete(self):
        pass

    @abstractmethod
    def old_state(self):
        pass

    @abstractmethod
    def data_type(self):
        pass

    @abstractmethod
    def object_spec(self):
        pass

    def new_state(self):
        new = {"DATA_TYPE": self.data_type()}
        for k in self.object_spec.keys():
            if self.module.params[k] is not None:
                new[k] = self.module.params[k]
        return new

    @staticmethod
    def compare(old, new):
        for k in (new.keys() - ["DATA_TYPE"]):
            if (k not in old) or (old[k] != new[k]):
                return True
        return False

    def create_gcs_client(self):
        address = self.module.params["gcs_address"]
        endpoint_id = self.module.params["endpoint_id"]
        client_id = self.module.params["client_id"]
        client_secret = self.module.params["client_secret"]

        # discover endpoint id from /api/info.
        if endpoint_id is None:
            gcs_tmp = GCSClient(gcs_address = address)
            info = gcs_tmp.get("info").data["data"]
            for i in info:
                if "endpoint_id" in i:
                    endpoint_id = i["endpoint_id"]
                    self.module.params["endpoint_id"] = endpoint_id
                    break

        client = ConfidentialAppAuthClient(client_id, client_secret)
        scope_builder = GCSClient.get_gcs_endpoint_scopes(endpoint_id)
        scopes = scope_builder.manage_collections
        cc_authorizer = ClientCredentialsAuthorizer(client, scopes)

        return GCSClient(gcs_address = address, 
                     authorizer = cc_authorizer)

    def common_spec(self):
        return dict(
            gcs_address =   dict(type='str', required=True),
            endpoint_id =   dict(type='str', required=False),
            id =   dict(type='str', required=False),
            client_id =     dict(type = 'str', 
                             required = False,
                             no_log = True),
            client_secret = dict(type='str', 
                             required=False,
                             no_log = True),
            state =         dict(type = 'str',
                                 required = False,
                                 choices = ["present", "absent"],
                                 default = "present")
        )
    
    def fail(self, **kwargs):
        self.module.fail_json(**kwargs)