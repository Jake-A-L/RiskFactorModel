import pandas as pd
import numpy as np

data_path = '../数据库/'

#%%
# from sqlalchemy import create_engine
#
# sqlEngine = create_engine('sqlite:///test.db')
# dbConnection = sqlEngine.connect()

#%% 从wind读取数据
database_wind = pd.read_excel(data_path +'万得/' + 'database_wind.xlsx')
database_wind.drop('Unnamed: 0', axis=1, inplace=True)
database_wind.set_index('DATE', inplace=True)

data_micro = pd.read_excel(data_path+'万得/' + 'data_micro.xls')

data_index = pd.read_excel(data_path+'万得/' + 'data_index.xlsx')

# database_wind.to_sql("database_wind", dbConnection, if_exists='replace')
# data_micro.to_sql("data_micro", dbConnection, if_exists='replace')

#%% 检查两表匹配度
miss_set = []
for i in range(data_micro.shape[0]):
    id = data_micro.loc[i, '指标ID']
    if id not in database_wind.columns:
        miss_set.append(id)
print('miss id in data_micro:', miss_set)

miss_set = []
for i in range(database_wind.shape[1]):
    id = database_wind.columns[i]
    if id not in data_micro['指标ID'].values:
        miss_set.append(id)
print('miss id database_wind:', miss_set)



#%% 因子成分
'''
增长：GPD,PMI，失业率，工业，宏观经济景气指数，产量, 克强指数
利率：SHIBOR,存款利率，国债， 货币乘数， 企业债， 活期存款
通胀：CPI, PPI, RPI
信用：企业债到期收益率-国债到期收益率，
流动性：M0,M1,M2, 社会融资规模， 公开市场操作，住宅价格指数（？）
对外贸易：进出口金额，即期汇率，出口金额
发达市场：美国CPI，美元指数
'''
data_construct = pd.read_excel(data_path+'万得/'+'construct.xlsx')
negative_set = ['城镇登记失业率', '城镇领取失业保险金人数', '工业企业:亏损企业亏损额:累计同比','企业债到期收益率(AA+):1年']
growth = None
rate = None
inflation = None
credit = None
liquid = None
export = None
oversea = None

def construct(factor):
    sub_factors = data_construct[factor].dropna().values
    sub_factors_code = [data_micro.loc[data_micro['指标名称']==sub, '指标ID'].values[0] for sub in sub_factors]
    return sub_factors, sub_factors_code



#%%

sub_factors, sub_factors_code = construct('增长')
factors_data = database_wind.loc['2009':, sub_factors_code]
factors_data = factors_data.resample('1M').last()
factors_data.fillna(method='ffill', inplace=True)

for sub_factor,sub_factor_code in zip(sub_factors,sub_factors_code):
    unit = data_micro.loc[data_micro['指标名称'] == sub_factor, '单位'].values[0]
    if unit != '%':
        print('环比')
        factors_data[sub_factor_code] = factors_data[sub_factor_code].diff(1)/factors_data[sub_factor_code].shift(1) * 100
    if sub_factor[:3] == 'PMI':
        factors_data[sub_factor_code] = factors_data[sub_factor_code]-50

    if sub_factor in negative_set:
        factors_data[sub_factor_code] = -factors_data[sub_factor_code]

factors_data = (factors_data-factors_data.mean(axis=0))/factors_data.std(axis=0)
factors_data['增长'] = factors_data.mean(axis=1)


