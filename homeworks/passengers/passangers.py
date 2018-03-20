# -*- encoding: utf-8 -*-
import json
from glob import glob
from collections import OrderedDict
# from passangers import process

def process(data, events, car):
    trains_dict = OrderedDict()  # Ключи - буквы поездов, значения - массивы словарей (car_dict), в которых
    car_dict = OrderedDict()    # ключами являются номера вагонов, а значениями - количество пассажиров
    all_passengers = {} # Для хранения имен всех пассажиров и определения их поезда и вагона
    cars_list = OrderedDict() # Для итерации по вагонам

    for i in range(len(data)):  # Цикл по поездам data[i]
        trains_dict[data[i]['name']] = []
        cars_list[data[i]['name']] = []
        for j in range(len(data[i]['cars'])): # Цикл по вагонам data[i]['cars'][j]    
            car_dict[data[i]['cars'][j]['name']] = data[i]['cars'][j]['people']
            trains_dict[data[i]['name']].append({data[i]['cars'][j]['name']  : car_dict[data[i]['cars'][j]['name']]})
            cars_list[data[i]['name']].append(data[i]['cars'][j]['name'])
            for k in range(len(data[i]['cars'][j]['people'])):
                all_passengers[data[i]['cars'][j]['people'][k]] = [data[i]['name'], data[i]['cars'][j]['name']]

    for i in range(len(events)):
        if events[i]['type'] == "walk":
            # Проверяем, существует ли такой пассажир
            if events[i]['passenger'] not in all_passengers: 
                return -1
            passenger = events[i]['passenger']
            distance = events[i]['distance']
            train_number = all_passengers[passenger][0]
            car_number = all_passengers[passenger][1]
            index_in_cars = cars_list[train_number].index(car_number)
            #Проверяем, есть ли место для маневра:
            if distance > (len(cars_list[train_number]) - index_in_cars) or -distance > index_in_cars:  
                return -1
            # Удаляем элемент из старого вагона
            trains_dict[train_number][index_in_cars][car_number].remove(passenger)
            # Добавляем в новый
            new_car_number = cars_list[train_number][index_in_cars + distance]
            trains_dict[train_number][index_in_cars + distance][new_car_number].append(passenger)
            all_passengers[passenger][1] = new_car_number

        elif events[i]['type'] == "switch":
            # Проверяем, есть ли такие поезда
            if events[i]['train_from'] not in trains_dict or events[i]['train_to'] not in trains_dict:
                return -1 
            train_from = events[i]['train_from']
            train_to = events[i]['train_to']
            num_of_cars = events[i]['cars']
            # Проверяем, хватает ли вагонов для перемещения
            num = len(trains_dict[train_from]) # Количество вагонов в поезде
            if num_of_cars < 0:
                return - 1
            if num_of_cars > num:
                return - 1
            # Перемещаем вагоны
            for i in range(num - num_of_cars, num):
                trains_dict[train_to].append(trains_dict[train_from][num - num_of_cars])
                for _, peoples in trains_dict[train_from][num - num_of_cars].items():
                    for p in peoples:
                        all_passengers[p][0] = train_to
                cars_list[train_to].append(cars_list[train_from][num - num_of_cars])        
                del cars_list[train_from][num - num_of_cars]                
                del trains_dict[train_from][num - num_of_cars]

        else:
            return -1

    num = 0
    for train, cars in cars_list.items():
        if car in cars:
            index_in_cars = cars.index(car)
            return len(trains_dict[train][index_in_cars][car])             
