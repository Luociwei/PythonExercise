# -*- coding: utf-8 -*-
import gc


recording_list = []
_recorder_list = []


def get_recording_list():
    return recording_list


def add_recorder(recorder):
    if isinstance(recorder, Recorder):
        _recorder_list.append(recorder)


def del_recorder(recorder):
    if isinstance(recorder, Recorder):
        _recorder_list.remove(recorder)


def clear_recording():
    '''
    Clear recorder list and recording list
    To provide a clean test start.
    '''
    global _recorder_list
    global recording_list
    _recorder_list = []
    recording_list = []


def start_record():
    gc.collect()
    for recorder in _recorder_list:
        recorder.start()


def stop_record():
    for recorder in _recorder_list:
        recorder.stop()


def assert_action_seq(seq_id, action):
    msg = 'seq_id: {}, action: {}, full records: {}'
    msg = msg.format(seq_id, action, recording_list)
    assert recording_list[seq_id] == action, msg


def assert_action_call(action):
    result = False
    for item in recording_list:
        if item == action:
            result = True
            break
    assert result is True


def assert_action_count(action, count):
    num = 0
    for item in recording_list:
        if item == action:
            num += 1
    assert num == count


class Recorder(object):
    '''
    Record actions in emulator to a list to verify in unit test.
    '''

    def __init__(self, max_record=5000):
        del recording_list[:]
        self._max_record = max_record

    def start(self):
        del recording_list[:]

    def stop(self):
        del recording_list[:]

    def record(self, content):
        if len(recording_list) < self._max_record:
            recording_list.append(content)
        else:
            raise Exception("Record commands too much.")
