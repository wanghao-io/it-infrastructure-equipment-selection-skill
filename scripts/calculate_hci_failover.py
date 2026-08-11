#!/usr/bin/env python3

def check_n_plus_one(nodes, cpu_total, memory_total):
    if nodes < 3:
        return False
    remaining = nodes - 1
    return remaining * cpu_total / nodes >= cpu_total * 0.7 and remaining * memory_total / nodes >= memory_total * 0.7

if __name__ == '__main__':
    print(check_n_plus_one(3,100,512))
