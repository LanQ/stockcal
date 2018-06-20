# -*- coding: utf-8 -*-
from flask import Flask
from flask import render_template
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired

import tushare as ts
import pandas as pd

app = Flask(__name__)
app.config['SECRET_KEY'] = 'hard to guess string'

class MyForm(FlaskForm):
    code = StringField(u'代码', validators=[DataRequired()])
    submit = SubmitField(u'提交')

@app.route('/', methods=['GET', 'POST'])
def index():
	code = None
	form = MyForm()
	code_list = []
	record = pd.DataFrame()
	records = pd.DataFrame()
	result = None

	if form.validate_on_submit():
		code_list = form.code.data.split(',')
		form.code.data = ''
		
		for code in code_list:
			try:
				record = ts.get_k_data(code, ktype='W', start='2015-05-01')
								
				record_decr = record.describe()
				record_decr_filter = record_decr.loc[['mean', 'min', 'max', 'low']]
				
				record_custom = pd.Series([code,\
				float(record[-1:]['close'].values),\
				record_decr_filter.loc['mean', 'high'],\
				record_decr_filter.loc['mean', 'low'],\
				record_decr_filter.loc['max', 'high'],\
				record_decr_filter.loc['min', 'high'],\
				record_decr_filter.loc['min', 'low'],\
				],\
				index=\
				['code',\
				'close',\
				'high_mean',\
				'low_mean',\
				'high_max',\
				'high_min',\
				'low_min'])
				
				record_custom['close_low_mean_pct'] = (record_custom['close']-record_custom['low_mean']) / record_custom['low_mean']
				
				
				#if no NAN value in dataframe
				if (record_custom.isnull().values.any() == False):
					records = records.append(record_custom, ignore_index=True)
				else:
					print '%s has NaN value, skip it.' % (code)			

			except Exception as e:
				print code, e
		##app.logger.info(record_decr_filter)
		result = records.to_html()
	return render_template('stock_data.html', code=code_list, form=form, result=result)
