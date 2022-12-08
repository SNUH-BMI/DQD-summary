#!/usr/bin/env python
# coding: utf-8

# In[179]:


import json
import csv
import pandas as pd
import os


# In[180]:


# 파일 읽기 (현재 경로에 있는 json 파일)
_file = os.listdir(os.getcwd())
json_list = list()
for f in _file:
    if '.json' in f:
        json_list.append(f)

if len(json_list) == 0:
    raise Exception("json file is not existed.")
elif len(json_list) == 1:
    json_file = json_list[0]
else:
    for i in range(len(json_list)):
        print(str(i+1)+":", json_list[i])
    select = int(input("읽을 파일의 번호를 입력하세요: "))
    json_file = json_list[select-1]

print(json_file, "is read.")


# In[181]:


# check_result 불러오기
with open(json_file) as json_data:
    data = json.load(json_data)

keys= list(data.keys())
values = list(data.values())

# check_Results
checkresults = values[3] # 딕셔너리로 이루어진 리스트

# 레코드 데이터프레임
result_df = pd.DataFrame(checkresults)
print(len(result_df))

# Error 제거
#result_df = result_df[pd.isna(result_df['ERROR'])]
#print(len(result_df))

# Denom = 0 제거
result_df = result_df[result_df['NUM_DENOMINATOR_ROWS']!=0]
print(len(result_df))


# In[182]:


# metadata 불러오기
metadata = values[4][0]
SOURCE_DESCRIPTION = metadata['SOURCE_DESCRIPTION']
CDM_VERSION = metadata['CDM_VERSION']
DQD_VERSION = metadata['DQD_VERSION']

# time 불러오기
execution_time = values[2][0]
start_time = values[1][0]


# In[183]:


context = ['Verification', 'Validation','Total']
category = ['Plausibility', 'Conformance', 'Completeness','Total']


# In[184]:


data = dict()
for con in context:
    for cat in category:
        if con == 'Total' and cat == 'Total':
            data[(con,cat)] = result_df
        if con == 'Total' and cat != 'Total':
            data[(con,cat)] = result_df[(result_df['CATEGORY'] == cat)]
        if con != 'Total' and cat == 'Total':
            data[(con,cat)] = result_df[(result_df['CONTEXT'] == con)]
        if con != 'Total' and cat != 'Total':
            data[(con,cat)] = result_df[(result_df['CONTEXT'] == con) & (result_df['CATEGORY'] == cat)]     


# In[185]:


table_data = dict()

# 원래 양식을 써보자.
dqd_html_filename = 'html.txt'
file = open(dqd_html_filename)
dqd_html = file.read()

for key in data:
    con, cat = key
    result = data[key]
    _total = len(result)
    _pass = len(result[result['FAILED'] == 0])
    _fail = len(result[result['FAILED'] == 1])
    
    if _total == 0:
        _percent_pass = "0%"
    else:
        _percent_pass = str(round(_pass / _total * 100))+"%"
        
        keywords = ['Pass','Fail','Total','% Pass']
        for keyword in keywords:    
            if not((con, keyword) in table_data):
                table_data[(con,keyword)] = list()
                
                
                
        table_data[(con,'Pass')].append(_pass)
        table_data[(con,'Fail')].append(_fail)
        table_data[(con,'Total')].append(_total)
        table_data[(con,'% Pass')].append(_percent_pass)
        
        # Pass, Fail, Total, PercentPass 채우기
        text = "{{"+con+"."+cat+"."+"Pass"+"}}"
        dqd_html = dqd_html.replace(text,str(_pass))
        text = "{{"+con+"."+cat+"."+"Fail"+"}}"
        dqd_html = dqd_html.replace(text,str(_fail))
        text = "{{"+con+"."+cat+"."+"Total"+"}}"
        dqd_html = dqd_html.replace(text,str(_total))
        text = "{{"+con+"."+cat+"."+"PercentPass"+"}}"
        dqd_html = dqd_html.replace(text,str(_percent_pass))
        
        # fail 0이 아니면 빨간색으로 바꾸기
        if _fail != 0:
            text = "{{#if "+con+"."+cat+"."+"Fail"+"}}"+'class="fail"{{/if}}'
            #style = "style = color: #C00; font-weight:bold;"
            style = 'class="fail"'
            dqd_html = dqd_html.replace(text,style)
            


# In[186]:


# 텍스트 대체
text = "{{"+"SOURCE_DESCRIPTION"+"}}"
dqd_html = dqd_html.replace(text,str(SOURCE_DESCRIPTION))

text = "{{"+"CDM_VERSION"+"}}"
dqd_html = dqd_html.replace(text,str(CDM_VERSION))

text = "{{"+"execution_time"+"}}"
dqd_html = dqd_html.replace(text,str(execution_time))

text = "{{"+"start_time"+"}}"
dqd_html = dqd_html.replace(text,str(start_time))


# In[187]:


table = pd.DataFrame(table_data, index = category)


# In[188]:


# 저장할 파일 이름
html_filename = json_file[:-5] + ".html"

# html 저장
f = open(html_filename,'w')
f.write(dqd_html)
f.close()

#html_filename2 = html_filename[:-5] + "_raw.html"
#table.to_html(html_filename2)


# In[189]:


# 파일 실행
os.system(html_filename)


# In[ ]:




