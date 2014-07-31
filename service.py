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
import datetime
import ast


__addon__        = xbmcaddon.Addon('service.progressive.steps')
__addonid__      = __addon__.getAddonInfo('id')
__setting__      = __addon__.getSetting
dialog           = xbmcgui.Dialog()
script_path       = __addon__.getAddonInfo('path')

logging    = True if __setting__('logging') == 'true' else False
maxt  = float(__setting__('maxt')) * 1000000
delay = float(__setting__('delay')) * 1000000

ACTION_STEP_FORWARD           = 20 
ACTION_STEP_BACK              = 21 
ACTION_BIG_STEP_FORWARD       = 22 
ACTION_BIG_STEP_BACK          = 23 

def log(msg, label=''):

    if logging:
        combined_message = 'service.progressive.steps ::-:: ' + str(label) + ' = ' + str(msg)
        xbmc.log(msg=combined_message)


class Steps_Monitor(xbmc.Monitor):
    ''' this monitor is simply to accommodate changes to the addon settings '''

    def __init__(self, *args, **kwargs):

        self.updater = kwargs['updater']
        self.click_action = kwargs['click_action']
        self.time_components = ['hours','minutes','seconds','milliseconds']

        xbmc.Monitor.__init__(self)
        
        log('Steps_Monitor created')


    def onSettingsChanged(self):

        self.updater()


    def onNotification(self, sender, method, data):

        log(data)

        if method == 'Player.OnSeek':

            d = ast.literal_eval(data)

            item = d.get('item','')

            if item:

                media_type = item.get('type', '') 

                if media_type in ['movie','episode']:

                    player = d.get('player','')

                    if player:

                        seek_offset = player.get('seekoffset','')

                        if seek_offset:

                            off_set = [ seek_offset.get(x,0) for x in self.time_components ]

                            log(off_set,'off_set')

                            # ['hours','minutes','seconds','milliseconds']

                            if not off_set[3] and not off_set[0]:
                                ''' if milliseconds and hours are zero, then 999/1000 the action is due to an automatic jump'''

                                now = datetime.datetime.now()

                                if not off_set[1] and off_set[2]:
                                    ''' if there are seconds but no minutes then assume a small step'''

                                    if off_set > 0:

                                        self.click_action.append((now,'SF'))
                                        log('SF')

                                    else:

                                        self.click_action.append((now,'SB'))
                                        log('SB')

                                if off_set[1] and not off_set[2]:
                                    ''' if there are minutes but no seconds then assume a big step'''

                                    if off_set > 0:

                                        self.click_action.append((now,'BF'))
                                        log('BF')

                                    else:

                                        self.click_action.append((now,'BB'))
                                        log('BB')


class Main:

    def __init__(self):

        self.steps = []
        self.get_set()

        self.click_action = []
        # [(time, action),(time, action),(time, action)]


        #Stinky = stinky_pete('dot.xml', script_path, 'Default', click_action = self.click_action, steps = self.steps)
        #Stinky.show()
        #Stinky = stinky_pete(xmlfile, scriptPath, 'Default', click_action = self.click_action, steps = self.steps)


        # mp = MyPlayer(click_action = self.click_action)

        self.SM = Steps_Monitor(updater = self.get_set, click_action = self.click_action)

        self._daemon()

        del self.SM


    def get_set(self):
        ''' updates and integrates the addon settings '''
        global logging
        global maxt
        global delay
        logging    = True if __setting__('logging') == 'true' else False
        maxt  = float(__setting__('maxt')) * 1000000
        delay = float(__setting__('delay')) * 1000000


        standard     = 1
        standard_big = 10

        s2 = int(float(__setting__('2s')))
        s3 = int(float(__setting__('3s')))
        s4 = int(float(__setting__('4s')))
        s5 = int(float(__setting__('5s')))
        b2 = int(float(__setting__('2b')))
        b3 = int(float(__setting__('3b')))
        b4 = int(float(__setting__('4b')))
        b5 = int(float(__setting__('5b')))

        small_steps_raw = [s2, s3, s4, s5]
        big_steps_raw   = [b2, b3, b4, b5]

        small = [x - standard     for x in small_steps_raw]
        big   = [x - standard_big for x in big_steps_raw]

        self.steps = small + big

        log(self.steps, 'steps')


    def _action(self):
        ''' analyses the requests and makes the appropriate jump (if any) '''

        # count the items in click_action
        # identify the action
        # calculate the delta
        # clear the click action

        action = self.click_action[-1][1]
        count = len(self.click_action)

        del self.click_action[:]

        if count > 1:

            log(action, '_action action')
            log(count, '_action count')

            direction = 1
            base = 0

            if action[-1] == 'B':
                direction = -1

            if action[0] == 'B':
                base = 4

            delta = self.steps[min(base + count - 1, base + 3)] * direction * 60

            log(delta, 'delta')

            if delta:
                log(xbmc.Player().getTime(), 'got time')
                resume_time = xbmc.Player().getTime() + delta
                xbmc.Player().seekTime(resume_time) 
                log('seeked')


    def delta_conv(self, dTime):

        return dTime.seconds * 1000000 + dTime.microseconds


    def _daemon(self):
        ''' bleeds for a week but doesnt die '''

        while not xbmc.abortRequested:

            xbmc.sleep(250)
            log('tick')

            if self.click_action:

                log('------------------------------------------------')
                log('------------')
                log('---------------')
                log(self.click_action)
                log('---------------------')
                log('--------------------------------')
                log('-----------------------------------------------')

                ''' if the actions are different, remove the actions that dont match the last one '''

                last = 'none'
                for i, e in reversed(list(enumerate(self.click_action))):
                    log(i, 'iiiiiiiiii')
                    log(last)
                    if last == 'none':
                        last = e[1]
                        continue
                    elif e[1] != last:
                        log('action removed, type')
                        log(self.click_action)
                        self.click_action = self.click_action[i:]
                        log(self.click_action)

                log('------------')
                log('---------------')
                log(self.click_action)


                ''' start with the last item, check each previous item to ensure that 
                they are within the maxt, delete the ones that aren't '''

                click_time = self.click_action[-1][0]
                for i, e in reversed(list(enumerate(self.click_action))):
                    diff_time = self.delta_conv(click_time - e[0])
                    if diff_time > maxt:
                        log('action removed, time')
                        log(self.click_action)
                        self.click_action = self.click_action[i:]
                        log(self.click_action)
                        break
                    else:
                        click_time = e[0]

                log('--------')
                log(self.click_action)

                ''' check the current time against the max time, and action if it is greater than the delay '''

                click_time = self.click_action[-1][0]
                diff_time = self.delta_conv(datetime.datetime.now() - click_time)

                log(diff_time, 'diff time')
                log(maxt,'delay')

                if diff_time > delay:
                    log(self.click_action, '_daemon click_action')
                    self._action()


                    log('click_action cleared')




if __name__ == "__main__":
    Main()

    del Main
