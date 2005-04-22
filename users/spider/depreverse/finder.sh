#!/bin/bash

echo "Thinking about $1.."
etcat files $1 | ./deplister | while read FILE; do 
	qpkg -nc -f $FILE
done | sort -u
