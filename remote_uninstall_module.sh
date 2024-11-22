#!/bin/bash

remote_uninstall_module() {
    local SSH_USERNAME="$1"
    local SSH_PRIVATE_KEY_PATH="$2"
    local SSH_HOST="$3"
    local ADDONS_PATH="$4"
    local DATABASE_NAME="$5"
    local MODULE_NAME="$6"
    local CONTAINER_NAME="$7"


    ssh -o StrictHostKeyChecking=no -i "$SSH_PRIVATE_KEY_PATH" "$SSH_USERNAME@$SSH_HOST" <<EOF

docker exec $CONTAINER_NAME bash -c "echo \"self.env['ir.module.module'].search([('name', '=', '$MODULE_NAME')]).button_immediate_uninstall()\" | odoo shell -d $DATABASE_NAME --stop-after-init"
rm -rf $ADDONS_PATH/$CONTAINER_NAME

EOF
}
remote_uninstall_module "$@"
