# SECWebScraper


| Software  | Package Requirements |
| ------------- | ------------- |
| Python  | pandas, pandas_datareader, bs4, requests, re, smtplib, apscheduler|

## Summary

This project is a web scraper to pull data from filings and financial statements from SEC.gov for public companies. This program compiles data on the SPAC market from SEC.gov and spachero.com into a dataframe that updates daily. The program sends email notifications when a SPAC files an S-4.

I am in the process of adding SMS notifications when a SPAC files an S-4 or an 8-K detailing a definitive agreement.

