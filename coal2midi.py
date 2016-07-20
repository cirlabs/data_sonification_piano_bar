import os
import csv
from datetime import datetime, timedelta
from miditime.miditime import MIDITime
# from django.utils.timezone import make_aware, get_default_timezone


class Coal2Midi(object):

    # tz = get_default_timezone()
    epoch = datetime(1970, 1, 1)
    mymidi = None

    min_value = 0
    max_value = 5.7

    tempo = 120
    min_pitch = 25
    max_pitch = 88

    min_attack = 30
    max_attack = 255

    min_duration = 1
    max_duration = 5

    seconds_per_year = 7

    c_major = ['C', 'D', 'E', 'F', 'G', 'A', 'B']
    c_minor = ['C', 'D', 'Eb', 'F', 'G', 'Ab', 'Bb']
    a_minor = ['A', 'B', 'C', 'D', 'E', 'F', 'F#', 'G', 'G#']
    c_blues_minor = ['C', 'Eb', 'F', 'F#', 'G', 'Bb']
    d_minor = ['D', 'E', 'F', 'G', 'A', 'Bb', 'C']
    c_gregorian = ['C', 'D', 'Eb', 'F', 'G', 'Ab', 'A', 'Bb']

    current_key = 'd_minor'
    base_octave = 4
    octave_range = 3

    def __init__(self):
        self.csv_to_miditime()

    def read_csv(self, filepath):
        csv_file = open(filepath, 'rU')
        return csv.DictReader(csv_file, delimiter=',', quotechar='"')

    def remove_weeks(self, csv_obj):
        return [r for r in csv_obj if r['Week'] not in [1, 27, 52, 53]]

    def make_notes(self, data_timed, data_key):
        note_list = []

        start_time = data_timed[0]['beat']

        for d in data_timed:
            note_list.append([
                d['beat'] - start_time,
                self.mag_to_pitch_tuned(d[data_key]),
                100,
                #mag_to_attack(d['magnitude']),  # attack
                0.5  # duration, in beats
            ])

    # def week_magic(day):
    #     day_of_week = day.weekday()
    #
    #     to_beginning_of_week = datetime.timedelta(days=day_of_week)
    #     beginning_of_week = day - to_beginning_of_week
    #
    #     to_end_of_week = datetime.timedelta(days=6 - day_of_week)
    #     end_of_week = day + to_end_of_week
    #
    #     return (beginning_of_week, end_of_week)

    def csv_to_miditime(self):
        raw_data = self.read_csv('data/coal_prod_1984_2016_weeks_summed.csv')
        filtered_data = self.remove_weeks(raw_data)

        timed_data = []

        mymidi = MIDITime(80, 'myfile.mid', 45, 2, 5)

        # first_date = filtered_rows[0]

        for r in filtered_data:
            year_start = datetime(int(r['Year']), 1, 1).date()
            # print year_start
            week_start_date = year_start + timedelta(weeks=1 * (int(r['Week']) - 1))
            print week_start_date
            days_since_epoch = mymidi.days_since_epoch(week_start_date)
            beat = mymidi.beat(days_since_epoch)
            # mydict = {'days_since_epoch': int(float(row[0])), 'CoalProdMillions': float(r['CoalProd'] / 1000000)}
            timed_data.append({
                'days_since_epoch': days_since_epoch,
                'beat': beat,
                'CoalProdMillions': float(r['CoalProd']) / 1000000.0
            })
            # processed_data.append(mydict)

        note_list = self.make_notes(timed_data, 'CoalProdMillions')
        # Add a track with those notes
        mymidi.add_track(note_list)

        # Output the .mid file
        mymidi.save_midi()

    def mag_to_pitch_tuned(self, magnitude):
        # Where does this data point sit in the domain of your data? (I.E. the min magnitude is 3, the max in 5.6). In this case the optional 'True' means the scale is reversed, so the highest value will return the lowest percentage.
        scale_pct = mymidi.linear_scale_pct(10, 25, magnitude)

        # Another option: Linear scale, reverse order
        # scale_pct = mymidi.linear_scale_pct(3, 5.7, magnitude, True)

        # Another option: Logarithmic scale, reverse order
        # scale_pct = mymidi.log_scale_pct(3, 5.7, magnitude, True)

        # Pick a range of notes. This allows you to play in a key.
        c_major = ['C', 'D', 'E', 'F', 'G', 'A', 'B']

        #Find the note that matches your data point
        note = mymidi.scale_to_note(scale_pct, c_major)

        #Translate that note to a MIDI pitch
        midi_pitch = mymidi.note_to_midi_pitch(note)

        return midi_pitch

    def mag_to_attack(self, magnitude):
        # Where does this data point sit in the domain of your data? (I.E. the min magnitude is 3, the max in 5.6). In this case the optional 'True' means the scale is reversed, so the highest value will return the lowest percentage.
        scale_pct = mymidi.linear_scale_pct(10, 25, magnitude)

        #max_attack = 10

        adj_attack = (1-scale_pct)*max_attack + 70
        #adj_attack = 100

        return adj_attack

if __name__ == "__main__":
    mymidi = Coal2Midi()
