#!/bin/sh

echo "Starting merge JS code"

./libraries/merge_libraries.sh
./screen/merge_base.sh
./screen/merge_kea-u1000.sh
./screen/merge_kea-u1142.sh
./screen/merge_kea-c200.sh

echo "Merge JS code done"

