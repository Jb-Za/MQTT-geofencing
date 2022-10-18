import 'dart:async';

import 'package:flutter/material.dart';
import 'package:geolocator/geolocator.dart';
import 'package:mqtt_client/mqtt_client.dart';

import 'dart:async';
import 'dart:developer';

import 'package:mqtt_client/mqtt_server_client.dart';
import 'package:flutter/material.dart';

class MyHomePage extends StatefulWidget {
  const MyHomePage({Key? key, required this.title}) : super(key: key);

  final String title;

  @override
  _MyHomePageState createState() => _MyHomePageState();
}

class _MyHomePageState extends State<MyHomePage> {
  Position? _position;

  @override
  void initState() {
    super.initState();
    MqttService.initMqtt();
    Geolocator.getPositionStream(
      desiredAccuracy: LocationAccuracy.best,
      distanceFilter: 0,
      forceAndroidLocationManager: true,
      intervalDuration: Duration(
          milliseconds: 2000), // only retrieve the location every 2 seconds
    ).listen((position) {
      setState(() {
        _position = position;
        if (_position != null) {
          MqttService.publish("test/flutter_location",
              "$_position"); // publish the location to the broker
        }
      });
    });
  }

  @override
  Widget build(BuildContext context) {
    // some frontend stuff
    return Scaffold(
      appBar: AppBar(
        title: Text(widget.title),
      ),
      body: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: <Widget>[
            Text(
              'You are located at:',
            ),
            Text(
              '$_position',
            ),
          ],
        ),
      ),
    );
  }
}

// found and heavily modified code from the official packages documentation site https://pub.dev/packages/mqtt_client/example
class MqttService extends _MyHomePageState {
  MqttService._();
  static late MqttClient client;
  static StreamSubscription? mqttListen;

  static void initMqtt() async {
    client = MqttServerClient(
        'test.mosquitto.org', 'flutter_client') // the broker and client
      ..logging(on: false)
      ..port = 1883
      ..keepAlivePeriod = 20;

    final mqttMsg =
        MqttConnectMessage() // creates a message on connection to the broker
            .withWillMessage('connection-failed')
            .withWillTopic('willTopic')
            .startClean()
            .withWillQos(MqttQos.atLeastOnce)
            .withWillTopic('failed');
    client.connectionMessage = mqttMsg;
    await _connectMqtt();
  }

  static Future<void> _connectMqtt() async {
    //connects to the broker.
    if (client.connectionStatus!.state != MqttConnectionState.connected) {
      try {
        await client.connect();
      } catch (e) {
        log('Connection failed' + e.toString());
      }
    } else {
      log('MQTT Server already connected ');
    }
  }

  static Future<void> disconnectMqtt() async {
    //disconnects from the broker.
    if (client.connectionStatus!.state == MqttConnectionState.connected) {
      try {
        client.disconnect();
      } catch (e) {
        log('Disconnection Failed ' + e.toString());
      }
    } else {
      log('MQTT Server already disconnected ');
    }
  }

  //publishes the given message, reatain means the broker saves the last message.
  static void publish(String topic, String message, {bool retain = true}) {
    final builder =
        MqttClientPayloadBuilder(); // need to put the string through a payload builder
    builder.addString(message); //in order to send it thrhough to the broker.
    print(message);
    client.publishMessage(
      topic,
      MqttQos
          .atLeastOnce, //QOS 1 , the sender stores the message until it gets a PUBACK packet from the reciever.
      builder.payload!,
      retain: retain,
    );
    builder.clear();
  }

  static void onClose() {
    disconnectMqtt();
  }
}
