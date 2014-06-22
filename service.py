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

def log():
    pass

def grab_JBL_iCal():
    '''
    grabs the iCal file from JB website and saves in local addon data folder
    '''
    pass


def parse_JBL_iCal():
    '''
    strips out the relevant data from the iCal file and saves it in a dict
    '''
    pass


def _daemon():
    '''
    stays alive and checks the time to see whether reminders are needed
        a) takes down notification after prescribed time
        b) updates time since start of show
    '''
    pass


def initiate_reminder():
    '''
        a) post icon from the home screen
        b) post notification
        c) post modal reminder
        d) play sound
    '''
    pass


if __name__ == "__main__":
    Main()
