import sqlalchemy as sa

INT_TYPE = sa.Integer()
LONG_STR_TYPE = sa.String(90)
SHORT_STR_TYPE = sa.String(30)
TEXT_TYPE = sa.Text()
DATETIME_TYPE = sa.DateTime(timezone=True)
ARRAY_TYPE = sa.ARRAY(sa.String(12))
