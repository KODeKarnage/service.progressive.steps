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
script_path      = __addon__.getAddonInfo('path')

logging          = True if __setting__('logging') == 'true' else False


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

                                step = off_set[1] * 60 + off_set[2]

                                log([now,step], 'appending')

                                self.click_action.append((now,step))

class Main:

    def __init__(self):

        self.get_set()

        self.click_action = []

        self.SM = Steps_Monitor(updater = self.get_set, click_action = self.click_action)

        self._daemon()


    def get_set(self):
        ''' updates and integrates the addon settings '''

        global logging
        setting_ids = ['2s','3s','4s','5s']

        logging     = True if __setting__('logging') == 'true' else False
        self.maxt   = float(__setting__('maxt'))
        self.delay  = float(__setting__('delay'))
        self.steps  = [(int(float(__setting__(x))) * 60) if __setting__(x + 'b') == 'true' else 0 for x in setting_ids ] + [0,0,0,0]

        log(self.maxt,'setting - maxt')
        log(self.delay, 'setting - delay')
        log(self.steps, 'setting - steps')


    def _action(self):
        ''' analyses the requests and makes the appropriate jump (if any) '''

        # count the items in click_action
        # identify the action
        # calculate the delta
        # clear the click action

        rec_step = self.click_action[-1][1]
        count = len(self.click_action)

        del self.click_action[:]

        if count > 1:

            log(rec_step, '_action rec_step')
            log(count, '_action count')

            direction = 1
            base = 0

            if rec_step < 0 :
                direction = -1

            # if any([rec_step > 60, rec_step < -60]):
            #     ''' steps above 60 seconds are considered big else small '''
            #     base = 4

            step = self.steps[min(base + count - 1, base + 3)] 


            if step:

                delta = (step * direction) - (count * rec_step)

                log(delta, 'delta')

                if delta:

                    gt = xbmc.Player().getTime()

                    resume_time = max(gt + delta, 0)

                    xbmc.Player().seekTime(resume_time) 

                    log('seeked')


    def delta_conv(self, dTime):

        return dTime.seconds + (dTime.microseconds / 1000000.0)


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


                ''' if the actions are different, remove the actions that dont match the last one '''

                last = 'none'
                for i, e in reversed(list(enumerate(self.click_action))):
                    log(i, 'item number')
                    log(last)
                    if last == 'none':
                        last = e[1]
                        continue
                    elif e[1] != last:
                        log('action removed, type')
                        log(self.click_action)
                        del self.click_action[: i + 1]
                    else:
                        log('item is the same')

                log('------------')
                log('---------------')
                log(self.click_action)

                if self.click_action:

                    ''' start with the last item, check each previous item to ensure that 
                    they are within the maxt, delete the ones that aren't '''

                    click_time = self.click_action[-1][0]
                    for i, e in reversed(list(enumerate(self.click_action))):

                        diff_time = self.delta_conv(click_time - e[0])

                        log(diff_time - self.maxt, 'time between clicks')

                        if diff_time > self.maxt:

                            log('action removed, time')
                            log(self.click_action)

                            del self.click_action[: i + 1]
                            break

                        else:
                            click_time = e[0]

                    log('--------')
                    log(self.click_action)

                    if self.click_action:

                        ''' check the current time against the max time, and action if it is greater than the delay '''

                        click_time = self.click_action[-1][0]
                        diff_time = self.delta_conv(datetime.datetime.now() - click_time)

                        log(diff_time, 'diff time')
                        log(self.delay,'delay')
                        log(diff_time - self.delay, 'time since last click')

                        if diff_time > self.delay:

                            log(self.click_action, '_daemon click_action')
                            self._action()

                            log('click_action cleared')


if __name__ == "__main__":
    Main()

