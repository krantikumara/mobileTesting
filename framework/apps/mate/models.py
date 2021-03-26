"""
This file defines the database models
"""

from .common import db, Field
from pydal.validators import *

### Define your table below
#
db.define_table('execution_results', Field('execution_id', type = 'string', unique = True),
                                     Field('execution_name', type = 'string'),
                                     Field('execution_data', type = 'json', length = 2**31))
                                     
db.define_table('execution_screenshots', Field('execution_id', type = 'string'),
                                     Field('screenshot', type = 'text'))

db.commit()

