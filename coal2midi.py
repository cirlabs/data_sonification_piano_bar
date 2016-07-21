import csv
from datetime import datetime, timedelta
from miditime.miditime import MIDITime


class Coal2Midi(object):
    ''' Adapted from Jordan Wirfs-Brock's awesome coal production sonification.
    Post here: http://insideenergy.org/2016/05/03/listen-to-u-s-coal-production-fall-off-a-cliff/
    Code and data here: https://github.com/InsideEnergy/Data-for-stories/tree/master/20160503-coal-production-sonification
    '''

    epoch = datetime(1970, 1, 1)  # TODO: Allow this to override the midtime epoch
    mymidi = None

    tempo = 120

    min_attack = 30
    max_attack = 255

    min_duration = 1
    max_duration = 5

    seconds_per_year = 26

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
        return [r for r in csv_obj if int(r['Week']) not in [53]]

    def get_data_range(self, data_list, attribute_name):
        data_list = list(data_list)  # If the data is still a CSV object, once you loop through it you'll get rewind issues. So coercing to list.
        minimum = min([float(d[attribute_name]) for d in data_list])
        maximum = max([float(d[attribute_name]) for d in data_list])
        return [minimum, maximum]

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

    def map_week_to_day(self, year, week_num, desired_day_num=None):
        ''' Helper for weekly data, so when you jump to a new year you don't have notes playing too close together. Basically returns the first Sunday, Monday, etc. in 0-indexed integer format that is in that week. '''
        year_start = datetime(int(year), 1, 1).date()
        year_start_day = year_start.weekday()
        week_start_date = year_start + timedelta(weeks=1 * (int(week_num) - 1))
        week_start_day = week_start_date.weekday()
        if desired_day_num and week_start_day < desired_day_num:
            return week_start_date + timedelta(days=(desired_day_num - week_start_day))
        return week_start_date

    def data_to_pitch_tuned(self, datapoint):
        # Where does this data point sit in the domain of your data? (I.E. the min magnitude is 3, the max in 5.6). In this case the optional 'True' means the scale is reversed, so the highest value will return the lowest percentage.
        scale_pct = self.mymidi.linear_scale_pct(0, self.maximum, datapoint)

        # Another option: Linear scale, reverse order
        # scale_pct = mymidi.linear_scale_pct(0, self.maximum, datapoint, True)

        # Another option: Logarithmic scale, reverse order
        # scale_pct = mymidi.log_scale_pct(0, self.maximum, datapoint, True)

        # Pick a range of notes. This allows you to play in a key.
        mode = self.c_major

        #Find the note that matches your data point
        note = self.mymidi.scale_to_note(scale_pct, mode)

        #Translate that note to a MIDI pitch
        midi_pitch = self.mymidi.note_to_midi_pitch(note)

        return midi_pitch

    def mag_to_attack(self, datapoint):
        # Where does this data point sit in the domain of your data? (I.E. the min magnitude is 3, the max in 5.6). In this case the optional 'True' means the scale is reversed, so the highest value will return the lowest percentage.
        scale_pct = self.mymidi.linear_scale_pct(0, self.maximum, datapoint)

        #max_attack = 10

        adj_attack = (1 - scale_pct) * max_attack + 70
        #adj_attack = 100

        return adj_attack

    def csv_to_miditime(self):
        raw_data = self.read_csv('data/coal_prod_1984_2016_weeks_summed.csv')
        filtered_data = self.remove_weeks(raw_data)

        self.minimum = self.get_data_range(filtered_data, 'CoalProd')[0] / 1000000.0
        self.maximum = self.get_data_range(filtered_data, 'CoalProd')[1] / 1000000.0

        timed_data = []

        self.mymidi = MIDITime(self.tempo, 'coaltest.mid', self.seconds_per_year, self.base_octave, self.octave_range)

        # Get the first day in the dataset, so we can use it's day of the week to anchor our other weekly data.
        first_day = self.map_week_to_day(filtered_data[0]['Year'], filtered_data[0]['Week'])

        for r in filtered_data:
            # Convert the week to a date in that week
            week_start_date = self.map_week_to_day(r['Year'], r['Week'], first_day.weekday())
            # To get your date into an integer format, convert that date into the number of days since Jan. 1, 1970
            days_since_epoch = self.mymidi.days_since_epoch(week_start_date)
            # Convert that integer date into a beat
            beat = self.mymidi.beat(days_since_epoch)

            timed_data.append({
                'days_since_epoch': days_since_epoch,
                'beat': beat,
                'CoalProdMillions': float(r['CoalProd']) / 1000000.0
            })

        note_list = self.make_notes(timed_data, 'CoalProdMillions')
        # Add a track with those notes
        self.mymidi.add_track(note_list)

        # Output the .mid file
        self.mymidi.save_midi()

if __name__ == "__main__":
    mymidi = Coal2Midi()
