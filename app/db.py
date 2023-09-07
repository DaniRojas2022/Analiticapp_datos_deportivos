import pyodbc
import click
from flask import current_app, g
import pandas as pd

def connection():
    s = '' #Your server name 
    d = 'CarSales' 
    u = '' #Your login
    p = '' #Your login password
    cstr = 'DRIVER={ODBC Driver 17 for SQL Server};SERVER='+s+';DATABASE='+d+';UID='+u+';PWD='+ p
    conn = pyodbc.connect(cstr)
    return conn

def pdLecturaDatos(nfile):
    return pd.read_csv(nfile)