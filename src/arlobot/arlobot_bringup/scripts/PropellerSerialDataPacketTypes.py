#!/usr/bin/env python

# ======================================
# Propeller Serial Data Packet Types
# ======================================
"""
These are the Packet Types that can be sent
to and from the Propeller Board.
"""


class PropellerSerialDataPacketTypes(object):
    def __init__(self):
        # WARNING: In SimpleIDE there is a box that says "32bit Double" FLOAT is 32 bit!
        # So what this means is there is no double, double === float
        # SO on the Python side use 'f' NOT 'd'!! Or you get a mismatch between pack and the struct,
        # because 'd' is 64 bits normally!

        # The idea is that we send an agreed upon packet format that both sides understand to always be the same.
        # This may get tricky if we want to have variable numbers of sensors, etc.
        # Either we have to make the code more flexible, or generate this packet format string at run time.

        # the <Lhhhb  is interpreted as follows
        #   see https://docs.python.org/2/library/struct.html
        #     <   little-endian
        #     L   unsigned long
        #     h   signed short
        #     H   unsigned short uint16_t
        #     B   unsigned char - same as Propeller uint8_t
        #     f   float - Note, don't use d, it doesn't work.

        # WARNING: In SimpleIDE there is a box that says "32bit Double" FLOAT is 32 bit!
        # So what this means is there is no double, double === float
        # SO on the Python side use 'f' NOT 'd'!! Or you get a mismatch between pack and the struct,
        # because 'd' is 64 bits normally!

        # the following lines of code can be used to explore the packed data
        # print goodDataPacket
        # for character in goodDataPacket:
        # print character.encode('hex')

        # Incoming data ideas:
        # 1. Use a character after the length (beginning of the packet, IN the checksumed and encoded data) to signify packet type/format to the other end.
        # 2. For the Odometry: bit to say how many pings, then next X bits are just 1 byte ping entries, then after "ping length count" IR count, then another list of bytes for the ir. An array in the struct on the Prop should hold them and they can be dropped into an array on Python when received.
        # NOTE: Ping/IR have always been consecutive on the Prop, although the prop skipped sending "empty" IRs, the data is still shorter in binary with the "empty" IRs being sent as 0 length bytes.

        # See Dropbox/Twoflower/BinaryVsTextData.ods for some byte comparison between binary and text formats of the data.

        # Data format options:

        #  Incoming: (form Propeller Board)
        #   e - Error: Error message
        #       This is also set by using 253, the "Special Byte" as the length,
        #       so the 'e' may be ignored, but if you don't fill this slot before the
        #       error text, the first letter of the error text becomes the "type" and
        #       is dropped from the message.
        #       NOTE: Error packets are just text data bounded by the "begin" and "end" markers,
        #       These are detected and output as text from the PropellerSerialInterface
        #       without any unpacking, so there is no code here for this data type.

        #   r - Ready: Propeller board is ready, but not initialized, replaces i
        #       The only parameter this has is a single
        #       uint8_t loopCount
        #       that counts up as it loops, and will of course cycle back to 0
        #       every so often, but it gives some indication of time passing,
        #       and some data to checksum to verify serial functioning.
        #       NOTE: We COULD set it up to just "ALWAYS RUN". Not sure what the drawbacks are.
        #         Initially this period was to let the HB-25's start up, which is not an issue anymore.
        #           This would run the QuickStartBoard 24x7, or could we kind of "detect" it?
        #           This would run the gyro 24x7.
        #         We would need sane default values, or some way to store the last values.
        #           Can we save variables to the Propeller EEPROM?
        self.CharacterReady = "r"
        self.FormatReady = "<BBBBBBB"  # Ready Packet Format

        class ReadyDataPacket:
            def __init__(self, loopCount=0):
                self.loopCount = loopCount  # uint8_t 1 byte

        self.ReadyDataPacket = ReadyDataPacket  # 1 byte Total + checksum

        #   o - Odometry: This includes odometry and ping/ir sensor data
        #       NOTE: We will need to account for varying number of sensors per robot somehow.
        #       NOTE: We also had an 's' option, but I want to combine that with the odometry
        #       NOTE: We also had a 'b' option for buttons, but I also want to combine that.
        self.CharacterOdom = "o"
        self.FormatOdomBase = "<ffffffffBBBBBBBB"
        self.FormatOdom = self.FormatOdomBase

        #   c - Config: This returns the setting settings data from the Propeller Board
        #       This is how we know if the Propeller Board has the correct settings.
        #       If these do not not match what ROS intends, then ROS sends the settings
        #       to the Propeller Board until they match.
        self.CharacterConfig = "c"
        self.FormatConfig = "<ffBBBBB"

        #   t - Test: Test message
        #       This is the only message type that is sent BOTH ways.
        #       These will ONLY come in response to a 't' from here,
        #       and will mostly mirror the data sent
        self.CharacterTest = "t"
        self.FormatTest = "<LhhhBcf"  # Test Packet Format

        class TestDataPacket:
            def __init__(
                self,
                testUnsignedLog=0,
                testIntOne=0,
                testIntTwo=0,
                testIntThree=0,
                testByte=0,
                testCharacter="a",
                testFloat=1.1,
            ):
                self.testUnsignedLog = testUnsignedLog  # uint32_t 4 bytes
                self.testIntOne = testIntOne  # int16_t 2 bytes
                self.testIntTwo = testIntTwo  # int16_t 2 bytes
                self.testIntThree = testIntThree  # int16_t 2 bytes
                self.testByte = testByte  # uint8_t 1 byte
                self.testCharacter = testCharacter  # uint8_t 1 byte
                self.testFloat = testFloat  # float 4 bytes

        self.TestDataPacket = TestDataPacket  # 16 bytes Total + checksum

        #  Outgoing: (to Propeller Board)
        #   t - Test: Test message intended to elicit a pre-formatted response
        #       This is the only message type that is sent BOTH ways.
        #   i - Initialize: Data sent to Propeller in "Ready" state to tell it how to start up
        #       NOTE: This was 'd' before Robot Initialized. I'd rather make then clearly distinct.
        #       NOTE: We could send all init data in every speed (twist) update if that doesn't slow things down.
        self.CharacterInit = "i"
        self.FormatInit = "<fff"  # Init Packet Format

        class InitDataPacket:
            def __init__(self, X=0.0, Y=0.0, Heading=0.0):
                self.X = X
                self.Y = Y
                self.Heading = Heading

        self.InitDataPacket = InitDataPacket  # 1 byte Total + checksum

        #   s - Settings: Set options for the robot:
        #         trackWidth
        #         distancePerCount
        #         ignoreProximity
        #         ignoreCliffSensors
        #         ignoreIRSensors
        #         ignoreFloorSensors
        #         pluggedIn
        #       NOTE: This was 'd' after Robot Initialized. I'd rather keep them distinct,
        #             and just start fresh to avoid confusion.
        self.CharacterSettings = "s"
        self.FormatSettings = "<ffBBBBB"  # Settings Packet Format

        class SettingsDataPacket:
            def __init__(
                self,
                trackWidth=0.0,
                distancePerCount=0.0,
                ignoreProximity=0,
                ignoreCliffSensors=0,
                ignoreIRSensors=0,
                ignoreFloorSensors=0,
                pluggedIn=1,
            ):
                self.trackWidth = trackWidth
                self.distancePerCount = distancePerCount
                self.ignoreProximity = ignoreProximity
                self.ignoreCliffSensors = ignoreCliffSensors
                self.ignoreIRSensors = ignoreIRSensors
                self.ignoreFloorSensors = ignoreFloorSensors
                self.pluggedIn = pluggedIn

        self.SettingsDataPacket = SettingsDataPacket

        #   m - Move messages: This is the requests to move, taken from Twist messages
        #         CommandedVelocity
        #         CommandedAngularVelocity
        #       NOTE: This used to be 's' for Speed
        #       NOTE: These are expected to come in continually. If they stop, the robot
        #             should come to a stop, given enough timeout to account for normal
        #             delays between updates.
        self.CharacterMove = "m"
        self.FormatMove = "<ff"  # Move Packet Format

        class MoveDataPacket:
            def __init__(self, CommandedVelocity=0.0, CommandedAngularVelocity=0.0):
                self.CommandedVelocity = CommandedVelocity
                self.CommandedAngularVelocity = CommandedAngularVelocity

        self.MoveDataPacket = MoveDataPacket  # 1 byte Total + checksum

        #   l - LED Control: Used to turn various button LEDs on/off
        #         ledNumber
        #         ledState
        self.CharacterLED = "l"
        self.FormatLED = "<BB"  # LED Packet Format

        class LEDDataPacket:
            def __init__(self, ledNumber=0, ledState=0):
                self.ledNumber = ledNumber
                self.ledState = ledState

        self.LEDDataPacket = LEDDataPacket

        #   p - Position: Update the X, Y position and Heading
        #         X
        #         Y
        #         Heading
        #       NOTE: This is not a "normal" action. The robot creates and tracks its own odometry,
        #             and reports it, not reads it. The ROS program tracks a "difference" between
        #             the reported odometry and the position on the map.
        #             But if you know the robot's position better than it does, for instance,
        #             when loading a new map, or a board reset while AMCL is running, then
        #             we may want to tell the robot where to start after init is already done.
        self.CharacterPositionUpdate = "p"
        self.FormatPositionUpdate = "<fff"  # PositionUpdate Packet Format

        class PositionUpdateDataPacket:
            def __init__(self, X=0.0, Y=0.0, Heading=0.0):
                self.X = X
                self.Y = Y
                self.Heading = Heading

        self.PositionUpdateDataPacket = PositionUpdateDataPacket

        #   a - ABD Parameter Override
        #         abd_speedLimit
        #         abdR_speedLimit
        #       NOTE: This is not a "normal" action. These two variables set the
        #             maximum forward and reverse speed in Ticks Per Second (TPS).
        #             The code on the Propeller Board initially pegs these to the
        #             MAXIMUM_SPEED. Then the code adjusts these down and back up
        #             in real time based on input from the sensors. When all sensors
        #             indicate the way is clear, the variables are set back to equal
        #             MAXIMUM_SPEED. So setting these by hand is not only unusual,
        #             but you are literally fighting with the code on the Propeller
        #             board.
        self.CharacterAbdParameterOverride = "a"
        self.FormatAbdParameterOverride = "<BB"  # AbdParameterOverride Packet Format

        class AbdParameterOverrideDataPacket:
            def __init__(self, abd_speedLimit=0, abdR_speedLimit=0):
                self.abd_speedLimit = abd_speedLimit
                self.abdR_speedLimit = abdR_speedLimit

        self.AbdParameterOverrideDataPacket = AbdParameterOverrideDataPacket

    def setFormatOdom(self, sensorDataCount):
        count = 0
        sensorDataBits = ""
        while count < sensorDataCount:
            sensorDataBits = sensorDataBits + "B"
            count += 1
        self.FormatOdom = self.FormatOdomBase + sensorDataBits
