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
    """ Function to open Database connection and database handle. """
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


def close_green_db(cnx):
    """ Function to Close Database connection """
    if cnx is not None:
        cnx.close


def get_equipment_state():
    """ Function to get Equipment State and return dictionary of
    Equipment and its active state.
    """
    cnx = open_green_db()
    if cnx is None:
        return None

    query = "SELECT Equipement, State from commandes"

    cursor = cnx.cursor()
    cursor.execute(query)
    equipment_state = {Equipement: State for (Equipement, State) in cursor}

    close_green_db(cnx)
    return equipment_state


def get_equipment_command():
    """ Function to get Equipment Command Request from web and return dictionary of
    Equipment and its active command request.
    """
    cnx = open_green_db()
    if cnx is None:
        return None

    query = "SELECT Equipement, Command from commandes"

    cursor = cnx.cursor()
    cursor.execute(query)
    equipment_command = {Equipement: Command for (Equipement, Command) in cursor}

    close_green_db(cnx)
    return equipment_command


def get_device_id():
    """ Function to get Equipment State and return dictionary of
    Equipment and its active state.
    """
    cnx = open_green_db()
    if cnx is None:
        return None

    query = "SELECT Type, IdType from types"

    cursor = cnx.cursor()
    cursor.execute(query)
    device_id = {Type: IdType for (Type, IdType) in cursor}

    close_green_db(cnx)
    return device_id

def process_command_request():
    """ Process Command Request from website and update Active state accordingly """
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
            send_command_arduino("LAMPOFF")
            print "Lamp OFF"
            update_state_command("Lamp", 0)

        if command_request.get('Lamp') == 1:
            send_command_arduino("LAMPON")
            print "Lamp ON"
            update_state_command("Lamp", 1)

    if state.get('Valve') != command_request.get('Valve'):
        print "Valve Request"
        if command_request.get('Valve') == 0:
            send_command_arduino("VALVEOFF")
            print "Valve OFF"
            update_state_command("Valve", 0)

        if command_request.get('Valve') == 1:
            send_command_arduino("VALVEON")
            print "Valve ON"
            update_state_command("Valve", 1)

    if state.get('Fan') != command_request.get('Fan'):
        print "Fan Request"
        if command_request.get('Fan') == 0:
            send_command_arduino("FANOFF")
            print "Fan OFF"
            update_state_command("Fan", 0)

        if command_request.get('Fan') == 1:
            send_command_arduino("FANON")
            print "Fan ON"
            update_state_command("Fan", 1)

    if state.get('Pump') != command_request.get('Pump'):
        print "Pump Request"
        if command_request.get('Pump') == 0:
            send_command_arduino("PUMPOFF")
            print "Pump OFF"
            update_state_command("Pump", 0)

        if command_request.get('Pump') == 1:
            send_command_arduino("PUMPON")
            print "Pump ON"
            update_state_command("Pump", 1)


def send_command_arduino(command):
    """ Function to Send command to Arduino device via Serial Port. """
    ACK = ""
    while True:
        try:
            ser.write(command)
            ser.flush()
            ACK = str(ser.readline())
            if not ACK == "OK":
                break
        except:
            print("send_command_arduino: Exception in serial port")


def update_state_command(equipment, state):
    """ Update Active state to Database. """
    cnx = open_green_db()
    if cnx is None:
        return None

    cursor = cnx.cursor()
    cursor.execute("UPDATE commandes SET State=%s WHERE Equipement=%s",
                   (int(state), equipment))
    cnx.commit()
    close_green_db(cnx)


def get_measure_arduino(command):
    """ Function to get Measurement from Arduino """

    while True:
        try:
            ser.write(command)
            ser.flush()
            value = ser.readline()
            if not value == "":
                break
        except:
            print "Error accessing serial port"
            return None

    return value


def update_measure_db(equipment_id, value):
    """ Function to update Measurement to DB """
    cnx = open_green_db()
    if cnx is None:
        return None

    cursor = cnx.cursor()
    cursor.execute("INSERT INTO mesures(IdType, Date, Value) VALUES(%s,%s,%s)",
                   (equipment_id, time.strftime('%y/%m/%d %H:%M:%S', time.localtime()), float(value)))
    cnx.commit()
    close_green_db(cnx)


def process_measurement():
    """ Function to Process Measurement for each device """
    device_id = get_device_id()
    temp_int = get_measure_arduino("TEMPINT")
    if temp_int is not None:
        update_measure_db(device_id.get("Temperature_int"), temp_int)

    temp_ext = get_measure_arduino("TEMPEXT")
    if temp_ext is not None:
        update_measure_db(device_id.get("Temperature_ext"), temp_ext)

    humidity = get_measure_arduino("HUMID")
    if humidity is not None:
        update_measure_db(device_id.get("Humidity"), humidity)

    luminosity = get_measure_arduino("LUMIN")
    if luminosity is not None:
        update_measure_db(device_id.get("Luminosity"), luminosity)

    moisture = get_measure_arduino("MOIST")
    if moisture is not None:
        update_measure_db(device_id.get("Moisture"), moisture)


if __name__ == "__main__":
    all_state = get_equipment_state()
    all_command = get_equipment_command()
    print all_state
    print all_command
    while True:
        process_command_request()
        process_measurement()
        time.sleep(1)