import csv
from datetime import datetime
from miditime.miditime import MIDITime

from lib.jaws_notes import JAWS_NOTES


class leaks2midi(object):
    ''' Submitted by Michael Corey. '''

    epoch = datetime(2008, 1, 1)  # Not actually necessary, but optional to specify your own
    mymidi = None

    tempo = 120

    min_attack = 30
    max_attack = 255

    seconds_per_year = 24

    base_octave = 2
    octave_range = 5

    def __init__(self):
        self.just_jaws('williams.mid')
        # self.csv_to_miditime('data/keystone_gas_plant.csv', 'keystone_leaks.mid', 3)
        self.csv_to_miditime('data/waha_gas_plant.csv', 'waha_leaks.mid', 4)

    def read_csv(self, filepath):
        csv_file = open(filepath, 'rU')
        return csv.DictReader(csv_file, delimiter=',', quotechar='"')

    def bigger_boat(self, start_beat, num_beats, miditime_instance, octave):
        # octave = 3

        notes = []
        for r in JAWS_NOTES:
            if r[0] <= num_beats:
                try:
                    octavated_pitch = '%s%s' % (r[1], octave + r[4],)
                except:
                    octavated_pitch = '%s%s' % (r[1], octave,)
                try:
                    channel = r[5]
                except:
                    channel = 0
                adjusted_beat = r[0] + start_beat
                midi_pitch = miditime_instance.note_to_midi_pitch(octavated_pitch)
                notes.append([[adjusted_beat, midi_pitch, r[2], r[3]], channel])

        return notes

    def just_jaws(self, outfile):  # Just play the whole song
        mymidi = MIDITime(self.tempo, outfile, self.seconds_per_year, self.base_octave, self.octave_range, self.epoch)
        note_list = self.bigger_boat(0, 70, mymidi, 3)
        # Add a track with those notes
        mymidi.add_track(note_list)

        # Output the .mid file
        mymidi.save_midi()

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

        # Add a track with those notes
        mymidi.add_track(note_list)

        # Output the .mid file
        mymidi.save_midi()

if __name__ == "__main__":
    mymidi = leaks2midi()
