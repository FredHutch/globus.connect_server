
Example playbook. 
```
- hosts: localhost
  module_defaults:
    group/nesi.globus.gcs:
      gcs_address: "xxxxx.xxxx.data.globus.org"
      client_id: "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxx"
      client_secret: "xxxxxxxxxxxxxxxxxxxxxxxxxxxx"
  tasks:
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
    - nesi.globus.storage_gateway:
        id: "xxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
        state: absent
    - name: create new storage gateway
      nesi.globus.storage_gateway:
        display_name: "Example Gateway 3"
        allowed_domains:
          - example.com
        connector_id: Posix
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