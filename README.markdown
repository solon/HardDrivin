# Overview

The system consists of several components that communicate using OpenSoundControl.

The Car Control service receives OpenSoundControl messages and sends serial commands to the Arduino board that move the servo motors.

The Pure Data interface allows manual control of the cars and sends OpenSoundControl messages to the Car Control service.

The Twitter service allows automatic control of the cars in response to tweets.

The Processing sketch provides a way to display the tweets that are controlling the cars.

# Installing

## Requirements

Install [Arduino](https://www.arduino.cc/en/Main/Software), [Pure Data](https://puredata.info/downloads/pd-extended), and [Processing](https://processing.org/download/?processing)

You also need Python 2.x which is installed by default on Mac OS X and Linux. Windows users may need to download and install [Python 2.x](https://www.python.org/downloads/release/python-2711/).

The included code was written for [Arduino 0022](https://www.arduino.cc/en/Main/OldSoftwareReleases#00xx), [Pure Data 0.41](https://puredata.info/downloads/pure-data/releases/0.41.4) and Processing 0187.

If you have trouble getting the code running with newer versions of these languages, try the old versions.

Older versions of Processing than 1.5.1 can only be built from source, so try 1.5.1 first.

The Twitter service was written for an older version of the Twitter API and will most likely need to be updated to use the current API.

## Servo Firmware (Arduino)

Open `Arduino/HardDrivin.pde` in the Arduino IDE and upload the sketch to your Arduino board.

## Twitter Service & Car Control (Python)

### Install Python dependencies

    $ easy_install tweepy, pyosc, pyyaml, pyserial, simplejson

## Configure Twitter credentials

Rename `settings.example.yaml` to `settings.yaml` replace `ACCESS_KEY`, `ACCESS_SECRET`, `CONSUMER_KEY`, `CONSUMER_SECRET` with the actual credentials.

# Running

The Twitter service and Car Control service are Python applications that run as command line processes.
Start each one in a separate Terminal window.

## Start Car Control

    $ python CarControl.py

## Start Twitter Service

    $ python TwitterService.py

## Launch User Interface (Pure Data)

Open the `PureData\HardDrivin.pd` patch in Pure Data. This interface is useful for manually controlling the cars.

## Tweet Display (Processing)

This Processing sketch displays the tweets that control the cars.
