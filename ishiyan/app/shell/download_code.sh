#!/usr/bin/env bash

USERNAME=$1
if test -d /tmp/${USERNAME}; then
    zip /tmp/${USERNAME}.zip /tmp/${USERNAME}/* > /dev/null
    mv /tmp/${USERNAME}.zip /usr/local/openresty/nginx/html/ishiyan/statics/downloads/code
else
    echo 目录/tmp/${USERNAME}不存在
    exit 1
fi