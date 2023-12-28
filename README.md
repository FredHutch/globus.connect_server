
This collection implements ansible modules for managing globus endpoints, storage gateways and collections. Storage gateways and collections can be modified, created and deleted. Endpoints can be modified only.

Additionally there are **collection_info** and **storage_gateway_info** modules that will return a list of objects that match provided attribute values without modifying anything. 

Supported attributes are documented in corresponding schemas:

* [Endpoint](https://docs.globus.org/globus-connect-server/v5/api/schemas/Endpoint_1_2_0_schema/)
* [Storage gateway](https://docs.globus.org/globus-connect-server/v5/api/schemas/StorageGateway_1_2_0_schema/)
* [Collection](https://docs.globus.org/globus-connect-server/v5/api/schemas/Collection_1_9_0_schema/)

If **id** is set and **state** is *present*, ansible will try to ensure all of the set attribute values match corresponding object in GCS while ignoring all unset attribute values. 

If **id** is not set and **state** is *present*, ansible will create a new object. 

In addition to the above, every module supports attributes **gcs_address**, **endpoint_id**, **client_secret** and **client_id**. Endpoint id is not necessary as it can be obtained by modules automatically. **module_defaults** can be used to set all of those in one place (see playbook examples below). 

**storage_gateway** and **collection** support **state** attribute (either *present* or *absent*).

Examples:

Set module defaults for endpoint discovery and authentication. **endpoint_id** is optional and can be inferred at the cost of additional call to /api/info at runtime. 

```
- hosts: localhost
  module_defaults:
    group/nesi.globus.gcs:
      gcs_address: "xxxxx.xxxx.data.globus.org"
      endpoint_id: "xxxxxxxxxxxxxxxxxxxxxxxxx"
      client_id: "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxx"
      client_secret: "xxxxxxxxxxxxxxxxxxxxxxxxxxxx"
```

Modify endpoint attributes:

```
- nesi.globus.endpoint:
    display_name: "Test Endpoint"
    contact_email: "example@example.com"
    contact_info: "0123456789"
    department: "ITS"
    description: "Endpoint description"
    keywords: ["test1", "test2", "test3"]
    #max_concurrency: 5
    #preferred_concurrency: 5
    #max_parallelism: 10
    #preferred_parallelism: 10
    gridftp_control_channel_port: 443
    network_use: "aggressive"
    public: False
    allow_udt: False
    subscription_id: "xxxxxxxxxxxxxxxxxxxxxxxx"
    organization: "Org Name"
```

Create new storage gateway:

```
- name: create new storage gateway
  nesi.globus.storage_gateway:
    display_name: "Example Gateway 3"
    allowed_domains:
      - example.com
    connector_id: Posix
```

Modify existing gateway and collection:

```
- nesi.globus.storage_gateway:
    id: "xxxxxxxxxxxxxxxxxxxxxxxxxx"
    display_name: "Example Gateway 1"
    allowed_domains:
      - example.com
    connector_id: Posix
    authentication_timeout_mins: 15840
  register: gateway_result
- nesi.globus.collection:
    id: "xxxxxxxxxxxxxxxxxxxxxxxxxxxx"
    collection_type: "mapped"
    domain_name: "test.xxxxx.xxxx.data.globus.org"
    display_name: "Collection 1"
    public: False
    collection_base_path: "/data"
    storage_gateway_id: "{{ gateway_result.data.id }}"
```

Delete storage gateway:

```
- nesi.globus.storage_gateway:
    id: "xxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
    state: absent
```

Obtain and print a list of all mapped collections:

```
- name: Get all collections
  nesi.globus.collection_info:
    collection_type: "mapped"
  register: collections_task
- debug: msg="{{ collections_task.results }}"
```

Get properties of storage gateway (or empty list if it doesn't exist):

```
- name: Get all collections
  nesi.globus.storage_gateway_info:
    id: "xxxxxxxxxxxxxxxxxxxxx"
  register: gateways_task
- debug: msg="{{ collections_task.results | length }}"
```