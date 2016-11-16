################################################################################
# srf01
#
# Created: 2016-11-08 14:46:49.825158
# By: Andrea Bau'
################################################################################


"""
.. module:: srf01

****************
srf01 Library
****************

This module contains class definitions and methods to access most of the functionality of srf01 Ultrasonic range finder.
Sensor's charactheristics and detailed descriptions can be found at https://www.robot-electronics.co.uk/htm/srf01tech.htm.

These sensors use one pin serial interfaces, this library however rely on Zerynth's *streams* class and both pin of a serial peripheral are needed.
Depending on the board that is used is necessary to put a resistor (1-5 kOhm) between Tx and Rx board's pins and then connect the sensor's serial port to Rx pin.

With a single serial peripheral it is possible to control up to 16 SRF01's.

Example::

    import streams
    from community.anba.srf01 import srf01

    streams.serial()
    my_sensors = srf01.Srf(D0,SERIAL1)

    print("cheking versions...")
    sft01 = my_sensors.get_software_version(1) # retrieve software version of sensor with address 1
    sft04 = my_sensors.get_software_version(4) # retrieve software version of sensor with address 4
    if sft01!=2 or sft04!=2:
        print("wrong sensor's software version")
    else:
        print("done")
        while True:
            my_sensors.do_range() # all connected sensor starts the ranging routine at the same time, the returned distance will be in cm
            sleep(70)
            rng01 = my_sensors.get_last_range(1)
            rng04 = my_sensors.get_last_range(4)
            print("-----------------")
            print("sensor 1: %03d cm"%rng01)
            print("sensor 4: %03d cm"%rng04)
            sleep(1000)

"""

import streams

RANGE_IN = 0x50            #0-addressable
RANGE_CM = 0x51            #0-addressable

RANGE_IN_R = 0x53          #return 2 bytes after ~70ms
RANGE_CM_R = 0x54          #return 2 bytes after ~70ms

FAKE_RANGE_IN = 0x56       #0-addressable
FAKE_RANGE_CM = 0x57       #0-addressable

FAKE_RANGE_IN_R = 0x59     #return 2 bytes after ~70ms
FAKE_RANGE_CM_R = 0x5A     #return 2 bytes after ~70ms

BURST = 0x5C               #0-addressable
SOFTWARE_VERSION = 0x5D    #return 1 byte
RANGE = 0x5E               #return 2 bytes
STATUS = 0x5F              #return 1 byte
SLEEP = 0x60               #0-addressable
UNLOCK = 0x61              #0-addressable
SET_ADV_MODE = 0x62        #0-addressable
CLR_ADV_MODE = 0x63        #0-addressable

BAUD19200 = 0x64           #0-addressable
BAUD38400 = 0x65           #0-addressable

WAKEUP = 0xFF              #0-addressable

CHANGE01 = 0XA0
CHANGE02 = 0XAA
CHANGE03 = 0XA5

READ_ATTEMPT = 10

new_exception(InvalidAddress,ValueError,"Invalid address value! Use an integer between 1 and 16")
new_exception(InvalidUnit,ValueError,"Invalid range unit! Use \"cm\" or \"in\"")
new_exception(InvalidAddress0,ValueError,"Invalid address! Use an integer between 1 and 16 or 0")

streams.serial()

class Srf():
    """

    ==================
    Srf Class
    ==================

    .. class:: Srf(pin,driver)

        Creates a Srf instance through which is possible to interact with srf01 sensors.
        Communications with sensors is via *driver* serial port, where *pin* is the Tx pin.
    """
    def __init__(self,pin,driver):
        self.pin = pin
        self.driver = driver

    def change_address(self,current_addr,new_addr):
        """
        .. method:: change_address(current_addr,new_addr)

            With this method it is possible to change the sensor address. Only one sensor have to be
            connected to the serial in order to use this method. Valid address values are integeres 
            from ``1`` to ``16`` included, otherwise :exc:`InvalidAddress` exception is raised.
            ::

                import streams
                from community.anba.srf01 import srf01

                streams.serial()
                my_sensors = srf01.Srf(D0,SERIAL1)
                try:
                    my_sensors.change_address(1,5)
                except Exception as e:
                    print(e)

        """
        if not _is_valid_addr(current_addr) or not _is_valid_addr(new_addr):
            raise InvalidAddress

        self._writeNread(current_addr,CHANGE01)
        self._writeNread(current_addr,CHANGE02)
        self._writeNread(current_addr,CHANGE03)
        self._writeNread(current_addr,new_addr)

    def get_software_version(self,addr):
        """
        .. method:: get_software_version(addr)

            Return a small integer representing the software version loaded in the sensor with address
            *addr*. If serial communication fails ``-1`` is returned. If *addr* is not an integer between ``1`` and
            ``16`` included, :exc:`InvalidAddress` exception is raised.
            ::

                import streams
                from community.anba.srf01 import srf01

                streams.serial()
                my_sensors = srf01.Srf(D0,SERIAL1)
                print("Checking software version...",end="")
                for i in range(10):
                    print(".",end="")
                    sft13 = my_sensors.get_software_version(13)
                    if sft13 != -1:
                        print(" done!")
                        print(Sensor 13's software version: ",sft13)
                        break
                if sft13 == -1:
                    print(" ooops, failed :( ")

        """
        if not _is_valid_addr(addr):
            raise InvalidAddress
        sftVer = self._writeNread(addr,SOFTWARE_VERSION,nbit=1)
        return sftVer[0]

    def get_status(self,addr):
        """
        .. method:: get_status(addr)

            Return a small integer representing the status (see sensor's technical documentation for details about status value) of the sensor with address
            *addr*. If serial communication fails return ``-1``. If *addr* is not an integer between ``1`` and
            ``16`` included, :exc:`InvalidAddress` exception is raised. If the sensor is in advanced mode and it is locked, it can measure range all the way
            down to zero. Otherwise if the sensor is not locked or it is in standard mode the minimi range the SRF01 sensor ca detect is around 18 cm or 7 inches.
            ::

                import streams
                from community.anba.srf01 import srf01

                streams.serial()
                my_sensors = srf01.Srf(D0,SERIAL1)
                print("Checking sensor's status...",end="")
                for i in range(10):
                    print(".",end="")
                    sft08 = my_sensors.get_status(8)
                    if sft08 != -1:
                        print(" done!")
                        break
                if sft08 == -1:
                    print(" ooops, failed :( ")
                else:
                    if sft08 == 0:
                        print("Standard mode, unlocked")
                    elif sft08 == 1:
                        print("Standard mode, locked")
                    elif sft08 == 2:
                        print("Advanced mode, unlocked")
                    else: #stf08 == 3
                        print("Advanced mode, locked")

        """

        if not _is_valid_addr(addr):
            raise InvalidAddress
        status = self._writeNread(addr,STATUS,nbit=1)
        return status[0]

    def get_last_range(self,addr):
        """
        .. method:: get_last_range(addr)

            Return a small integer representing last range done by the sensor with address *addr*.
            The unit of measure (cm or in) of the returned value depends on the last range command received by that sensor.
            If serial communication fails this method return ``-1``. If *addr* is not an integer between ``1`` and
            ``16`` included, :exc:`InvalidAddress` exception is raised.
            ::

                import streams
                importfrom community.anba.srf01 import srf01

                streams.serial()

                my_sensors = srf01.Srf(D0,SERIAL1)

                my_sensors.do_range(3)
                my_sensors.do_range(7,"in")

                sleep(70)

                rng03 = my_sensors.get_last_range(3)
                rng07 = my_sensors.get_last_range(7)

                print("Sensor 3: %03d cm"%rng03)
                print("Sensor 7: %03d in"%rng07)

        """
        if not _is_valid_addr(addr):
            raise InvalidAddress
        resp = self._writeNread(addr,RANGE,nbit=2)
        if len(resp)==2:
            rangeInt = 256*resp[0]+resp[1]
            return rangeInt
        else:
            return resp[0]

    def do_range(self,addr=0,unit="cm"):
        """
        .. method:: do_range(addr=0,unit="cm")

            This method initiate a ranging on srf01 sensor. Using ``get_last_range()`` method after ~70 ms it 
            is possible to get the result of the ranging. If *addr* is equal to ``0`` (default value) all
            connected sensors will start the ranging at the same time, otherwise only the sensor with address
            equal to *addr* will. If *addr* is not any of these value :exc:`InvalidAddress0` exception is raised.
            *unit* define the measure unit of the result (retrievable with ``get_last_range()``), it can be ``"cm"``
            or ``"in"`` otherwise :exc:`InvalidUnit` exception is raised.


        """
        if addr !=0 and not _is_valid_addr(addr):
            raise InvalidAddress0
        if unit not in ["cm","in"]:
            raise InvalidUnit
        elif unit == "in":
            cmd = RANGE_IN
        else:
            cmd = RANGE_CM
        self._writeNread(addr,cmd)

    def burst(self,addr=0):
        """
        .. method:: burst(addr=0)

            Transmit a burst without doing the ranging. If *addr* is equal to ``0`` (default value) all 
            connected sensors will send the burst at the same time, otherwise only the sensor with address
            equal to *addr* will. If *addr* is not any of these value :exc:`InvalidAddress0` exception is raised.

        """
        if addr!=0 and not _is_valid_addr(addr):
            raise InvalidAddress0
        self._writeNread(addr,BURST)

    def do_fake_range(self,addr=0,unit="cm"):
        """
        .. method:: do_fake_range(addr=0,unit="cm")

            Same as ``do_range()`` except that the sensor do not send the 8-cycle ultrasonic burst out.
            This method is used where the burst has been transmitted by another sonar.

        """
        if addr !=0 and not _is_valid_addr(addr):
            raise InvalidAddress0
        if unit not in ["cm","in"]:
            raise InvalidUnit
        elif unit == "in":
            cmd = FAKE_RANGE_IN
        else:
            cmd = FAKE_RANGE_CM
        self._writeNread(addr,cmd)

    def get_range(self,addr,unit="cm"):
        """
        .. method:: get_range(addr,unit="cm")

            Same as ``do_range()`` but this method block the thread (for ~70 ms) until the measured range is returned or ``-1`` if serial communication fails.
            Unlike ``do_range()`` here *addr* can not be ``0`` (to avoid multiple sensors to write on the communication bus at the same time), if *addr* is not an integer between ``1`` and
            ``16`` included, :exc:`InvalidAddress` exception is raised.
            ::

                import streams
                from community.anba.srf01 import srf01

                streams.serial()

                my_sensors = srf01.Srf(D0,SERIAL1)

                while True:
                    rng04 = my_sensors.get_range(3)
                    rng09 = my_sensors.get_range(9,"in")

                    print("------------")
                    print("Sensor 4: %03d cm"%rng04)
                    print("Sensor 9: %03d in"%rng09)

                    sleep(2000)

        """
        if not _is_valid_addr(addr):
            raise InvalidAddress
        if unit not in ["cm","in"]:
            raise InvalidUnit
        elif unit == "in":
            cmd = RANGE_IN_R
        else:
            cmd = RANGE_CM_R

        resp = self._writeNread(addr,cmd,nbit=2,delay=65)
        if len(resp)==2:
            rangeInt = 256*resp[0]+resp[1]
            return rangeInt
        else:
            return resp[0]

    def get_fake_range(self,addr,unit="cm"):
        """
        .. method:: get_fake_range(addr,unit="cm")

            Same as ``get_range()`` except that the sensor do not send the 8-cycle ultrasonic burst out.
            This method is used where the burst has been transmitted by another sonar.

        """
        if not _is_valid_addr(addr):
            raise InvalidAddress
        if unit not in ["cm","in"]:
            raise InvalidUnit
        elif unit == "in":
            cmd = FAKE_RANGE_IN_R
        else:
            cmd = FAKE_RANGE_CM_R

        resp = self._writeNread(addr,cmd,nbit=2,delay=65)
        if len(resp)==2:
            rangeInt = 256*resp[0]+resp[1]
            return rangeInt
        else:
            return resp[0]

    def set_advanced_mode(self,addr=0):
        """
        .. method:: set_advanced_mode(addr=0)

            This method set the sensor on advanced mode, if *addr* is equal to ``0`` all 
            connected sensors will be set.

        """
        if addr !=0 and not _is_valid_addr(addr):
            raise InvalidAddress0
        self._writeNread(addr,SET_ADV_MODE)

    def clear_advanced_mode(self,addr=0):
        """
        .. method:: clear_advanced_mode(addr=0)

            This method set the sensor on standard mode, if *addr* is equal to ``0`` all 
            connected sensors will be set.

        """
        if addr !=0 and not _is_valid_addr(addr):
            raise InvalidAddress0
        self._writeNread(addr,CLR_ADV_MODE)

    def _unlock(self,addr=0):
        if addr !=0 and not _is_valid_addr(addr):
            raise InvalidAddress0
        self._writeNread(addr,UNLOCK)

    def _writeNread(self,addr,cmd,baud_rate=9600,nbit=0,delay=0):
        digitalWrite(self.pin,LOW)
        pinMode(self.pin,OUTPUT)
        sleep(4)
        channel = streams.serial(self.driver,baud_rate,set_default=False)
        channel.write(chr(addr))
        channel.write(chr(cmd))
        thr = []
        for i in range(READ_ATTEMPT):
            if channel.available() >= 2:
                thr = channel.read(2)
                break
            else:
                sleep(1)

        if len(thr)!=2:
            return [-1]
        resp = []
        if nbit!=0:
            if delay!=0:
                sleep(delay)
            resp = []
            for i in range(READ_ATTEMPT):
                if channel.available() >=nbit:
                    resp = channel.read(nbit)
                    break
                else:
                    sleep(1)
            if len(resp)!=nbit:
                resp = [-1]
        channel.close()
        digitalWrite(self.pin,LOW)
        pinMode(self.pin,OUTPUT)
        return resp


def _is_valid_addr(addr):
    if addr>=1 and addr<=16:
        return True
    else:
        return False


