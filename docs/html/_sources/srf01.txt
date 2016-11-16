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
==================
Srf Class
==================

.. class:: Srf(pin,driver)

    Creates a Srf instance through which is possible to interact with srf01 sensors.
    Communications with sensors is via *driver* serial port, where *pin* is the Tx pin.
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
.. method:: do_range(addr=0,unit="cm")

    This method initiate a ranging on srf01 sensor. Using ``get_last_range()`` method after ~70 ms it 
    is possible to get the result of the ranging. If *addr* is equal to ``0`` (default value) all
    connected sensors will start the ranging at the same time, otherwise only the sensor with address
    equal to *addr* will. If *addr* is not any of these value :exc:`InvalidAddress0` exception is raised.
    *unit* define the measure unit of the result (retrievable with ``get_last_range()``), it can be ``"cm"``
    or ``"in"`` otherwise :exc:`InvalidUnit` exception is raised.
.. method:: burst(addr=0)

    Transmit a burst without doing the ranging. If *addr* is equal to ``0`` (default value) all 
    connected sensors will send the burst at the same time, otherwise only the sensor with address
    equal to *addr* will. If *addr* is not any of these value :exc:`InvalidAddress0` exception is raised.
.. method:: do_fake_range(addr=0,unit="cm")

    Same as ``do_range()`` except that the sensor do not send the 8-cycle ultrasonic burst out.
    This method is used where the burst has been transmitted by another sonar.
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
.. method:: get_fake_range(addr,unit="cm")

    Same as ``get_range()`` except that the sensor do not send the 8-cycle ultrasonic burst out.
    This method is used where the burst has been transmitted by another sonar.
.. method:: set_advanced_mode(addr=0)

    This method set the sensor on advanced mode, if *addr* is equal to ``0`` all 
    connected sensors will be set.
.. method:: clear_advanced_mode(addr=0)

    This method set the sensor on standard mode, if *addr* is equal to ``0`` all 
    connected sensors will be set.
