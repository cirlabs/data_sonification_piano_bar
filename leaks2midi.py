import os
import csv
from datetime import datetime, timedelta
from miditime.miditime import MIDITime


class bomb2midi(object):
    ''' Submitted by Jennifer LaFleur. '''

    epoch = datetime(1945, 1, 1)  # Not actually necessary, but optional to specify your own
    mymidi = None

    min_value = 0
    max_value = 5.7

    tempo = 120

    min_attack = 30
    max_attack = 255

    min_duration = 1
    max_duration = 5

    seconds_per_year = 3

    c_major = ['C', 'D', 'E', 'F', 'G', 'A', 'B']
    c_minor = ['C', 'D', 'Eb', 'F', 'G', 'Ab', 'Bb']
    a_minor = ['A', 'B', 'C', 'D', 'E', 'F', 'F#', 'G', 'G#']
    c_blues_minor = ['C', 'Eb', 'F', 'F#', 'G', 'Bb']
    d_minor = ['D', 'E', 'F', 'G', 'A', 'Bb', 'C']
    c_gregorian = ['C', 'D', 'Eb', 'F', 'G', 'Ab', 'A', 'Bb']

    current_key = c_major
    base_octave = 2
    octave_range = 5

    def __init__(self):
        self.csv_to_miditime()

    def read_csv(self, filepath):
        csv_file = open(filepath, 'rU')
        return csv.DictReader(csv_file, delimiter=',', quotechar='"')

    def remove_weeks(self, csv_obj):
        return [r for r in csv_obj if r['Date'] not in ['']]

    def round_to_quarter_beat(self, input):
        return round(input * 4) / 4

    def make_notes(self, data_timed, data_key):
        note_list = []

        start_time = data_timed[0]['beat']

        for d in data_timed:
            note_list.append([
                self.round_to_quarter_beat(d['beat'] - start_time),
                self.data_to_pitch_tuned(d[data_key]),
                100,
                #mag_to_attack(d['magnitude']),  # attack
                1  # duration, in beats
            ])
        return note_list

    def bigger_boat(self, num_beats):
        octave = 4
        notes = [
            [0, self.mymidi.note_to_midi_pitch('E%s' % (octave,)), 75, 1],
            [1, self.mymidi.note_to_midi_pitch('F%s' % (octave,)), 75, 2],

            [6, self.mymidi.note_to_midi_pitch('E%s' % (octave,)), 75, 1],
            [7, self.mymidi.note_to_midi_pitch('F%s' % (octave,)), 75, 1],
            [8, self.mymidi.note_to_midi_pitch('E%s' % (octave,)), 75, 2],

            [12, self.mymidi.note_to_midi_pitch('E%s' % (octave,)), 75, 1],
            [13, self.mymidi.note_to_midi_pitch('F%s' % (octave,)), 75, 1],

            [14, self.mymidi.note_to_midi_pitch('E%s' % (octave,)), 75, 1],
            [15, self.mymidi.note_to_midi_pitch('F%s' % (octave,)), 75, 2],

            [17, self.mymidi.note_to_midi_pitch('E%s' % (octave,)), 75, 0.75],
            [18, self.mymidi.note_to_midi_pitch('F%s' % (octave,)), 75, 0.75],
            [19, self.mymidi.note_to_midi_pitch('E%s' % (octave,)), 75, 0.75],
            [20, self.mymidi.note_to_midi_pitch('F%s' % (octave,)), 75, 0.75],
        ]

        return notes

    def csv_to_miditime(self):
        raw_data = list(self.read_csv('data/keystone_gas_plant.csv'))
        # filtered_data = self.remove_weeks(raw_data)

        self.mymidi = MIDITime(self.tempo, 'keystone_leaks.mid', self.seconds_per_year, self.base_octave, self.octave_range, self.epoch)

        # self.minimum = self.mymidi.get_data_range(filtered_data, 'Yieldnum')[0]
        # self.maximum = self.mymidi.get_data_range(filtered_data, 'Yieldnum')[1]
        #
        # timed_data = []
        #
        # for r in filtered_data:
        #     python_date = datetime.strptime(r["Date"], "%m/%d/%Y")
        #     days_since_epoch = self.mymidi.days_since_epoch(python_date)
        #     beat = self.mymidi.beat(days_since_epoch)
        #     timed_data.append({
        #         'days_since_epoch': days_since_epoch,
        #         'beat': beat,
        #         'BombYieldMillions': float(r['Yieldnum'])
        #     })
        #
        # note_list = self.make_notes(timed_data, 'BombYieldMillions')

        note_list = self.bigger_boat(1)
        # Add a track with those notes
        self.mymidi.add_track(note_list)

        # Output the .mid file
        self.mymidi.save_midi()

    def data_to_pitch_tuned(self, datapoint):
        # Where does this data point sit in the domain of your data? (I.E. the min magnitude is 3, the max in 5.6). In this case the optional 'True' means the scale is reversed, so the highest value will return the lowest percentage.
        #scale_pct = self.mymidi.linear_scale_pct(0, self.maximum, datapoint)

        # Another option: Linear scale, reverse order
        # scale_pct = self.mymidi.linear_scale_pct(0, self.maximum, datapoint, True)
        # print 10**self.maximum
        # Another option: Logarithmic scale, reverse order
        scale_pct = self.mymidi.log_scale_pct(0, self.maximum, datapoint, True, 'log')

        # Pick a range of notes. This allows you to play in a key.
        mode = self.current_key

        #Find the note that matches your data point
        note = self.mymidi.scale_to_note(scale_pct, mode)

        #Translate that note to a MIDI pitch
        midi_pitch = self.mymidi.note_to_midi_pitch(note)
        print scale_pct, note

        return midi_pitch

    def mag_to_attack(self, datapoint):
        # Where does this data point sit in the domain of your data? (I.E. the min magnitude is 3, the max in 5.6). In this case the optional 'True' means the scale is reversed, so the highest value will return the lowest percentage.
        scale_pct = self.mymidi.linear_scale_pct(0, self.maximum, datapoint)

        #max_attack = 10

        adj_attack = (1 - scale_pct) * max_attack + 70
        #adj_attack = 100

        return adj_attack

if __name__ == "__main__":
    mymidi = bomb2midi()
