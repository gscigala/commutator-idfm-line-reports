# Commutator-Idfm-Line-Reports

Commutator-Idfm-Line-Reports is an application that provides a DBus interface for accessing real-time information about public transportation lines in the Île-de-France region. It allows you to fetch and monitor the status of metro, RER, and Transilien lines, making it easy to integrate transportation data into other applications or services.

## Installation

	pip install .

## Usage

First, you have to register on [prim](https://prim.iledefrance-mobilites.fr) IDFM website to get your token.

To start the program, run:

	commutator-idfm-line-reports --token YOUR_TOKEN
	
You can also use the --session flag to use the DBus session bus instead of the system bus:

	commutator-idfm-line-reports --session --token YOUR_TOKEN
	
Additionally, you can specify the update interval in seconds using the --update-interval flag. The default interval is 300 seconds (5 minutes):

	commutator-idfm-line-reports --session --token YOUR_TOKEN --update-interval 60

## DBus Interface

### Properties

    id: The unique identifier of the line.
    name: The name of the line.
    color: The HTML color associated with the line.
    text_color: The HTML text color associated with the line.
    severity_effect: The effect of the current severity on the line.
    severity_color: The HTML color representing the current severity on the line.

### Possible Values

#### **Severity effect**

- **NO_PROBLEM**
- **OTHER_EFFECTS**
- **SIGNIFICANT_DELAYS**
- **NO_SERVICE**

## Systemd Service

The project includes a systemd service file to manage the service using systemd. The service file is located at systemd/commutator-idfm-line-reports.service. You need to replace %%TOKEN%% with your token.

## DBus Configuration

The project includes a DBus configuration file to set the necessary permissions for the DBus service. The configuration file is located at dbus/com.commutator.IdfmLineReports.conf.
