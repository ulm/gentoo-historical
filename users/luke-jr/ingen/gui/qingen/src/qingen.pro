SOURCES	+= main.cpp
SOURCES += ui/objects.cpp
#SOURCES += ui/wizard.cpp
#HEADERS += ui/wizard.h
FORMS	= ui/wizard.ui
IMAGES	= images/ed-side.png \
	images/harddisk-icon.png \
	images/license-icon.png \
	images/op-side.png \
	images/software-icon.png \
	images/status-icon.png \
	images/users-icon.png
TEMPLATE	=app
CONFIG	+= qt warn_on
LANGUAGE	= C++
