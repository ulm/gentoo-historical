#!/bin/bash																				
#Creator: ZhEN																		
#Date: 1/10/03																		
#																							
#This just creates the doc tarball that can be downloaded by users so that they can	
#modify docs, submit new bugs, etc.													
#																						
#####################################################################################

[ -z ${WEBROOT} ] && echo "Webroot is not set, exiting" &&	exit 1
DOCROOT="${WEBROOT}/doc"
tar -cf ${DOCROOT} ${WEBROOT}/dyn/docs-latest.tar 2&1> /dev/null
bzip2 -z ${WEBROOT}/dyn/docs-latest.tar 2&1> /dev/null

