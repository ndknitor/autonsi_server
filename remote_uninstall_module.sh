#!/bin/bash

remote_uninstall_module() {
    local SSH_USERNAME="$1"
    local SSH_PRIVATE_KEY_PATH="$2"
    local SSH_HOST="$3"
    local ADDONS_PATH="$4"
    local DATABASE_NAME="$5"
    local MODULE_NAME="$6"
    IFS=',' read -ra paths <<< "$ADDONS_PATH"
    local MAIN_ADDONS_PATH="${paths[0]}"
    ssh -o StrictHostKeyChecking=no -i "$SSH_PRIVATE_KEY_PATH" "$SSH_USERNAME@$SSH_HOST" <<EOF
        echo "self.env['ir.module.module'].search([('name', '=', '$MODULE_NAME')]).button_immediate_uninstall()" | sudo -u odoo python3 /odoo/odoo-server/odoo-bin shell -d $DATABASE_NAME --addons-path=$ADDONS_PATH --dev all --stop-after-init
        sudo rm -rf "$MAIN_ADDONS_PATH"/"$MODULE_NAME"
        sudo service odoo-server restart
EOF
}
remote_uninstall_module "$@"
