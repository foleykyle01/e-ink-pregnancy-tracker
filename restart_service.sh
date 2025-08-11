#!/bin/bash
# Script to restart the pregnancy tracker service
# This can be called without sudo password via sudoers configuration

systemctl restart pregnancy-tracker-auto
exit $?