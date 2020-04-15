# terraform-inventory (v0.9) is not working well with terraform (v0.12.6).
# This script creates the hosts file used by ansible.
# First run "terraform show -json > current_state"
import json


with open('current_state') as json_file:
    data = json.load(json_file)
    file = open('../ansible/hosts', 'w')

    file.write('[nfs_server]\n')
    file.write([obj for obj in data['values']['root_module']['resources'] if
                obj['address'] == 'openstack_compute_instance_v2.nfs_server'][0]['values']['access_ip_v4'] + '\n')
    file.write('\n')

    file.write('[postgres]\n')
    file.write([obj for obj in data['values']['root_module']['resources'] if obj['address'] == 'openstack_compute_instance_v2.postgres'][0]['values']['access_ip_v4'] + '\n')
    file.write('\n')

    file.write('[sequence_search]\n')
    file.write([obj for obj in data['values']['root_module']['resources'] if obj['address'] == 'openstack_compute_floatingip_associate_v2.sequence_search'][0]['values']['floating_ip'] + '\n')
    file.write('\n')

    file.write('[producer]\n')
    file.write([obj for obj in data['values']['root_module']['resources'] if obj['address'] == 'openstack_compute_instance_v2.producer'][0]['values']['access_ip_v4'] + '\n')
    file.write('\n')

    file.write('[monitor]\n')
    file.write([obj for obj in data['values']['root_module']['resources'] if
                obj['address'] == 'openstack_compute_instance_v2.monitor'][0]['values']['access_ip_v4'] + '\n')
    file.write('\n')

    file.write('[consumers]\n')
    for obj in data['values']['root_module']['resources']:
        if obj['address'] == 'openstack_compute_instance_v2.consumers':
            file.write(obj['values']['access_ip_v4'] + '\n')

# print(json.dumps(output, indent=4))
