#!/bin/sh
java -Djava.awt.headless=true -classpath .:./lib/pircbot.jar:./lib/PieSpy.jar:./lib/JMegaHal.jar:./lib/Reminder.jar org.gentoo.rizzo.rizbot.RizBot ./config.ini
