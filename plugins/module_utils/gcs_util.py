import globus_sdk

from enum import Enum

class Action(Enum):
    NOTHING = 0
    CREATE  = 1
    UPDATE  = 2
    DELETE =  3

def plan(desired, actual):
    if desired is None:
        if actual is None:
            return Action.NOTHING
        else:
            return Action.DELETE
    
    if actual is None:
        return Action.CREATE
    
    if is_changed(actual, desired):
        return Action.UPDATE
    
    return Action.NOTHING

def is_changed(old, new):
    for k in new.keys():
        if (k not in old) or (old[k] != new[k]):
            return True
    return False

def get_connector_id(id):
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

def common_spec():
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

def create_gcs_client(module):
    address = module.params["gcs_address"]
    endpoint_id = module.params["endpoint_id"]
    client_id = module.params["client_id"]
    client_secret = module.params["client_secret"]

    # discover endpoint id from /api/info.
    if endpoint_id is None:
        gcs_tmp = globus_sdk.GCSClient(gcs_address = address)
        info = gcs_tmp.get("info").data["data"]
        for i in info:
            if "endpoint_id" in i:
                endpoint_id = i["endpoint_id"]
                module.params["endpoint_id"] = endpoint_id
                break
    
    client = globus_sdk.ConfidentialAppAuthClient(client_id, client_secret)
    scope_builder = globus_sdk.GCSClient.get_gcs_endpoint_scopes(endpoint_id)
    scopes = scope_builder.manage_collections
    cc_authorizer = globus_sdk.ClientCredentialsAuthorizer(client, scopes)

    return globus_sdk.GCSClient(gcs_address = address, 
                     authorizer = cc_authorizer)

def read_keys(keys, module):
    result = {}
    for k in keys:
        v =  module.params[k]
        if v is not None:
            result[k] = v
    return result

# convert 404 status code to None
def none_if_not_found(f):

    def g(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except globus_sdk.GlobusAPIError as e:
            if e.http_status == 404:
                return None
            else:
                raise e
    return g