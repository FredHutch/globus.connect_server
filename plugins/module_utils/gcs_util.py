'''shared utility functions for GCS ansible modules.'''
from enum import Enum

import globus_sdk


def storage_gateway_spec():
    return dict(
        admin_managed_credentials = dict(type='bool',
                                        required=False),
        allowed_domains = dict(type='list', required = False),
        authentication_timeout_mins = dict(type='int', 
                                        required = False),
        connector_id = dict(type = get_connector_id,
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

def collection_spec():
    return dict(
        allow_guest_collections = dict(type='bool', 
                                    required=False),
        authentication_timeout_mins = dict(type = 'int',
                                        required = False),
        collection_base_path = dict(type = 'str', required = False),
        collection_type = dict(type = 'str', 
                            choices = ["mapped", "guest"],
                            required = True),
        connector_id = dict(type = get_connector_id,
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

def endpoint_spec():
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
    '''globus sdk functions raise exceptions on 404 status code.
       This decorator makes it return None instead.
    '''
    def g(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except globus_sdk.GlobusAPIError as e:
            if e.http_status == 404:
                return None
            else:
                raise e
    return g
