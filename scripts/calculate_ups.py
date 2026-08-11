#!/usr/bin/env python3

def ups_rating(load_kw, margin=1.3):
    return load_kw * margin

if __name__ == '__main__':
    print(ups_rating(5))
