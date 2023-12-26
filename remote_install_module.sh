#!/bin/bash

remote_install_module() {
    local SSH_USERNAME="$1"
    local SSH_PRIVATE_KEY_PATH="$2"
    local SSH_HOST="$3"
    local ADDONS_PATH="$4"
    local GITHUB_URL="$5"
    local DATABASE_NAME="$6"
    local MODULE_NAME="$7"
    local GITHUB_BRANCH="$8"
    local MAIN_MODULE="$9"
    local GITHUB_PATH="$10"
    

    IFS=',' read -ra paths <<< "$ADDONS_PATH"

    local MAIN_ADDONS_PATH="${paths[0]}"

    # Check if the correct number of arguments are provided
    if [ "$#" -ne 10 ]; then
        echo "Usage: $0 <SSH_USERNAME> <SSH_PRIVATE_KEY_PATH> <SSH_HOST> <ADDONS_PATH> <GITHUB_URL> <DATABASE_NAME> <MODULE_NAME> <GITHUB_BRANCH> <GITHUB_PATH>"
        return 1
    fi

    # SSH into the remote server and check if the git_sparse_clone script exists in /tmp
    ssh -o StrictHostKeyChecking=no -i "$SSH_PRIVATE_KEY_PATH" "$SSH_USERNAME@$SSH_HOST" <<EOF
        function git_sparse_clone() (
          rurl="\$1" localdir="\$2" branch="\$3" && shift 3
          mkdir -p "\$localdir"
          cd "\$localdir"

          git init
          git remote add -f origin "\$rurl"

          git config core.sparseCheckout true

          # Loops over remaining args
          for i; do
            echo "\$i" >> .git/info/sparse-checkout
          done

          git pull origin "\$branch"
          for i; do
            mv "\$i"/* ./
            rm -rf "\$i"
          done
        )
        if [ "$MAIN_MODULE" == "True" ]; then
          sudo rm -rf "$MAIN_ADDONS_PATH"/"$MODULE_NAME"
          if [ "$GITHUB_PATH" == "" ]; then
              git_sparse_clone "$GITHUB_URL" "$MAIN_ADDONS_PATH" "$GITHUB_BRANCH" "$GITHUB_PATH"
          else
              git clone -b "$GITHUB_BRANCH" "$GITHUB_URL" "$MAIN_ADDONS_PATH"/"$MODULE_NAME"
          fi
          sudo -u odoo /odoo/odoo-server/odoo-bin -i "$MODULE_NAME" -d "$DATABASE_NAME" --addons-path="$ADDONS_PATH" --dev all --stop-after-init
        else
          if [ -d "$MAIN_ADDONS_PATH"/"$MODULE_NAME" ]; then
            echo "Skiping reinstall module"
          else
            if [ -n "$GITHUB_PATH" == "" ]; then
                git_sparse_clone "$GITHUB_URL" "$MAIN_ADDONS_PATH" "$GITHUB_BRANCH" "$GITHUB_PATH"
            else
                git clone -b "$GITHUB_BRANCH" "$GITHUB_URL" "$MAIN_ADDONS_PATH"/"$MODULE_NAME"
            fi
          fi
        fi
      exit
EOF
}

remote_install_module "$@"