import time
from random import randint


class FakeRelayDriver:
    def __init__(self, name, initial_state=False):
        """
        Initializes the relay driver.

        Args:
            initial_state (bool, optional): The initial state of the relay. False for closed, True for open. Defaults to False.
        """
        time.sleep(0.5)
        if randint(0, 5) == 1:
            raise ValueError("some error")
        self.name = name
        self.state = initial_state  # Relay state: False = closed, True = open


    def open(self):
        """
        Opens the relay.
        """
        time.sleep(0.5)
        if randint(0, 5) == 2:
            raise ValueError("some error")
        self.state = True
        # Simulate opening the relay

    def close(self):
        """
        Closes the relay.
        """
        time.sleep(0.5)
        if randint(0, 5) == 3:
            raise ValueError("some error")
        self.state = False
        # Simulate closing the relay

    def check_state(self):
        """
        Checks the current state of the relay.

        Returns:
            bool: The current state of the relay. True for open, False for closed.
        """
        time.sleep(0.5)
        if randint(0, 5) == 4:
            raise ValueError("some error")
        # Simulate checking the relay's current state
        return self.state


if __name__ == "__main__":
    # Example usage
    relay_driver = FakeRelayDriver("gao")
    print(f"Initial relay state: {'open' if relay_driver.check_state() else 'closed'}")

    relay_driver.open()
    print(f"Relay state after opening: {'open' if relay_driver.check_state() else 'closed'}")

    relay_driver.close()
    print(f"Relay state after closing: {'open' if relay_driver.check_state() else 'closed'}")
