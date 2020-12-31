# type: ignore
"""Pull data from Weatherunderground Web API."""

__author__ = 'larry.clos'
__version__ = 20161219

import sys
import os
import datetime as dt
import json
import urllib2


_weatherrecords_json_dir = '/mnt/production_storage/sequencing/ops/metadata/misc/weather_jsons/'
_weatherunderground_key  = 'a684b2fcb86e3f53'


class Weather_Data_Dict:
    """Weather data object."""
    def __init__(self, records_dirpath=None):
        """Initiate weather data object."""
        if records_dirpath is None:
            records_dirpath = _weatherrecords_json_dir
        self.records_dirpath = records_dirpath
        self.currdate = dt.datetime.now().date()

        self.datedict = self._retrieve_local_records(records_dirpath)

    def fetch_datedict(self, datetag):
        """Fetch data."""
        if datetag in self.datedict:
            date_dict = self.datedict[datetag]
        else:
            date_dict = self._retrieve_online_daterecord(datetag)
            if date_dict != {}:
                self.datedict[datetag] = date_dict
                self._commit_datedict_to_jsons()
        return date_dict

    def massfetch_online_records(self, goback_daylim=30):
        """Mass fetch data."""
        if self.datedict != {}:
            oldest_dtobj = self._datetag_to_dtobj(sorted(self.datedict.keys())[0])
        else:
            oldest_dtobj = self.currdate
        for days_adjust in range(1, goback_daylim):
            datetag_to_fetch = self._dtobj_to_datetag(oldest_dtobj, days_adjust * -1)
            date_dict = self._retrieve_online_daterecord(datetag_to_fetch)
            if date_dict != {}:
                print(datetag_to_fetch)
                self.datedict[datetag_to_fetch] = date_dict

        self._commit_datedict_to_jsons()

    def _datetag_to_dtobj(self, datetag, days_adjust=0):
        dtobj = dt.datetime.strptime(datetag, '%Y%m%d')
        adj_dtobj = dtobj + dt.timedelta(days=int(days_adjust))
        return adj_dtobj

    def _dtobj_to_datetag(self, dtobj, days_adjust=0):
        adj_dtobj = dtobj + dt.timedelta(days=int(days_adjust))
        return adj_dtobj.strftime('%Y%m%d')
        # return '%d%02d%02d'%(adj_dtobj.year,adj_dtobj.month,adj_dtobj.day)

    def _retrieve_online_daterecord(self, datetag):
        url_str = 'http://api.wunderground.com/api/%s/history_%s/q/MI/Ann_Arbor.json' % (_weatherunderground_key,
                                                                                         datetag)
        try:
            f         = urllib2.urlopen(url_str)
            json_dict = json.loads(f.read())
            f.close()
            return json_dict
        except Exception:
            sys.stderr.write('[ERROR] Failed to retrieve %s data from web resource')
            return {}

    def _retrieve_local_records(self, records_dirpath):
        local_records_dict = {}
        json_datelt = [f.replace('.json', '') for f in os.listdir(records_dirpath)
                       if os.path.splitext(f)[-1] == '.json']
        for datetag in json_datelt:
            local_date_record = self._retrieve_json(datetag)
            if local_date_record == {}:
                continue
            else:
                local_records_dict[datetag] = local_date_record
        return local_records_dict

    def _retrieve_json(self, json_datetag):
        """Pull results dictionary from input json file."""
        json_fnpath = os.path.join(self.records_dirpath, json_datetag + '.json')
        if not os.path.exists(json_fnpath):
            sys.stderr.write('<WARNING> Retrieval error - json file does not exist:%s\n' % json_fnpath)
            return {}
        else:
            try:
                f = open(json_fnpath, 'rb')
                json_dict = json.load(f)
                f.close()
            except Exception:
                sys.stderr.write('<WARNING> Failure retrieving json file:%s\n' % json_fnpath)
                return {}
            else:
                # sys.stdout.write('<NOTICE> json file retrieved:%s\n'%json_fnpath)
                return json_dict

    def _write_json(self, json_datetag, datedict):
        """Commit input dictionary to json file, so long as dict not empty."""
        json_fnpath = os.path.join(self.records_dirpath, json_datetag + '.json')
        if datedict == {}:
            sys.stderr.write('<WARNING> Empty results = json file NOT produced:%s\n' % json_fnpath)
            return False
        f = open(json_fnpath, 'wb')
        json.dump(datedict, f)
        f.flush()
        f.close()
        return True

    def _commit_datedict_to_jsons(self):
        for datetag, datedict in self.datedict.items():
            self._write_json(datetag, datedict)


if __name__ == '__main__':
    wu_obj = Weather_Data_Dict(_weatherrecords_json_dir)
    for datetag in ['20161207']:

        print(datetag, wu_obj.datedict[datetag].keys())
        print(datetag, wu_obj.datedict[datetag]['history'].keys())
        for x in wu_obj.datedict[datetag]['history']['observations']:
            print(x['date'], x['dewptm'])
        # print datetag,wu_obj.datedict[datetag]['history']['dailysummary'][0].keys()
