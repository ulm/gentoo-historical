SOURCES	+= main.cpp \
	ui/objects.cpp
HEADERS	+= main.h \
	ui/objects.h
FORMS	= ui/wizard.ui
IMAGES	= images/ed-side.png \
	images/harddisk-icon.png \
	images/license-icon.png \
	images/op-side.png \
	images/software-icon.png \
	images/status-icon.png \
	images/users-icon.png
TEMPLATE	=app
CONFIG	+= qt warn_on debug
LANGUAGE	= C++
