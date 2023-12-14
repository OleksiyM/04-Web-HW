# Web Application with HTTP and Socket Servers

This project implements a simple web application that uses both HTTP and socket servers to receive and store messages.

## Overview

The `main.py` file contains Python code that:

- Sets up directories and files for data storage
- Starts an HTTP server on port 3000 to serve web pages
- Starts a UDP socket server on port 5000 to receive messages
- Defines request handlers for the HTTP server
- Saves received data to a JSON file

## HTTP Server

The HTTP server is implemented using the `BaseHTTPRequestHandler` from the `http.server` module. It handles GET requests to serve index and message HTML pages stored locally.

## Socket Server

A UDP socket server is started on a separate port to receive messages sent from a client. Any data received is saved to the JSON storage file.

## Data Storage

A storage directory is created if needed, and a JSON file is used to store received messages, with timestamps, in a dictionary format.

## Threading

The HTTP and socket servers are started in separate threads to allow concurrent operation.

## Error Handling

Exceptions are caught and logged to help debug any issues receiving or storing data.
