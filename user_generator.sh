#!/bin/bash

# Set the number of users you want to add
NUM_USERS=30

# Loop through and execute the Docker command for each user
for ((i=0; i<NUM_USERS; i++)); do
    docker exec -e OC_PASS=test_password1234! --user www-data nextcloud /var/www/html/occ user:add --password-from-env locust_user$i
done
