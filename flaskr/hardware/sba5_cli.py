import click
import serial
import threading
import time

class SBAWrapper:
    def __init__(self, devname, baudrate, timeout):
        self.devname = devname
        self.baudrate = baudrate
        self.timeout = timeout
        self.serial_conn = serial.Serial(devname, baudrate, timeout=timeout)

    def send_command(self, command):
        try:
            self.serial_conn.write(command.encode('utf-8'))
            self.serial_conn.flush()
            time.sleep(0.5)  # time for device to answer
            response = self.serial_conn.readline().decode('utf-8').strip()
            return response
        except Exception as e:
            return f"Error: {str(e)}"

    def read_serial_loop(self, stop_event):
        try:
            while not stop_event.is_set():
                if self.serial_conn.in_waiting > 0:
                    message = self.serial_conn.readline().decode('utf-8').strip()
                    if message:
                        print(f"[Device]: {message}")
                time.sleep(0.1)
        except Exception as e:
            print(f"Error during serial read loop: {str(e)}")

@click.group(context_settings={"help_option_names": ["-h", "--help"]})
@click.option('--devname', default='/dev/serial/by-id/usb-FTDI_FT230X_Basic_UART_DN03WQZS-if00-port0', help='Device name or path')
@click.option('--baudrate', default=19200, help='Baud rate for serial communication')
@click.option('--timeout', default=1, help='Timeout for serial communication')
@click.pass_context
def cli(ctx, devname, baudrate, timeout):
    "CLI for SBA5 CO2 sensor"
    ctx.obj = SBAWrapper(devname, baudrate, timeout)

@cli.command()
@click.argument('command')
@click.option('-l', '--loop', is_flag=True, help="Continuously read responses for the command")
@click.pass_obj
def send(sba, command, loop):
    "Send a command to the device"
    command = command + '\r\n'  # Ensure correct termination
    if loop:
        stop_event = threading.Event()

        def handle_interrupt(signum, frame):
            stop_event.set()

        try:
            print(f"[Info]: Sending command: {command.strip()} and starting read loop. Press Ctrl+C to exit.")
            sba.send_command(command)  # Send the command
            thread = threading.Thread(target=sba.read_serial_loop, args=(stop_event,), daemon=True)
            thread.start()
            while not stop_event.is_set():
                time.sleep(0.1)
        except KeyboardInterrupt:
            print("\n[Info]: Exiting read loop.")
            stop_event.set()
        thread.join()
    else:
        result = sba.send_command(command)
        print(f"[Response]: {result}")

@cli.command()
@click.pass_obj
def listen(sba):
    "Enter continuous read mode"
    stop_event = threading.Event()

    def handle_interrupt(signum, frame):
        stop_event.set()

    try:
        print("[Info]: Starting serial read loop. Press Ctrl+C to exit.")
        thread = threading.Thread(target=sba.read_serial_loop, args=(stop_event,), daemon=True)
        thread.start()
        while not stop_event.is_set():
            time.sleep(0.1)
    except KeyboardInterrupt:
        print("\n[Info]: Exiting serial read loop.")
        stop_event.set()
    thread.join()

@cli.command()
def list_commands():
    "List available commands and their descriptions"
    commands_info = """
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
    and <linefeed>.

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

    For more info please see SBA5 operational manual in web.
    """
    print(commands_info)

if __name__ == '__main__':
    cli()
