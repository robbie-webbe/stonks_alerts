import pandas as pd
from datetime import datetime as dt
import requests
import tarfile
import os

# pick out the csv files needed. File should be concatenated XSA format csv.
obslist_files = 'obslist_myhp_gpponti.csv'

# set the current time as a variable for comparison
run_datetime = dt.now()

# set a start date for observations to download OBSMLIs (for now set a start time of 1st July 2023 for last 12 months)
start_date = dt.fromisoformat('2023-07-01 00:00:00.000')

# open the observation details file as a dataframe
obs_detail_df = pd.read_csv(obslist_files, dtype=object, usecols=[0,5,11], header=0, names=['OBSID','START DATE','PROP END DATE'])

# collect a list of good obsids for the date range desired
good_obsids = []

# for each observation in the log
for i in range(len(obs_detail_df)):

    # check that the propietary period (if any) has ended
    if dt.fromisoformat(obs_detail_df['PROP END DATE'][i]) < run_datetime:

        # check that the observation start time is after the desired benchmark
        if dt.fromisoformat(obs_detail_df['START DATE'][i]) > start_date:

            # if so then append to the list
            good_obsids.append(obs_detail_df['OBSID'][i])

print(good_obsids)
print(len(good_obsids))

# now download and process the obsmli files for each good observation needed.
for obsid in good_obsids:

        # download the obsmli files, if they exist
        url = 'http://nxsa.esac.esa.int/nxsa-sl/servlet/data-action-aio?extension=FTZ&level=PPS&name=OBSMLI&obsno='+obsid
        dl_dets = requests.get(url, timeout=(10,600))
        if dl_dets.status_code == 200:
            with open('./_dl_temp_/obsmli.tar','wb') as saved_file:
                saved_file.write(dl_dets.content)
        else:
            continue

        # if there was a file downloaded successfully of non-zero size
        if os.path.getsize('./_dl_temp_/obsmli.tar') != 0:
            # try and open it, and move on if not
            try:
                tar = tarfile.open('./_dl_temp_/obsmli.tar')
            except:
                os.system('rm ./_dl_temp_/obsmli.tar')
                continue
            else:
                tar = tarfile.open('./_dl_temp_/obsmli.tar')

            # find the file in the tar relating to the EP source detections
            EP_file = 0
            for file in tar.getnames():
                if 'EPX' in file:
                    EP_file = file

            # extract the desired file, close the tar object, and delete file
            tar.extract(EP_file, path='./_dl_temp_/')
            tar.close()
            os.system('rm ./_dl_temp_/obsmli.tar')

            # then move the file desired to the output folder
            os.system('mv ./_dl_temp_/'+EP_file+' ./OBSMLI/GP_Ponti/'+EP_file[15:-4]+'.fits')

            # and delete the empty folder
            os.system('rm -r ./_dl_temp_/'+obsid+'/')