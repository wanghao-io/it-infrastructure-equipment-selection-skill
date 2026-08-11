#!/usr/bin/env python3

def usable_capacity(raw_tb, replica=2):
    return raw_tb / replica

if __name__ == '__main__':
    print(usable_capacity(20))
