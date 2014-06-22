#!/usr/bin/python
# -*- coding: utf-8 -*-
#
#     Copyright (C) 2014 KODeKarnage
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program. If not, see <http://www.gnu.org/licenses/>.
#

import xbmc
import xbmcaddon
import xbmcgui
import os
import urllib2


__addon__        = xbmcaddon.Addon('service.jblive.reminder')
__addonid__      = __addon__.getAddonInfo('id')
__setting__      = __addon__.getSetting
dialog           = xbmcgui.Dialog()
script_path       = __addon__.getAddonInfo('path')
addon_path       = xbmc.translatePath('special://home/addons')
user_data        = xbmc.translatePath( "special://userdata")
iCal_file        = os.path.join(user_data,'addon_data',os.path.basename(script_path),'basic.ics')


def log(msg, label=''):

    if label:
        combined_message = 'service.JBLIVE.reminder ::-:: ' + str(label) + ' = ' + str(msg)
    else:
        combined_message = 'service.JBLIVE.reminder ::-:: ' + str(msg)

    xbmc.log(msg=combined_message)




class show(object):


    def __init__(self, name, start, duration, icon):
        self.name = name
        self.start = start
        self.duration = duration
        self.icon = icon


    def initiate_reminder(self):
        '''
            a) post icon from the home screen
            b) post notification
            c) post modal reminder
            d) play sound
        '''
        pass


    def denitiate_reminder(self):
        '''
        takes down the notification
        '''
        pass        


class Main:

    def __init__(self):
        '''
        start up routine:
            a) grab JBL iCal file
            b) parse JBL iCal file
            c) start daemon loop
        '''

        self.iCal_loc = 'http://www.google.com/calendar/ical/jalb5frk4cunnaedbfemuqbhv4@group.calendar.google.com/public/basic.ics'
        self.iCal_Data = ''
        self.show_dict = {}

        self.grab_JBL_iCal()
        self.parse_JBL_iCal()
        self._daemon()


    def grab_JBL_iCal(self):
        '''
        grabs the iCal file from JB website and saves in local addon data folder
        '''

        try:
            self.iCal_Data = urllib2.urlopen(self.iCal_loc)
        except IOError as e:
            log("I/O error({0}): {1}".format(e.errno, e.strerror))
        else:
            log('unknown error occured in reading the iCal file')


    def parse_JBL_iCal(self):
        '''
        strips out the relevant data from the iCal file and creates a list of shows,

        '''

        # parse the data into a list of lines
        parsed = []
        if self.iCal_Data:
            for line in self.iCal_Data:
                parsed.append(line.rstrip())

            # group the vevents together
            grouped = []
            for entry in parsed:
                log(entry)

                l = len(grouped)

                if entry == 'BEGIN:VEVENT':
                    grouped.append([entry])
                elif not l:
                    continue
                else:
                    grouped[l-1].append(entry)

            for group in grouped:
                # turn each entry into a tuple
                # use the tuples to create a dict
                # find date of entry, if older than 3 days then break
                # use the name tuple as the base key
                # add the other entries as items within that dict[base key]


    ###########################
    ##########
    ##########
    ##########  handling overlaps
    ##########




    def convert_date(self, date_string):
        '''
        takes the date string from iCal and converts it to an actual date
        '''
        pass




    def process_entry(self, lst):
        pass

        # remove all instances of ";TZID=America/Los_Angeles"
        # get current time in that time zone, as that will be our current point of reference
        # all times will still be saved after conversion to OUR time zone

        # check if entry contains "RRULE", as this means it is set to repeat
        #               if any(['RRULE' in x for x in a]):
        #                       BETTER
        #               g = [x for x in a if 'RRULE' in x]
        #               if g:
        #       check for an UNTIL, if there is one, check if it is in the past, if it is then ignore the RRULE
        #       get the start time and date from DTSTART
        #       get the end time from DTEND
        #       get the days and the frequency from RRULE
        #       find the day immediately after that start date
        #       collect the EXDATES
        #       then cylce FREQ until the value is greater than the current day AND that date ISNT an EXDATE
        # if entry doesnt contain RRULE, then it is a one-off show, and you need to check DTSTART to see if it
        #       is set in the future, if it isnt, then ignore it

        # return {NAME:{localstartdatetime:xxx, localenddatetime:xxx}}


    def _daemon(self):
        '''
        stays alive and checks the time to see whether reminders are needed
            a) initiates reminder
            b) takes down notification after prescribed time
            c) updates time since start of show
            d) periodically updates with a new file from JB
        '''
        pass


if __name__ == "__main__":
    Main()
