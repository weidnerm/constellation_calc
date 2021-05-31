import datetime
import time
import ephem
import argparse
from datetime import timedelta, datetime
from pytz import timezone

full_names = {
    'AND':'Andromeda',
    'ANT':'Antlia',
    'APS':'Apus',
    'AQR':'Aquarius',
    'AQL':'Aquila',
    'ARA':'Ara',
    'ARI':'Aries',
    'AUR':'Auriga',
    'BOO':'Boötes',
    'CAE':'Caelum',
    'CAM':'Camelopardalis',
    'CNC':'Cancer',
    'CVN':'Canes Venatici',
    'CMA':'Canis Major',
    'CMI':'Canis Minor',
    'CAP':'Capricornus',
    'CAR':'Carina',
    'CAS':'Cassiopeia',
    'CEN':'Centaurus',
    'CEP':'Cepheus',
    'CET':'Cetus',
    'CHA':'Chamaeleon',
    'CIR':'Circinus',
    'COL':'Columba',
    'COM':'Coma Berenices',
    'CRA':'Corona Australis',
    'CRB':'Corona Borealis',
    'CRV':'Corvus',
    'CRT':'Crater',
    'CRU':'Crux',
    'CYG':'Cygnus',
    'DEL':'Delphinus',
    'DOR':'Dorado',
    'DRA':'Draco',
    'EQU':'Equuleus',
    'ERI':'Eridanus',
    'FOR':'Fornax',
    'GEM':'Gemini',
    'GRU':'Grus',
    'HER':'Hercules',
    'HOR':'Horologium',
    'HYA':'Hydra',
    'HYI':'Hydrus',
    'IND':'Indus',
    'LAC':'Lacerta',
    'LEO':'Leo',
    'LMI':'Leo Minor',
    'LEP':'Lepus',
    'LIB':'Libra',
    'LUP':'Lupus',
    'LYN':'Lynx',
    'LYR':'Lyra',
    'MEN':'Mensa',
    'MIC':'Microscopium',
    'MON':'Monoceros',
    'MUS':'Musca',
    'NOR':'Norma',
    'OCT':'Octans',
    'OPH':'Ophiuchus',
    'ORI':'Orion',
    'PAV':'Pavo',
    'PEG':'Pegasus',
    'PER':'Perseus',
    'PHE':'Phoenix',
    'PIC':'Pictor',
    'PSC':'Pisces',
    'PSA':'Piscis Austrinus',
    'PUP':'Puppis',
    'PYX':'Pyxis',
    'RET':'Reticulum',
    'SGE':'Sagitta',
    'SGR':'Sagittarius',
    'SCO':'Scorpius',
    'SCL':'Sculptor',
    'SCT':'Scutum',
    'SER1':'Serpens',
    'SER2':'Serpens',
    'SEX':'Sextans',
    'TAU':'Taurus',
    'TEL':'Telescopium',
    'TRI':'Triangulum',
    'TRA':'Triangulum Australe',
    'TUC':'Tucana',
    'UMA':'Ursa Major',
    'UMI':'Ursa Minor',
    'VEL':'Vela',
    'VIR':'Virgo',
    'VOL':'Volans',
    'VUL':'Vulpecula',
}

def read_data_file(filename):
    
    boundary_data = {}
    
    fh = open(filename, 'r')
    lines = fh.readlines()
    fh.close()
    
    #  boundary_data[] = {} ['points'] = [] = {} ['ra_text'] = text
    #                                            ['ra_rad'] = float
    #                                            etc
    #                       ['visible']= [] = bool
    #
    for line in lines:
        fields = line.replace('\n','').replace('\r','').split(' ')
        
        ra_text = fields[0]
        dec_text = fields[1]
        name = fields[2]
        ra_rad = ephem.hours(ra_text)
        dec_rad = ephem.degrees(dec_text)
            
        fixed_body = ephem.FixedBody()
        fixed_body._ra = ra_rad
        fixed_body._dec = dec_rad
        fixed_body._epoch = '2000'
        
        point_entry = {}
        point_entry['ra_text'] = ra_text
        point_entry['dec_text'] = dec_text
        point_entry['ra_rad'] = ra_rad
        point_entry['dec_rad'] = dec_rad
        point_entry['fixed_body'] = fixed_body
        if name:
            if not name in boundary_data:
                boundary_data[name] = {'points' : [], 'visible' : [], 'name': name}
            
            boundary_data[name]['points'].append(point_entry)

    print(len(boundary_data))
    
    return boundary_data

def get_observer():
    # ~ observer = ephem.city("Miami")
    observer = ephem.Observer()
    observer.lon = "-80.27" # home
    observer.lat = "26.13" # home
    observer.elevation = 5
    observer.pressure = 0          # disable atmospheric refraction
    
    return observer

def compute_positions(boundary_data, when_local, when_utc):

    observer = get_observer()
    observer.date = when_utc
    effective_horizon = ephem.degrees("20:00:00")

    # ~ print()
    # ~ print(when_local, when_utc)
    for constellation in boundary_data:
        visible = True
        visible_count = 0
        for index in range(len(boundary_data[constellation]['points'])):
            temp_body = boundary_data[constellation]['points'][index]['fixed_body']
            temp_body.compute(observer)
            
            # ~ print("%d %s az=%.1f  alt=%.1f  horiz=%.1f  vis=%s" % (index, constellation, temp_body.az/0.01745329252, temp_body.alt/0.01745329252, effective_horizon/0.01745329252, (temp_body.alt >effective_horizon)))

            if temp_body.alt < effective_horizon:
                visible = False
            else:
                visible_count += 1

        visible_frac = (visible_count*10) / len(boundary_data[constellation]['points'])
        
        if (is_dark(when_utc)):
            visible_char = '_'
        elif (visible_frac == 10):
            visible_char = 'Y'
        elif (visible_frac == 0):
            visible_char = '.'
        else:
            visible_char = '%1d' % (visible_frac)
        boundary_data[constellation]['visible'].append(visible_char)

def convert_local_time_to_utc(local_datetime):
    # ~ UTC_OFFSET_TIMEDELTA = timedelta(hours=4)
    # ~ utc_datetime = local_datetime + UTC_OFFSET_TIMEDELTA 
    
    tz=timezone("US/Eastern")
    utc_datetime = local_datetime - tz.utcoffset(local_datetime) 
    
    # ~ print(local_datetime, utc_datetime)
    
    return utc_datetime
    
def is_dark(when_utc):
    observer = get_observer()
    observer.date = when_utc
    sun = ephem.Sun()
    sun.compute(observer)
    
    dark_angle = ephem.hours("-00:30:00")  # about 30 mins after sunset.
    
    if sun.alt < dark_angle:
        return_value = 0
    else:
        return_value = 1
    # ~ print("dark_angle = %.1f   isdark=%d" % (dark_angle/0.01745329252, return_value))
     
    return return_value
    
def dump_visiblity(local_times, results_list, datelist):
    print(datelist)
    row = 'abrv,name'
    for date in datelist:
        row += ',' + date.strftime('%m/%d/%y')
    print(row)
    
    for constellation in results_list[0]:
        row = '%s,%s' % (constellation, full_names[constellation])
        for boundary_data in results_list:
            row = row + ',' + ''.join(boundary_data[constellation]['visible'])
        print(row)
    
# ~ def dump_visiblity(local_times, results_list, datelist):
    # ~ print(datelist)
    # ~ row = '                             '
    # ~ for date in datelist:
        # ~ row += ' ' + date.strftime('%m/%d/%y')
    # ~ print(row)
    
    # ~ for constellation in results_list[0]:
        # ~ row = '%-4s %-20s  ' % (constellation, full_names[constellation])
        # ~ for boundary_data in results_list:
            # ~ row = row + '   ' + ''.join(boundary_data[constellation]['visible'])
        # ~ print(row)
    
def get_new_moon_list(start_datetime, num_dates=12):
    current_datetime = start_datetime
    calc_interval = timedelta(hours=1)
    skip_ahead_interval = timedelta(days=24)
    
    datelist = []

    sun = ephem.Sun()
    moon = ephem.Moon()
    observer = get_observer()
    
    sep_min = 180
    while len(datelist) < num_dates :
        observer.date = current_datetime
        sun.compute(observer)
        moon.compute(observer)
        sep = abs((float(ephem.separation(moon, sun)) / 0.01745329252) )
        if sep<sep_min:
            sep_min = sep
        elif (sep>sep_min) and (sep < 10.0):
            # it started growing.  make note and move on.
            sep_min = 180
            datelist.append(datetime.strptime(current_datetime.strftime('%m/%d/%Y'), '%m/%d/%Y'))
            current_datetime += skip_ahead_interval
        else:
            current_datetime += calc_interval
            
        # ~ print('%s %.1f %.1f' % (current_datetime, sep, sep_min))

    # ~ print(datelist)
    
    return datelist
    



def main():
    parser= argparse.ArgumentParser(description='constellation visibility calculator')
    parser.add_argument('--date', default='2021-05-31', help='date of calculation yyyy-mm-dd')
    parser.add_argument('--num_dates', default='0', help='number of new moon sessions')
    parser.add_argument('--data_file', default='bound_ed.dat', help='boundary data file')
    
    args = parser.parse_args()
    
    num_dates = int(args.num_dates)
    default_date = datetime.strptime(args.date, '%Y-%m-%d')
    
    if num_dates == 0:  
        observation_datelist = [default_date]
    else:
        observation_datelist = get_new_moon_list(default_date, num_dates)

    # ~ tztest(observation_datelist)
    # ~ sys.exit()
    
    
    results_list = []
    for observation_date in observation_datelist:

        boundary_data = read_data_file(args.data_file)   
        local_times = [] 

        for obs_hour in range(6+12, 12+12):
        # ~ for hours in range(5+12, 6+12):
            (year, month, day, hour, minute, second, _, _, _) = observation_date.timetuple()
            # ~ local_time_text = '%s %02d:00:00' % (args.date, obs_hour)
            # ~ local_time = datetime.strptime(local_time_text, '%Y-%m-%d %H:%M:%S')
            local_time = datetime(year, month, day, obs_hour, minute, second)
            local_times.append(local_time)
            utc_time = convert_local_time_to_utc(local_time)
            compute_positions(boundary_data, local_time, utc_time)
            # ~ is_dark_flag = is_dark(utc_time)
        
        results_list.append(boundary_data)

    dump_visiblity(local_times, results_list, observation_datelist)

# ~ def tztest(observation_datelist):
    # ~ tz=timezone("US/Eastern")
    # ~ for date in observation_datelist:
        # ~ print(date, tz.utcoffset(date))

if __name__ == "__main__":
    main()
    # ~ tztest()
    
    # ~ 2021-05-31T03:04:16Z
    
