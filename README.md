# SPAC Data Web Scraper


| Software  | Package Requirements |
| ------------- | ------------- |
| Python  | pandas, pandas_datareader, bs4, requests, re, smtplib, apscheduler|

## Summary

This project is a generic web scraper to pull data from filings and financial statements from SEC.gov. In this use case of this scraper, the program compiles data on the SPAC market from SEC.gov and spachero.com into a dataframe that updates daily. The program has the functionality to send email notifications when a SPAC files an S-4. Some of the variables tracked include, share price, warrant price, market cap, volume, option availability, S-4 filing date, and returns since S-4.

I am in the process of adding SMS notifications,  when a SPAC files an S-4 or an 8-K detailing a definitive agreement.

