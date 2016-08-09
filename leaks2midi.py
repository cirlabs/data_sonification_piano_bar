import csv
import math
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

    base_octave = 3
    octave_range = 5

    def __init__(self):
        self.just_jaws('williams.mid')
        self.csv_to_miditime('data/keystone_gas_plant.csv', 'keystone_leaks.mid', 3)
        self.csv_to_miditime('data/waha_gas_plant.csv', 'waha_leaks.mid', 3)

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

    def bigger_boat_2(self, start_beat, next_note_index, num_beats, miditime_instance, octave):
        '''Play through the song, x notes at a time (rather than starting over.)'''

        # Make list of possible beats
        beats_list = sorted(list(set([j[0] for j in JAWS_NOTES])))
        # print beats_list

        notes = []
        print next_note_index, len(beats_list)
        if next_note_index >= len(beats_list):
            next_note_index = 0
        print JAWS_NOTES[next_note_index]
        first_jaws_beat = beats_list[next_note_index]
        adjusted_start_beat = start_beat - first_jaws_beat
        print adjusted_start_beat
        print 'First jaws beat: %s   adjusted_start_beat: %s   num_beats: %s' % (first_jaws_beat, adjusted_start_beat, num_beats)
        for note_index, r in enumerate(JAWS_NOTES):
            if r[0] >= first_jaws_beat and r[0] <= first_jaws_beat + num_beats:
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
                next_note_index = beats_list.index(r[0]) + 1
        print notes

        return (notes, next_note_index)

    def just_jaws(self, outfile):  # Just play the whole song
        mymidi = MIDITime(self.tempo, outfile, self.seconds_per_year, self.base_octave, self.octave_range, self.epoch)
        note_list = self.bigger_boat(0, 70, mymidi, self.base_octave)
        # Add a track with those notes
        mymidi.add_track(note_list)

        # Output the .mid file
        mymidi.save_midi()

    def csv_to_miditime(self, infile, outfile, octave):
        raw_data = list(self.read_csv(infile))

        mymidi = MIDITime(self.tempo, outfile, self.seconds_per_year, self.base_octave, self.octave_range, self.epoch)

        note_list = []
        start_note_index = 0

        for r in raw_data:
            began_date = datetime.strptime(r["began_date"], "%Y-%m-%d %H:%M:%S+00:00")  # 2009-01-15 16:15:00+00:00
            ended_date = datetime.strptime(r["ended_date"], "%Y-%m-%d %H:%M:%S+00:00")

            began_days_since_epoch = mymidi.days_since_epoch(began_date)
            ended_days_since_epoch = mymidi.days_since_epoch(ended_date)

            start_beat = mymidi.beat(began_days_since_epoch)
            end_beat = mymidi.beat(ended_days_since_epoch)
            duration_in_beats = end_beat - start_beat

            # if duration_in_beats < 3:
            #     duration_in_beats = 3
            # print start_beat, duration_in_beats
            new_notes, start_note_index = self.bigger_boat_2(start_beat, start_note_index, duration_in_beats, mymidi, octave)
            note_list = note_list + new_notes

        # Add a track with those notes
        mymidi.add_track(note_list)

        # Output the .mid file
        mymidi.save_midi()

if __name__ == "__main__":
    mymidi = leaks2midi()
