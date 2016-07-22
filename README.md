# data_sonification_piano_bar
A SRCCON 2016 experiment.

## Quickstart
1. Fork the repo (Feel free to submit pull requests for the group!)
2. Set up your virtual environment. (Basically, install miditime.)
```bash
mkvirtualenv pianobar
pip install -r requirements.txt
```

### What next?
1. Get a CSV with a date/time element (date, datetime, year, month, week, etc.) and some other value (something you would normally put on a Y-axis of a chart).
2. Save a (renamed) copy of coal2midi.py (or just crib from it). Be sure to change the output .mid filename.
3. Run `python yourfilename.py`.
4. Play your .mid file, or import it into a sheetmusic program like Musescore.
