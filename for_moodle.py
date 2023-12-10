import numpy as np
from kivy.app import App
from kivy.properties import ObjectProperty
from kivy.uix.screenmanager import ScreenManager,Screen
import sys
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
import pandas as pd

#Declare global variables year and semester.

class Manage(ScreenManager):

    '''
    Class for screenmanager that controls the screen appearance in the application.
    '''
    pass

class FormHazana(Screen):

    '''
    User Input form
    All references from KV file should come here.
    '''
    # Declare class variable for the student name.

    # Declare class variable for the student class.

    # Declare class variable for the student grade.

    def __init__(self,**kwargs):

        '''
        Initialize firebase
        :param kwargs:
        '''
        # Init the Screen class.

        # Path to the json file of the credentials.

        # Initialize fire base.

    def ktov(self):

        '''
        'Inserting user input to firebase'
        '''
        # Declare dictionary.

        # Insert name to dic.

        # Insert course to dic.

        # Insert grade to dic.

        # Declare reference to firebase.

        # Push the dictionary

        # Clear textinputs in the gui.

        # Set focus on student name.

        # Set spinner back to Mathematics.

    def out(self):

        '''
        'User close the application'
        :return:
        '''
        # Use sys.exit()

class ShowRecords(Screen):

    '''
    'Display query results to user'
    '''
    # Declare label of results for output.

    # To_do choose what event/method to use.
    def on______(self, *args):

        '''
        Event fired when the screen is displayed: the entering animation is complete.
        :param args:
        :return:
        '''
        # Clear label of results from previous data.

        # Set firebase reference to year and semester.

        # Flat json result using pandas json_normalize.

        # Make list of courses taking first item and every third item.

        # Make list of groups taking second item and every third item.

        # Make list of times taking third item and every third item.

        # Constract dataframe from lists.

        # Change the type of grade to int8

        # Change dataframe to records

        # Call show method with the records as parameter.

    def usrAvg(self):

        '''
        Finds for each user her mean grade using pandas.
        :return:
        '''
        # Find user ave

        # Turn result to records.

        # Call show method with the records as parameter.

    def cntUsrs(self):

        '''
        Finds number of students in each course.
        :return:
        '''
        # Finds number of students in each course and make a dataframe from result.

        # Turn result to records.

        # Call show method with the records as parameter.

    def genius(self):

        '''
        Finds the best student in Mathematics.
        :return:
        '''
        # Create dataframe of math course only.

        # Finds the record with has the highest grade.

        # Call show method with the record as parameter.

    def show(self,rows):

        '''
        'Show all query results on screen'
        '''
        # Clear result label in the gui.

        # If rows has no records

            # Inform user that there are no records

        # Else

            # For each row

                # If row has 3 words

                    # Show to user

                # If row has 2 words

                    # Show user with the number round to 2 decimal places

class FbApp(App):

