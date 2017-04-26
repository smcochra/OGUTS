'''
Created on Apr 14, 2017

@author: scochra
'''

import paho.mqtt.client as mqtt
import time


NUM_UUT = 40
NUM_THREAD_PER_UUT = 3
NUM_UI_VIEWERS = 5
NUM_TESTS_PER_UI = 10  # should be less than NUM_UUT

SEND_DELAY = 0.2
QOS = 2

# BROKER_ADD = 'iot.eclipse.org'
BROKER_ADD = '10.130.41.48'
BROKER_PORT = 1883


def on_connect(client, userdata, rc):
    print("%s connected with result code %s" % (userdata['name'], str(rc)))
    # client.subscribe('hello/world/%s' % userdata['name'])


# The callback for when a PUBLISH message is received from the server.
def on_message_uut(client, userdata, msg):
    print('[%s] [Thread: %s] %s' % (userdata['name'], msg.topic, msg.payload))


def on_message_ui(client, userdata, msg):
    diff = time.time() - float(msg.payload)
    if userdata['num'] == NUM_UI_VIEWERS:
        print('[%s] [Thread: %s] Diff: %ss' % (userdata['name'], msg.topic, diff))


if __name__ == '__main__':
    publisher = mqtt.Client()

    uut_client_dict = {}
    for uut_num in range(1, NUM_UUT + 1):
        uut_client_dict[uut_num] = mqtt.Client(userdata={'name': 'UUT_%s' % uut_num, 'num': uut_num})
        uut_client_dict[uut_num].on_connect = on_connect
        uut_client_dict[uut_num].on_message = on_message_uut

    ui_dict = {}
    for ui in range(1, NUM_UI_VIEWERS + 1):
        ui_dict[ui] = mqtt.Client(userdata={'name': 'UI_%s' % ui, 'num': ui})
        # Put all UI viewers online subscribed appropriately
        ui_dict[ui].connect(BROKER_ADD, BROKER_PORT)
        # Subscribe to tests/associated threads of each test
        for test in range(1, NUM_TESTS_PER_UI + 1):
            for thread_num in range(1, NUM_THREAD_PER_UUT + 1):
                thread = 'uut%s/thread%s' % (test, thread_num)
                ui_dict[ui].subscribe(thread, QOS)
                print 'UI_%s subscribed to [%s]' % (ui, thread)
        ui_dict[ui].on_connect = on_connect
        ui_dict[ui].on_message = on_message_ui

    # Put all UUT online
    for idx, uut_client in uut_client_dict.iteritems():
        uut_client.connect(BROKER_ADD, BROKER_PORT)

    for idx, uut_client in uut_client_dict.iteritems():
        uut_client.loop_start()

    for idx, ui_client in ui_dict.iteritems():
        ui_client.loop_start()

    msg_num = 1

    while True:
        time.sleep(SEND_DELAY)

        for uut in range(1, NUM_UUT + 1):
            for thread_num in range(1, NUM_THREAD_PER_UUT + 1):
                thread = "uut%s/thread%s" % (uut, thread_num)
                msg = str(time.time())
                uut_client_dict[uut].publish(thread, msg, QOS)

        msg_num += 1
