import pandas as pd
import os
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsClassifier
from sklearn.metrics import accuracy_score,classification_report


textFile = open(os.path.join( 'data', 'SMSSpamCollection'),'r')
lines =textFile.readlines()
classArray = []
smsArray = []

for line in lines:
    classArray.append(line.split(None, 1)[0]) # add only first word
    smsArray.append((line.split(None,1))[1])  #add others as text



X = smsArray
y = classArray
