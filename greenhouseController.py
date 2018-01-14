#!/usr/bin/env python
# -*- coding: utf-8 -*-

import mysql.connector  # Library for database
import serial   # Library for serial communication
import time     # Library for the delay

from mysql.connector import errorcode

''' Change this to function '''
try:
    ser = serial.Serial('/dev/cu.usbmodemFA131', 9600, timeout=0.5)
except:
    print("Exception in serial port")
    ser = None

time.sleep(4)   # we wait a little, so that the Arduino is ready.


def open_green_db():
    """ Database Connection and open """
    try:
        cnx = mysql.connector.connect(user='root',
                                      database='db_green_test')
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            print("Something is wrong with your user name or password")
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            print("Database does not exist")
        else:
            print(err)
        return None
    else:
        return cnx


''' Closing Database connector '''
def close_green_db(cnx):
    if cnx is not None:
        cnx.close

''' Get Equipment State '''
def get_equipment_state():
    cnx = open_green_db()
    if cnx is None:
        return None

    query = "SELECT Equipement, State from commandes"

    cursor = cnx.cursor()
    cursor.execute(query)
    equipment_state = {Equipement: State for (Equipement, State) in cursor}

    close_green_db(cnx)
    return equipment_state

''' Get Equipment State '''
def get_equipment_command():
    cnx = open_green_db()
    if cnx is None:
        return None

    query = "SELECT Equipement, Command from commandes"

    cursor = cnx.cursor()
    cursor.execute(query)
    equipment_command = {Equipement: Command for (Equipement, Command) in cursor}

    close_green_db(cnx)
    return equipment_command


def process_command_request():
    state = get_equipment_state()
    command_request = get_equipment_command()

    if ser is None:
        print("Error in accessing Serial port!")
        exit(1)

    if state is None:
        print "Error Getting State from Database"
        return

    if command_request is None:
        print "Error Getting Command from Database"
        return

    if state.get('Lamp') != command_request.get('Lamp'):
        print "Lamp Request"
        if command_request.get('Lamp') == 0:
            send_command_arduino("YELLOWOFF")
            print "Lamp OFF"
            update_state_command("Lamp", 0)

        if command_request.get('Lamp') == 1:
            send_command_arduino("YELLOWON")
            print "Lamp ON"
            update_state_command("Lamp", 1)

    if state.get('Valve') != command_request.get('Valve'):
        print "Valve Request"
        if command_request.get('Valve') == 0:
            send_command_arduino("GREENOFF")
            print "Valve OFF"
            update_state_command("Valve", 0)

        if command_request.get('Valve') == 1:
            send_command_arduino("GREENON")
            print "Valve ON"
            update_state_command("Valve", 1)


    if state.get('Fan') != command_request.get('Fan'):
        print "Fan Request"
        if command_request.get('Fan') == 0:
            send_command_arduino("REDOFF")
            print "Fan OFF"
            update_state_command("Fan", 0)

        if command_request.get('Fan') == 1:
            send_command_arduino("REDON")
            print "Fan ON"
            update_state_command("Fan", 1)

    if state.get('Pump') !=  command_request.get('Pump'):
        print "Pump Request"
        if command_request.get('Pump') == 0:
            send_command_arduino("BLUEOFF")
            print "Pump OFF"

        if command_request.get('Pump') == 1:
            send_command_arduino("BLUEON")
            print "Pump ON"

def send_command_arduino(command):
    ACK = ""
    while True:
        try:
            ser.write(command)
            ACK = str(ser.readline())
            if not ACK == "OK": break
        except:
            ''''''

def update_state_command(Equipment, state):
    cnx = open_green_db()
    if cnx is None:
        return None

    cursor = cnx.cursor()
    # UPDATE `db_green_test`.`commandes` SET `State`='1', `Command`='1' WHERE `Equipement`='Fan';
    cursor.execute("UPDATE commandes SET State=%s, Command=%s WHERE Equipement=%s", (int(state),int(state), Equipment))
    cnx.commit()
    close_green_db(cnx)

if __name__ == "__main__":
    all_state = get_equipment_state()
    all_command = get_equipment_command()
    print all_state
    print all_command
    while True:
        process_command_request()
        time.sleep(1)