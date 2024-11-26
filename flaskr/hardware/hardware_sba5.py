import serial

class SBAWrapper(object):
    """
    This class wraps all sba5 commands as a class methods or fields
    """
    def __init__(
            self,
            devname='/dev/serial/by-id/usb-FTDI_FT230X_Basic_UART_DN03WQZS-if00-port0',
            baudrate=19200,
            timeout= 1
    ):
        self.dev = devname
        self.baud = baudrate
        self.timeout = timeout

    def send_command(self, command):
        """
        Command must ends with \r\n !
        Its important
        :param command:
        :return:
        """
        """
        To initiate a command, the USB port or RS232 port sends an ASCII character or string.
        A single character command is acted on immediately when the character is received.
        A string command is acted on after the command string terminator <CR> is received. 
        The command can be sent with or without a checksum. If a checksum is sent, a “C” follows 
        the checksum value.
        For example,
        Device sends command without checksum: S,11,1<CR>
        Device sends command with checksum: S,11,1,043C<CR>
        On successfully receiving a command string, the SBA5+ sends an acknowledgement by 
        echoing back to all the ports the Command String and “OK”, each terminated with a <CR> 
        and<linefeed>.
        
        A<value>CR - Time [minutes] between zero operations
        B<value>CR - Averaging limit for CO2 running average.
        C<value>CR - Number of digits to the right of the decimal point for ccc.ccc. range:
        D<value>CR - 0-3 (integer) Determines if there is a zero operation at warmup
        E<char>CR - Zero operation duration (must be EL - large, EM - medium, ES - small)
        H<min>,<max>CR - Analog output H2OVOUT hardware scaling
        I<value>CR - Sets voltage or 4-20 mA output mode
        J<value>CR - Sets the mode of the spare I/O pin. See Spare I/O Line on page 18.
        L<value>CR - Low CO2 In [ppm] alarm.
        M - Display a measurement.
        O<min>,<max>CR - Analog output CO2VOUT hardware scaling
        P<value>CR - Turns on-board pump on or off (if installed)
        U<value>CR - Sets the user scale factor (for user calibrations)
        W<value>CR - Defines the measurement and zero ports on the solenoid valve.
        X - Saves the current configuration to non-volatile memory.
        Z - Perform a zero operation.
        ! - Turns measurement display off.
        @ - Turns measurement display on.
        ? - Display the SBA-5 configuration currently in use.
        ] - Restore the factory default configuration.





        
        """
        # \r\n
        try:
            ser = serial.Serial(
                port=self.dev,
                baudrate=self.baud,
                timeout=self.timeout
            )
            bcom = command.encode('utf-8')
            ser.write(bcom)
        except Exception as e:
            print("SBAWrapper error while send command: {}".format(e))
        # then try to read answer
        # it must be two messages, ended with \r\n
        try:
            ser = serial.Serial(
                port=self.dev,
                baudrate=self.baud,
                timeout=self.timeout
            )
            echo = (ser.readline()).decode('utf-8')
            status = (ser.readline()).decode('utf-8')
            return echo+status
        except Exception as e:
            print("SBAWrapper error while read answer from command: {}".format(e))
