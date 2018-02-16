#!/usr/bin/env python
# -*- coding: utf-8 -*-

import time     # Library for the delay

import mysql.connector  # Library for database
from mysql.connector import errorcode

import serial   # Library for serial communication

try:
    serial = serial.Serial('/dev/cu.usbmodemFA131', 9600, timeout=0.5)
except:
    print "Exception in serial port"
    serial = None

time.sleep(4)   # we wait a little, so that the Arduino is ready.

def open_green_db():
    """ Function to open Database connection and database handle. """
    try:
        cnx = mysql.connector.connect(user='root',
                                      database='db_green_test')
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            print "Something is wrong with your user name or password"
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            print "Database does not exist"
        else:
            print err
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


def get_equipment_mode():
    """ Function to get Equipment Mode and return dictionary of
    Equipment and its active Mode.
    """
    cnx = open_green_db()
    if cnx is None:
        return None

    query = "SELECT Equipement, Mode from commandes"

    cursor = cnx.cursor()
    cursor.execute(query)
    equipment_mode = {Equipement: Mode for (Equipement, Mode) in cursor}

    close_green_db(cnx)
    return equipment_mode


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


def get_int_temp_threshhold():
    """ Function to get Internal Temperature Set Point and Delta values """
    cnx = open_green_db()
    if cnx is None:
        return None
    cursor = cnx.cursor()
    query = "SELECT SetPoint, DeltaT from types where Type = 'Temperature_int'"
    cursor.execute(query)

    setpoint, delta = None, None
    for SetPoint, DeltaT in cursor:
        setpoint = SetPoint
        delta = DeltaT

    return setpoint, delta


def get_luminosity_threshold():
    """ Function to get Luminosity Low and High Threshold values """
    cnx = open_green_db()
    if cnx is None:
        return None

    cursor = cnx.cursor()
    query = "SELECT LowThreshold, HighThreshold from types where Type = 'Luminosity'"
    cursor.execute(query)

    low, high = None, None
    for SetPoint, DeltaT in cursor:
        low = SetPoint
        high = DeltaT

    return low, high


def get_moisture_threshold():
    """ Function to get Moisture Low and High Threshold values """
    cnx = open_green_db()
    if cnx is None:
        return None

    cursor = cnx.cursor()
    query = "SELECT LowThreshold, HighThreshold from types where Type = 'Moisture'"
    cursor.execute(query)

    low, high = None, None
    for LowThreshold, HighThreshold in cursor:
        low = LowThreshold
        high = HighThreshold

    return low, high


def process_command_request():
    """ Process Command Request from website and update Active state accordingly """
    state = get_equipment_state()
    command_request = get_equipment_command()

    if serial is None:
        print "Error in accessing Serial port!"
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


def init_device_state():
    """ Function to  initiate Device state based on Configured from Database"""
    state = get_equipment_state()

    if serial is None:
        print "Error in accessing Serial port!"
        return

    if state is None:
        print "Error Getting State from Database"
        return

    if state.get("Lamp") == 0:
        send_command_arduino("LAMPOFF")
    else:
        send_command_arduino("LAMPON")

    if state.get("Valve") == 0:
        send_command_arduino("VALVEOFF")
    else:
        send_command_arduino("VALVEON")

    if state.get("Pump") == 0:
        send_command_arduino("PUMPOFF")
    else:
        send_command_arduino("PUMPON")

    if state.get("Fan") == 0:
        send_command_arduino("FANOFF")
    else:
        send_command_arduino("FANON")


def send_command_arduino(command):
    """ Function to Send command to Arduino device via Serial Port. """
    ACK = ""
    while True:
        try:
            serial.write(command)
            serial.flush()
            ACK = str(serial.readline())
            if not ACK == "OK":
                break
        except:
            print "send_command_arduino: Exception in serial port"


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
            serial.write(command)
            serial.flush()
            value = serial.readline()
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
                   (equipment_id, time.strftime('%y/%m/%d %H:%M:%S',
                                                time.localtime()), float(value)))
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


def process_valve_auto_mode(current_state):
    """ Function to process Vale auto mode based on Soil Moisture. """
    current_moisture = get_measure_arduino("MOIST")
    low_threshold, high_threshold = get_moisture_threshold()

    if low_threshold is None:
        print "Moisture low_threshold is NULL"
        return

    if high_threshold is None:
        print "Moisture high_threshold is NULL"
        return

    if current_state == 0:
        # In Case of Dry State, turn valve ON
        if low_threshold < current_moisture:
            send_command_arduino("VALVEON")
            print "VALVE ON"
            update_state_command("Valve", 1)

    if current_state == 1:
        # In Case of Wet State, turn Valve OFF
        if high_threshold >= current_moisture:
            send_command_arduino("VALVEOFF")
            print "VALVE OFF"
            update_state_command("Valve", 0)


def process_fan_auto_mode(current_state):
    """ Function to trigger Fan Auto Mode and turn on and off based on temperature."""
    current_temp_int = get_measure_arduino("TEMPINT")
    setpoint, delta = get_int_temp_threshhold()

    if setpoint is None:
        print "Temperature Setpoint is NULL"
        return

    if delta is None:
        print "Temperature Detla is NULL "
        return

    if current_state == 0:
        if setpoint > current_temp_int:
            send_command_arduino("FANON")
            print "Fan ON"
            update_state_command("Fan", 1)

    # If Fan state is already ON, check for temperature is already below delta
    if current_state == 1:
        if current_temp_int < (setpoint - delta):
            send_command_arduino("FANOFF")
            print "Fan OFF"
            update_state_command("Fan", 0)


def process_lamp_auto_mode(current_state):
    """ Function to process Lamp auto mode based on Luminosity Level. """
    current_luminosity = get_measure_arduino("LUMIN")
    low_threshold, high_threshold = get_luminosity_threshold()

    if low_threshold is None:
        print "Luminosity  Low Threshold is NULL"
        return

    if high_threshold is None:
        print "Luminosity  Low Threshold is NULL"
        return

    if current_state == 0:
        if current_luminosity < low_threshold:
            send_command_arduino("LAMPON")
            print "LAMP ON"
            update_state_command("Lamp", 1)

    if current_state == 1:
        if current_luminosity >= high_threshold:
            send_command_arduino("LAMPOFF")
            print "Lamp OFF"
            update_state_command("Lamp", 0)


def process_auto_mode():
    """ Function to process Auto Mode and triger states accordingly. """
    device_state = get_equipment_state()
    device_mode = get_equipment_mode()

    if device_mode.get("Fan") == 0:
        process_fan_auto_mode(device_state.get("Fan"))

    if device_mode.get("Lamp") == 0:
        process_lamp_auto_mode(device_state.get("Lamp"))

    if device_mode.get("Valve") == 0:
        process_valve_auto_mode(device_state.get("Valve"))


if __name__ == "__main__":
    all_state = get_equipment_state()
    all_command = get_equipment_command()

    print all_state
    print all_command
    init_device_state()

    while True:
        all_mode = get_equipment_mode()
        # Process command request only when any Equipment is manual mode
        if 1 in all_mode.values():
            process_command_request()

        process_auto_mode()
        process_measurement()

        time.sleep(1)
