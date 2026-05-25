import streamlit as st
import pandas as pd
import plotly.express as px
import requests
import numpy as np

from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
