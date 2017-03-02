# redcap_link
Interface to Redcap.

## redcap_upload 
Upload JSON file of analysis results to Redcap

### usage:

```
as a function:
  import redcap_upload as rcu
  rcu.redcap_upload('Project Name','JSON file','INI file')

or from bash:
  python redcap_upload.py 'ProjectName' 'JSON file' 'INI file'

```

where 'Project Name' is one of :  CENC, Issues, CAHtest1 (until others are added)
   
and 'JSON file' looks like this:
   
```
   {
    "subject_id": "34P1015",
    "mt_analyst": "bkraft",
    "mt_datetime": "2016-Nov-15 16:45:22",
    "mt_gm_cortical_mean": "1.468",
    "mt_gm_cortical_std": "0.051", 
    "mt_gm_subcortical_mean": "0.518", 
    "mt_gm_subcortical_std": "0.042", 
    "mt_wm_cortical_mean": "0.567", 
    "mt_wm_cortical_std": "0.036",
    "mt_wmlesions_mean": "0.515", 
    "mt_wmlesions_std": "0.073"
   }
```   

and 'INI file' contains the API keys for Redcap projects

## redcap_check
Download all records in Redcap that match the one in a supplied JSON file

### usage:

```
as a function:
  import redcap_check as rcc
  rcc.redcap_check 'ProjectName' 'JSON file' 'INI file'
  
or from bash:
  python redcap_check.py 'ProjectName' 'JSON file' 'INI file'
```

where arguments are the same as for redcap_upload
    
All records like those in the input JSON file will be dumped to
a new CSV file with ".dump.csv" appended to the name of the input file
("mt.json" will become "mt.json.dump.csv")
   
  
