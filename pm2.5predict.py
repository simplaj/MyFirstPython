import sys
import numpy as np
import pandas as pd
import csv

## 读入训练集
raw_data = np.genfromtxt('train.csv', delimiter=',') ## train.csv
data = raw_data[1:,3:]  ## 舍弃前一行和前三列
where_are_NaNs = np.isnan(data) ## 处理非数字字符
data[where_are_NaNs] = 0  ## 将非数字字符置为零

month_to_data = {}  ## Dictionary (key:month , value:data)                                  

for month in range(12):
    sample = np.empty(shape = (18 , 480))
    for day in range(20):
        for hour in range(24): 
            sample[:,day * 24 + hour] = data[18 * (month * 20 + day): 18 * (month * 20 + day + 1),hour]
    month_to_data[month] = sample 

## 预处理
x = np.empty(shape = (12 * 471 , 18 * 9),dtype = float)
y = np.empty(shape = (12 * 471 , 1),dtype = float)

for month in range(12): 
    for day in range(20): 
        for hour in range(24):   
            if day == 19 and hour > 14:
                continue  
            x[month * 471 + day * 24 + hour,:] = month_to_data[month][:,day * 24 + hour : day * 24 + hour + 9].reshape(1,-1) 
            y[month * 471 + day * 24 + hour,0] = month_to_data[month][9 ,day * 24 + hour + 9]

## 正常化
mean = np.mean(x, axis = 0) ## 压缩矩阵
std = np.std(x, axis = 0)
for i in range(x.shape[0]):
    for j in range(x.shape[1]):
        if not std[j] == 0 :
            x[i][j] = (x[i][j]- mean[j]) / std[j]


## 开始训练
dim = x.shape[1] + 1 
w = np.zeros(shape = (dim, 1 ))
x = np.concatenate((np.ones((x.shape[0], 1 )), x) , axis = 1).astype(float)
learning_rate = np.array([[200]] * dim)
adagrad_sum = np.zeros(shape = (dim, 1 ))
 
for T in range(10000):
    if(T % 500 == 0 ):
        print("T=",T)
        print("Loss:",np.power(np.sum(np.power(x.dot(w) - y, 2 ))/ x.shape[0],0.5))
    gradient = (-2) * np.transpose(x).dot(y-x.dot(w))
    adagrad_sum += gradient ** 2
    w = w - learning_rate * gradient / (np.sqrt(adagrad_sum) + 0.0005)

np.save('weight.npy',w)     ## save weight

## 读入测试集
w = np.load('weight.npy')                                   ## load weight
test_raw_data = np.genfromtxt('test.csv', delimiter=',')   ## test.csv
test_data = test_raw_data[:, 2: ]
where_are_NaNs = np.isnan(test_data)
test_data[where_are_NaNs] = 0 

## 预测
test_x = np.empty(shape = (240, 18 * 9),dtype = float)

for i in range(240):
    test_x[i,:] = test_data[18 * i : 18 * (i+1),:].reshape(1,-1) 

for i in range(test_x.shape[0]):        ##Normalization
    for j in range(test_x.shape[1]):
        if not std[j] == 0 :
            test_x[i][j] = (test_x[i][j]- mean[j]) / std[j]

test_x = np.concatenate((np.ones(shape = (test_x.shape[0],1)),test_x),axis = 1).astype(float)
answer = test_x.dot(w)

## 写出数据
f = open('out.csv',"w")
w = csv.writer(f)
title = ['id','value']
w.writerow(title) 
for i in range(240):
    content = ['id_'+str(i),answer[i][0]]
    w.writerow(content) 