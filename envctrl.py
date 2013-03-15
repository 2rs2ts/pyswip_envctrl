## Python main program

"""
    This file is part of pyswip_envctrl.

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

from pyswip import *
import math

class Occupant(object):
    """An occupant of the building."""
    def __init__(self, pid, temp, hum, lux):
        """pid: person ID, temp: preferred temperature, hum: preferrred relative humidity, lux: preferred lux"""
        self.pid = pid
        self.temp = temp
        if hum > 100: self.hum = float(100)
        elif hum < 0: self.hum = float(0)
        else: self.hum = hum
        self.lux = lux

    def __str__(self):
        return "Occupant " + str(self.pid) + \
               " with preferences " + \
               str(self.temp) + "F, " + \
               str(self.hum) + "% humidity, and " + \
               str(self.lux) + "lx."
        

class Room(object):
    """A room equipped with a sensor."""
    def __init__(self, temp, hum, lux, savings, prolog):
        """temp = the outside temperature, hum = the oustide humidity, lux = the outside lux, savings = the savings percent, prolog: a prolog database"""
        self.occupants = []
        # Fixes for bounds
        if temp > 113: self.temp = float(113)
        elif temp < 32: self.temp = float(32)
        else: self.temp = float(temp)
        if hum > 100:
            self.hum = float(100)
            self.outsideHum = float(100)
        elif hum < 0:
            self.hum = float(0)
            self.outsideHum = float(0)
        else:
            self.hum = float(hum)
            self.outsideHum = float(hum)
        if savings < 0: self.savings = float(0)
        elif savings > 100: self.savings = float(100)
        else: self.savings = float(savings)
        if lux <= 0:
            self.lux = window(float(0.0001))
            self.outsideLux = float(0.0001)
        else:
            self.lux = window(float(lux)) 
            self.outsideLux = float(lux)
        # Let be
        self.outsideTemp = temp
        self.prolog = prolog

    def __str__(self):
        twrite,hwrite,lwrite = self.update()
        toReturn = "* This room's data:\n" + \
               "* There are " + str(len(self.occupants)) + " occupants in this room.\n" + \
               "* The average user prefs: " + \
               str(self.avgTemp()) + "F, " + \
               str(self.avgHumidity()) + "% humidity, " + \
               str(self.avgLux()) + " lx.\n" + \
               "* Outside conditions: " + \
               str(self.outsideTemp) + "F, " + \
               str(self.outsideHum) + "% humidity, " + \
               str(self.outsideLux) + " lx.\n" + \
               "* Window effect on indoor light: " + str(window(self.outsideLux)-self.outsideLux) + " lx.\n" + \
               "* Desired savings level: " + str(self.savings) + "%\n" + \
               "* System-decided room settings: " + \
               str(self.temp) + "F, " + \
               str(self.hum) + "% humidity, " + \
               str(self.lux) + " lx.\n" + \
               "*\tTemperature message: " + twrite + "\n" + \
               "*\tHumidity message: " + hwrite + "\n" + \
               "*\tLighting mesage: " + lwrite
        return toReturn

    def avgTemp(self):
        temps = [occupant.temp for occupant in self.occupants]
        med = median(temps)
        if med == None: return self.outsideTemp
        else: return med

    def avgHumidity(self):
        humidities = [occupant.hum for occupant in self.occupants]
        med = median(humidities)
        if med == None: return self.outsideHum
        else: return med

    def avgLux(self):
        luxes = [occupant.lux for occupant in self.occupants]
        med = median(luxes)
        if med == None: return self.outsideLux
        else: return med

    def leaving(self,occupant):
        if occupant in self.occupants:
            self.occupants.remove(occupant)

    def entering(self,occupant):
        if occupant not in self.occupants:
            self.occupants.append(occupant)

    def update(self):
        """The cool part! Prolog!!"""
        if len(self.occupants) > 0:
            # Query for the temperature setting.
            tempquery = list(self.prolog.query
                             ("setto(" + \
                             str(self.outsideTemp) + "," + \
                             str(self.avgTemp()) + "," \
                             "113,32," + \
                             str(self.savings) + ",Yield, Write)"))
            self.temp = float(tempquery[0]["Yield"])
            # Query for the humidity setting.
            humquery = list(self.prolog.query
                            ("setto(" + \
                             str(self.outsideHum) + "," + \
                             str(self.avgHumidity()) + "," \
                             "100,0," + \
                             str(self.savings) + ",Yield,Write)"))
            self.hum = float(humquery[0]["Yield"])
            # Query for the lighting setting.
            luxquery = list(self.prolog.query
                            ("setto(" + \
                            str(window(self.outsideLux)) + "," + \
                            str(self.avgLux()) + "," \
                            "130000,0," + \
                            str(self.savings) + ",Yield, Write)"))
            self.lux = float(luxquery[0]["Yield"])
            tempmessage = ""
            for char in tempquery[0]["Write"]:
                tempmessage += chr(char)
            hummessage = ""
            for char in humquery[0]["Write"]:
                hummessage += chr(char)
            luxmessage = ""
            for char in luxquery[0]["Write"]:
                luxmessage += chr(char)
            return tempmessage,hummessage,luxmessage
        else:
            if self.outsideTemp > 113: self.temp = float(113)
            elif self.outsideTemp < 32: self.temp = float(32)
            else: self.temp = self.outsideTemp
            self.hum = self.outsideHum
            self.lux = window(self.outsideLux)
            return "The goal was achieved.","The goal was achieved.","The goal was achieved."

class EmergencyWarning(Warning):
    pass

class WorldOnFireWarning(EmergencyWarning):
    pass

class AbsoluteZeroWarning(EmergencyWarning):
    pass

class SunIsTouchingEarthWarning(EmergencyWarning):
    pass

def window(outsideLux):
    """Returns the effect of windows on lux."""
    if outsideLux > 1:
        percent = 1/math.log(outsideLux)
        if percent > 100:
            percent = 100.0
        return outsideLux*percent
    else:
        return outsideLux / 10.0

def median(values):
    values.sort()
    if len(values) == 0:
        return None
    elif len(values) % 2 == 1:
        return values[((len(values)+1)/2)-1]
    else:
        return (float(values[(len(values)/2)-1] + values[len(values)/2]) / 2)


def main():
    exit = None
    quit = None
    prolog = Prolog()
    prolog.consult("envctrl.pl")
    currentPid = 0
    allOccupants = []
    while True:
        try:
            outsideTemp = float(input("What is the outside temperature, in Fahrenheit? "))
            if outsideTemp < -459:
                raise AbsoluteZeroWarning("The world has reached absolute zero. The system would normally detect an emergency, but particle motion has stopped entirely.")
            elif outsideTemp > 1000:
                raise WorldOnFireWarning("The air is hotter than a campfire. Only you can prevent forest fires.")
            outsideHum = float(input("What is the outside humidity, between 0 and 100%? "))
            outsideLux = float(input("What is the outside lux? "))
            if outsideLux > 130000:
                raise SunIsTouchingEarthWarning("The outdoors is brighter than direct sunlight. The sun is probably touching the Earth. That's bad!")
            savings = float(input("Please select a desired savings level: "))
            break
        except Warning as emergency:
            print emergency
            raise EmergencyWarning("The system will now pleasantly crash. Have a nice day.")
        except Exception:
            print "There was an error, please try again."
            pass
    room = Room(outsideTemp, outsideHum, outsideLux, savings, prolog)
    print "\n" + str(room)
    selection = -1
    while selection != 0:
        print "\nAction?"
        print "0) Exit this application."
        print "1) List the room's current occupants."
        print "2) Add an occupant."
        print "3) Remove an occupant."
        print "4) Change an occupant's preferences."
        print "5) Change the desired savings level."
        print "6) Update the outside weather."
        print "7) Report an emergency."
        try:
            selection = int(input(">> "))
        except Exception:
            print "\nThat is not an option."
            selection = -1
        if selection == 1:
            if len(room.occupants) != 0:
                for occupant in room.occupants:
                    print "  " + str(occupant)
                print ""
            else:
                print "\nThere are no occupants.\n"
        if selection == 2:
            try:
                newOcc = int(input("  Is this a new occupant? 1 for yes, 0 for no. "))
            except Exception:
                print "  That is not an option."
                newOcc = -1
            if newOcc == 1:
                try:
                    occTemp = float(input("  What is this new occupant's preference for temperature? "))
                    occHum = float(input("  What is this new occupant's preference for humidity? "))
                    occLux = float(input("  What is this new occupant's preference for lux? "))
                    newOcc = Occupant(currentPid, occTemp, occHum, occLux)
                    room.entering(newOcc)
                    print "  " + str(newOcc) + " has entered the room."
                    allOccupants.append(newOcc)
                    currentPid += 1
                    print "  The room will now automatically adjust for the new occupant."
                    print "\n" + str(room)
                except Exception as e:
                    print e
                    print "  There was an invalid selection. Returning to menu."
            elif newOcc == 0:
                try:
                    occPid = int(input("  What is the id of this occupant? "))
                    if occPid < currentPid:
                        for occupant in allOccupants:
                            if occupant.pid == occPid:
                                room.entering(occupant)
                                print "  " + str(occupant) + " has entered the room."
                                print "  The room will now automatically adjust for the new occupant."
                                print "\n" + str(room)
                    else:
                        print "  That occupant does not exist."
                except Exception:
                    print "  There was an invalid selection. Returning to menu."
            else:
                print "  There was an invalid selection. Returning to menu."
        elif selection == 3:
            try:
                occPid = int(input("  What is the id of the occupant who is leaving? "))
                if occPid < currentPid:
                    for occupant in room.occupants:
                        if occupant.pid == occPid:
                            room.leaving(occupant)
                            print "  " + str(occupant) + " has left the room."
                            print "  The room will now automatically adjust for less occupants."
                            print "\n" + str(room)
                else:
                    print "  That occupant does not exist."
            except Exception:
                print "  There was an invalid selection. Returning to menu."
        elif selection == 4:
            try:
                occPid = int(input("  What is the id of this occupant? "))
                if occPid < currentPid:
                    for occupant in allOccupants:
                        if occupant.pid == occPid:
                            occupant.temp = float(input("  What is this occupant's new preference for temperature? "))
                            occupant.hum = float(input("  What is this occupant's new preference for humidity? "))
                            occupant.lux = float(input("  What is this occupant's new preference for lux? "))
                            print "  The room will now automatically adjust for new preferences."
                            print "\n" + str(room)
                else:
                    print "  That occupant does not exist."
            except Exception:
                print "  There was an invalid selection. Returning to menu."
        elif selection == 5:
            try:
                room.savings = int(input("  Please select a new desired savings level: "))
                if room.savings < 0: room.savings = float(0)
                elif room.savings > 100: room.savings = float(100)
                print "  The room will now automatically adjust for a new desired savings level."
                print "\n" + str(room)
            except Exception:
                print "  There was an invalid selection. Returning to menu."
        elif selection == 6:
            try:
                room.outsideTemp = float(input("What is the outside temperature, in Fahrenheit? "))
                room.outsideHum = float(input("What is the outside humidity, between 0 and 100%? "))
                room.outsideLux = float(input("What is the outside lux (decimals allowed)? "))
                print "  The room will now automatically adjust for the new outside weather."
                print "\n" + str(room)
            except Exception:
                print "  There was an invalid selection. Returning to menu."
        elif selection == 7:
            raise EmergencyWarning("There is an emergency of some sort and everyone should evacuate.")
    print "The application will now quit. All user information has been lost."
    return 0

main()
