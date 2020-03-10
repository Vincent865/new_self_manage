#!/bin/sh

echo "Starting merge JS KEA-U1000 code!"

rm -f screen/kea-u1000.js

cat screen/kea-u1000/index/HeaderController.js\
	spacer.js\
	screen/kea-u1000/index/MenuControlle.js\
	spacer.js\
	screen/kea-u1000/home/HomeController.js\
	> screen/kea-u1000.js

echo "Merge JS KEA-U1000 code done!"

