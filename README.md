# Pipeline

1) get the data

    poetry shell

    python toggl_timesheet/entrypoints/get_raw_data.py --year 2024 --month 5
    
2) prepare aggregated report
    
    python toggl_timesheet/entrypoints/data_preparation.py -i data/bronze/2024/06/time_entries.csv -o ./data/silver/2024/06/timesheet.csv