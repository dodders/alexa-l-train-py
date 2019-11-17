from google.transit import gtfs_realtime_pb2
import urllib.request
import os
from datetime import datetime
import logging

log = logging.getLogger()
logging.basicConfig(level=logging.INFO)


def get_stop_times():
    log.info('getting stop times...')
    mta_url = os.getenv('MTAURL')
    mta_key = os.getenv('MTAKEY')
    mta_feedid = os.getenv('MTAFEEDID')
    bedford = 'L08N'
    # bedford = '115N'

    feed = gtfs_realtime_pb2.FeedMessage()
    url = mta_url + mta_key + '&feed_id=' + mta_feedid
    # url = mta_url + mta_key + '&feed_id=' + '1'
    response = urllib.request.urlopen(url)
    feed.ParseFromString(response.read())

    stop_times = []
    for entity in feed.entity:
        if hasattr(entity, 'trip_update'):
            for stop_time_update in entity.trip_update.stop_time_update:
                if stop_time_update.stop_id == bedford:
                    try:
                        dt = datetime.fromtimestamp(stop_time_update.arrival.time)
                        stop_times.append(dt)
                        if len(stop_times) >= 5:
                            log.info('stop times found.')
                            return stop_times
                    except ValueError as err:
                        log.info('invalid timestamp: %s. err: %s'.format(str(stop_time_update.arrival.time), err))
    return stop_times


def get_next_trains():
    log.info('starting get next trains...')
    times = get_stop_times()
    log.info('stop times: %s', times)
    curr_time = datetime.now()
    gaps = [round((t - curr_time).seconds / 60) for t in times]  # list of gaps in seconds...
    log.info('gaps: %s', gaps)
    return gaps


if __name__ == '__main__':
    print(get_next_trains())
