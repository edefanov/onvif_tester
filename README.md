# onvif_tester

A tool for testing ONVIF compatible cameras on a method-by-method basis with .csv report previewing and outputting.

## Getting Started

### Prerequisites and dependencies

* Python 3
* [Flask](http://flask.pocoo.org/)
* [Python-onvif](https://github.com/quatanium/python-onvif)
* [Tablib](http://docs.python-tablib.org/en/master/)
* [WSDiscovery](https://pypi.org/project/WSDiscovery/)

### Installing

Acquire the dependencies and clone this repository to your working environment

In main_flask.py change the IP in the following line:

```
app.run(host='192.168.11.103')
```

To your server's IP

### Running the Tool

Start the application up by typing

```
python3 main_flask.py
```

Then navigate to your server's IP in your browser, the tool should automatically discover ONVIF-compliant devices in your network before displaying the page
To start a test just press "Start" button, the page should refresh automatically after the test is done
