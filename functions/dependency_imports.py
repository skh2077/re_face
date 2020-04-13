import ast
import csv
import json
import logging
import os
import random
import string
from collections import Counter
from collections.abc import Iterable
from datetime import date, datetime, timedelta
from itertools import chain

import numpy as np
import pandas as pd
import psycopg2
import requests
from dateutil.relativedelta import relativedelta
from django import forms
from django.contrib.auth.models import AbstractBaseUser
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.postgres.constraints import ExclusionConstraint
from django.contrib.postgres.fields import (ArrayField, IntegerRangeField,
                                            JSONField, RangeOperators)
from django.core.exceptions import *
from django.core.mail import EmailMessage
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import IntegrityError, connection, models, reset_queries
from django.db.models import CheckConstraint, F, Max, Q, Sum
from django.db.models.functions import TruncDay
from django.http import QueryDict
from django.utils.datastructures import MultiValueDict, MultiValueDictKeyError
from django.views.decorators.csrf import csrf_exempt
from openpyxl import load_workbook
from openpyxl.utils.cell import coordinate_from_string
from psycopg2.extras import NumericRange

import drf_extra_fields.fields as drf_extra
from dew.settings import CLOUD_ROOT, GOOGLE_API_KEY,BOOTPAY_APPLICATION_ID,BOOTPAY_PRIVATE_KEY,STORAGE_CLIENT,GS_BUCKET_NAME
from drf_braces.serializers.form_serializer import FormSerializer
from drf_extra_fields.fields import Base64ImageField
from drf_extra_fields.geo_fields import PointField
from gcloud import storage
from server_python.lib.BootpayApi import BootpayApi
from model_utils.managers import InheritanceManager
from phonenumber_field.modelfields import PhoneNumberField
from rest_framework import serializers
from rest_framework import status as Status
from rest_framework import viewsets
from rest_framework.decorators import action, api_view
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from rest_framework.views import APIView
from structlog import get_logger

from .non_dependency import *
