import pandas as pd
import sys
import xml.etree.cElementTree as et
from math import radians, cos, sin, asin, sqrt
import numpy as np
from pykalman import KalmanFilter

def smooth(kalman_data):
    initial_state = kalman_data.iloc[0]
    observation_covariance = np.diag([0.000017, .000017]) ** 2 
    transition_covariance = np.diag([0.00001, 0.00001]) ** 2 
    kf = KalmanFilter(
        initial_state_mean=initial_state,
        initial_state_covariance=observation_covariance,
        observation_covariance=observation_covariance,
        transition_covariance=transition_covariance,
    )
    kalman_smoothed, state_cov = kf.smooth(kalman_data)

    return pd.DataFrame(kalman_smoothed, columns=['lat', 'lon'])

## taken from https://stackoverflow.com/questions/4913349/haversine-formula-in-python-bearing-and-distance-between-two-gps-points
def hav_distance(lat1, lon1, lat2, lon2):
    """
    Calculate the great circle distance between two points 
    on the earth (specified in decimal degrees)
    """
    # convert decimal degrees to radians 
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])

    # haversine formula 
    dlon = lon2 - lon1 
    dlat = lat2 - lat1 
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a)) 
    r = 6371000 # Radius of earth in meters. Use 3956 for miles
    return c * r 

def distance(df):
    df['prev_lat'] = df.shift()['lat']
    df['prev_lon'] = df.shift()['lon']
    # df = df.iloc[1:]
    df['distances'] = df.apply(lambda x: hav_distance(x['lat'], x['lon'], x['prev_lat'], x['prev_lon']), axis=1)
    total = df['distances'].sum()
    return total

def get_data(xmlFile):
    parsedXML = et.parse( xmlFile)
    df =pd.DataFrame(columns=['lat', 'lon'], dtype=np.float)
    for item in parsedXML.iter('{http://www.topografix.com/GPX/1/0}trkpt'):
        df = df.append(item.attrib, ignore_index=True)
    return df.astype('float64')


def output_gpx(points, output_filename):
    """
    Output a GPX file with latitude and longitude from the points DataFrame.
    """
    from xml.dom.minidom import getDOMImplementation
    def append_trkpt(pt, trkseg, doc):
        trkpt = doc.createElement('trkpt')
        trkpt.setAttribute('lat', '%.8f' % (pt['lat']))
        trkpt.setAttribute('lon', '%.8f' % (pt['lon']))
        trkseg.appendChild(trkpt)
    
    doc = getDOMImplementation().createDocument(None, 'gpx', None)
    trk = doc.createElement('trk')
    doc.documentElement.appendChild(trk)
    trkseg = doc.createElement('trkseg')
    trk.appendChild(trkseg)
    
    points.apply(append_trkpt, axis=1, trkseg=trkseg, doc=doc)
    
    with open(output_filename, 'w') as fh:
        doc.writexml(fh, indent=' ')


def main():
    points = get_data(sys.argv[1])
    print('Unfiltered distance: %0.2f' % (distance(points),))

    points = get_data(sys.argv[1])
    smoothed_points = smooth(points)
    print('Filtered distance: %0.2f' % (distance(smoothed_points),))
    output_gpx(smoothed_points, 'out.gpx')


if __name__ == '__main__':
    main()