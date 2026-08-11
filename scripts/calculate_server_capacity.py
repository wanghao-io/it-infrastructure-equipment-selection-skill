#!/usr/bin/env python3
"""Simple server capacity estimation helper."""


def calculate(vm_count, avg_vcpu, avg_memory_gb, cpu_overcommit=3):
    cpu = vm_count * avg_vcpu / cpu_overcommit
    memory = vm_count * avg_memory_gb * 1.3
    return {"physical_cpu_cores": round(cpu), "memory_gb": round(memory)}


if __name__ == '__main__':
    print(calculate(20, 4, 16))
