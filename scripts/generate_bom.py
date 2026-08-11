#!/usr/bin/env python3
import csv


def generate(items, filename='bom.csv'):
    with open(filename,'w',newline='',encoding='utf-8') as f:
        writer=csv.DictWriter(f, fieldnames=items[0].keys())
        writer.writeheader()
        writer.writerows(items)

if __name__ == '__main__':
    generate([{'name':'example','qty':1}])
