#!/bin/bash

remote_install_module() {
    local SSH_USERNAME="$1"
    local SSH_PRIVATE_KEY_PATH="$2"
    local SSH_HOST="$3"
    local ADDONS_PATH="$4"
    local GITHUB_URL="$5"
    local DATABASE_NAME="$6"
    local MODULE_NAME="$7"
    local CONTAINER_NAME="$8"
    local MAIN_MODULE="$9"

    ssh -o StrictHostKeyChecking=no -i "$SSH_PRIVATE_KEY_PATH" "$SSH_USERNAME@$SSH_HOST" <<EOF


if [ "$MAIN_MODULE" == "True" ]; then
    git clone "$GITHUB_URL" "$ADDONS_PATH"/"$MODULE_NAME"
    docker exec "$CONTAINER_NAME" odoo -i "$MODULE_NAME" -d "$DATABASE_NAME" --stop-after-init
else
  if [ -d "$ADDONS_PATH"/"$MODULE_NAME" ]; then
    echo "Skiping reinstall module"
  else
    git clone "$GITHUB_URL" "$ADDONS_PATH"/"$MODULE_NAME"
    docker exec "$CONTAINER_NAME" odoo -i "$MODULE_NAME" -d "$DATABASE_NAME" --stop-after-init
  fi
fi


EOF
}

remote_install_module "$@"