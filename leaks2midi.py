import os
import csv
from datetime import datetime, timedelta
from miditime.miditime import MIDITime


class leaks2midi(object):
    ''' Submitted by Michael Corey. '''

    epoch = datetime(2009, 1, 1)  # Not actually necessary, but optional to specify your own
    mymidi = None

    tempo = 120

    min_attack = 30
    max_attack = 255

    seconds_per_year = 48

    base_octave = 2
    octave_range = 5

    def __init__(self):
        self.csv_to_miditime('data/keystone_gas_plant.csv', 'keystone_leaks.mid', 3)
        self.csv_to_miditime('data/waha_gas_plant.csv', 'waha_leaks.mid', 4)

    def read_csv(self, filepath):
        csv_file = open(filepath, 'rU')
        return csv.DictReader(csv_file, delimiter=',', quotechar='"')

    def bigger_boat(self, start_beat, num_beats, miditime_instance, octave):
        # octave = 3
        raw_notes = [
            [0, 'E', 75, 1],
            [1, 'F', 75, 2],

            [6, 'E', 75, 1],
            [7, 'F', 75, 1],
            [8, 'E', 75, 2],

            [12, 'E', 75, 1],
            [13, 'F', 75, 1],

            [14, 'E', 75, 1],
            [15, 'F', 75, 2],

            [18, 'E', 75, 0.75],
            [19, 'F', 75, 0.75],
            [20, 'E', 75, 0.75],
            [21, 'F', 75, 0.75],
            [22, 'E', 75, 0.75],
            [23, 'F', 75, 0.75],
            [24, 'E', 75, 0.75],
            [25, 'F', 75, 0.75],

            [26, 'E', 75, 0.5],
            [26.5, 'F', 75, 0.5],
            [27, 'E', 75, 0.5],
            [27.5, 'F', 75, 0.5],
            [28, 'E', 75, 0.5],
            [28.5, 'F', 75, 0.5],
            [29, 'E', 75, 0.5],
            [29.5, 'F', 75, 0.5],

            [30, 'E', 75, 0.5],
            [30.5, 'F', 75, 0.5],
            [31, 'E', 75, 0.5],
            [31.5, 'F', 75, 0.5],
            [32, 'E', 75, 0.5],
            [32.5, 'F', 75, 0.5],
            [33, 'E', 75, 0.5],
            [33.5, 'F', 75, 0.5],

            [34, 'E', 75, 0.5],
            [34.5, 'F', 75, 0.5],
            [35, 'E', 75, 0.5],
            [35.5, 'F', 75, 0.5],
            [36, 'E', 75, 0.5],
            [36.5, 'F', 75, 0.5],
            [37, 'E', 75, 0.5],
            [37.5, 'F', 75, 0.5],

            [38, 'E', 75, 0.5],
            [38.5, 'F', 75, 0.5],
            [39, 'E', 75, 0.5],
            [39.5, 'F', 75, 0.5],
            [40, 'E', 75, 0.5],
            [40.5, 'F', 75, 0.5],
            [41, 'E', 75, 0.5],
            [41.5, 'F', 75, 0.5],

            # strings under
            [42, 'E', 75, 0.5],
            [42.5, 'F', 75, 0.5],
            [43, 'E', 75, 0.5],
            [43.5, 'F', 75, 0.5],
            [44, 'E', 75, 0.5],
            [44.5, 'F', 75, 0.5],
            [45, 'E', 75, 0.5],
            [45.5, 'F', 75, 0.5],

            # notes over
            [43, 'G', 75, 0.25, 1, 1],
            [43.25, 'B', 75, 0.25, 1, 1],
            [43.5, 'F', 75, 6.5, 2, 1],

            # strings under
            [46, 'E', 75, 0.5],
            [46.5, 'F', 75, 0.5],
            [47, 'E', 75, 0.5],
            [47.5, 'F', 75, 0.5],
            [48, 'E', 75, 0.5],
            [48.5, 'F', 75, 0.5],
            [49, 'E', 75, 0.5],
            [49.5, 'F', 75, 0.5],

            [50, 'E', 75, 0.5],
            [50.5, 'F', 75, 0.5],
            [51, 'E', 75, 0.5],
            [51.5, 'F', 75, 0.5],
            [52, 'E', 75, 0.5],
            [52.5, 'F', 75, 0.5],
            [53, 'E', 75, 0.5],
            [53.5, 'F', 75, 0.5],

            # notes over
            [50.5, 'G', 75, 0.25, 1, 1],
            [50.75, 'B', 75, 0.25, 1, 1],
            [51, 'F', 75, 0.25, 2, 1],
            [51.25, 'G', 75, 0.25, 2, 1],
            [51.5, 'D', 75, 0.25, 2, 1],
            [51.75, 'G', 75, 0.25, 1, 1],
            [52, 'F', 75, 6, 1, 1],

            # strings under
            [54, 'E', 75, 0.5],
            [54.5, 'F', 75, 0.5],
            [55, 'E', 75, 0.5],
            [55.5, 'F', 75, 0.5],
            [56, 'E', 75, 0.5],
            [56.5, 'F', 75, 0.5],
            [57, 'E', 75, 0.5],
            [57.5, 'F', 75, 0.5],
        ]
        notes = []
        for r in raw_notes:
            if r[0] <= num_beats:
                try:
                    octavated_pitch = '%s%s' % (r[1], octave + r[4],)
                except:
                    octavated_pitch = '%s%s' % (r[1], octave,)
                try:
                    channel = r[5]
                except:
                    channel = 0
                r[0] += start_beat
                r[1] = miditime_instance.note_to_midi_pitch(octavated_pitch)
                notes.append([[r[0], r[1], r[2], r[3]], channel])

        return notes

    def csv_to_miditime(self, infile, outfile, octave):
        raw_data = list(self.read_csv(infile))

        mymidi = MIDITime(self.tempo, outfile, self.seconds_per_year, self.base_octave, self.octave_range, self.epoch)

        note_list = []

        for r in raw_data:
            began_date = datetime.strptime(r["began_date"], "%Y-%m-%d %H:%M:%S+00:00")  # 2009-01-15 16:15:00+00:00
            ended_date = datetime.strptime(r["ended_date"], "%Y-%m-%d %H:%M:%S+00:00")

            began_days_since_epoch = mymidi.days_since_epoch(began_date)
            ended_days_since_epoch = mymidi.days_since_epoch(ended_date)

            start_beat = mymidi.beat(began_days_since_epoch)
            end_beat = mymidi.beat(ended_days_since_epoch)
            duration_in_beats = end_beat - start_beat
            if duration_in_beats < 3:
                duration_in_beats = 3

            # print start_beat, duration_in_beats
            note_list = note_list + self.bigger_boat(round(start_beat), duration_in_beats, mymidi, octave)

        # Just play the whole song
        # note_list = self.bigger_boat(0, 70)
        # Add a track with those notes
        mymidi.add_track(note_list)

        # Output the .mid file
        mymidi.save_midi()

if __name__ == "__main__":
    mymidi = leaks2midi()
