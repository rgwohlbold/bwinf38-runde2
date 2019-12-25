import sys
import math
from collections import defaultdict
from itertools import combinations_with_replacement
from queue import Queue

class Term(object):

    def __init__(self):
       pass 

    def number_of_digits(self):
        return NotImplementedError()
    
    def value(self):
        return NotImplementedError()
    
    def __str__(self):
        return NotImplementedError()

    def __repr__(self):
        return str(self)


class Number(Term):

    def __init__(self, val):
        self.val = val
    
    def value(self):
        return self.val
    
    def number_of_digits(self):
        return len(str(self.val))
    
    def __str__(self):
        return str(self.val)

class BinaryOperation(Term):

    OP_ADD = 0
    OP_SUB = 1
    OP_MULT = 2
    OP_DIV = 3
    OPERATIONS = [OP_ADD, OP_SUB, OP_MULT, OP_DIV]

    def __init__(self, val1, val2, op):
        assert op in self.__class__.OPERATIONS
        self.val1 = val1
        self.val2 = val2
        self.op = op

    def value(self):
        if self.op == BinaryOperation.OP_ADD:
            return self.val1.value() + self.val2.value()
        elif self.op == BinaryOperation.OP_SUB:
            return self.val1.value() - self.val2.value()
        elif self.op == BinaryOperation.OP_MULT:
            return self.val1.value() * self.val2.value()
        elif self.op == BinaryOperation.OP_DIV:
            v1 = self.val1.value()
            v2 = self.val2.value()
            res = v1/v2
            resint = int(res)
            assert res == resint
            return resint
        return NotImplementedError()

    def number_of_digits(self):
        return self.val1.number_of_digits() + self.val2.number_of_digits()
    
    def __str__(self):
        return '({}{}{})'.format(str(self.val1), self.opchar(), str(self.val2))
    
    def opchar(self):
        if self.op == BinaryOperation.OP_ADD:
            return '+'
        elif self.op == BinaryOperation.OP_SUB:
            return '-'
        elif self.op == BinaryOperation.OP_MULT:
            return '*'
        elif self.op == BinaryOperation.OP_DIV:
            return '/'
        return NotImplementedError()
        

AGGREGATED_TABLE = {}
TABLE_SPLIT = defaultdict(dict)

def add_to_table(term, table=AGGREGATED_TABLE):
    val = term.value()
    digits = term.number_of_digits()
    if val in table and table[val][1] < digits:
        return
    table[val] = (term, digits)



def generate(digit, num_digits):

    current_split_table = TABLE_SPLIT[num_digits]        

    # Add 3, 33, 333 etc
    num = int(str(digit)*num_digits)
    current_split_table[num] = (Number(num), num_digits)
    swap = False

    for op1_num_digits in range(1, num_digits // 2 + 1):
        op2_num_digits = num_digits - op1_num_digits
        for op1_k in TABLE_SPLIT[op1_num_digits]:
            op1_v = TABLE_SPLIT[op1_num_digits][op1_k][0]
            for op2_k in TABLE_SPLIT[op2_num_digits]:
                op2_v = TABLE_SPLIT[op2_num_digits][op2_k][0]
                # Make sure that op1_k > op2_k
                if op1_k < op2_k:
                    op1_k, op2_k = op2_k, op1_k
                    op1_v, op2_v = op2_v, op1_v
                    swap = True


                add_to_table(BinaryOperation(op1_v, op2_v, BinaryOperation.OP_ADD), current_split_table)
                add_to_table(BinaryOperation(op1_v, op2_v, BinaryOperation.OP_SUB), current_split_table)
                add_to_table(BinaryOperation(op2_v, op1_v, BinaryOperation.OP_SUB), current_split_table)
                add_to_table(BinaryOperation(op1_v, op2_v, BinaryOperation.OP_MULT), current_split_table)

                if op2_k != 0:
                    res = op1_k / op2_k
                    resint = int(res)
                    if res == resint:
                        add_to_table(BinaryOperation(op1_v, op2_v, BinaryOperation.OP_DIV), current_split_table)

                if swap:
                    op1_k, op2_k = op2_k, op1_k
                    op1_v, op2_v = op2_v, op1_v
                    swap = False
    print("generated", num_digits)

    for k in TABLE_SPLIT[num_digits]:
        if k not in AGGREGATED_TABLE:
            AGGREGATED_TABLE[k] = TABLE_SPLIT[num_digits][k]

def scan(number, digit):

    results = set()
    if number in AGGREGATED_TABLE:
        results.add(AGGREGATED_TABLE[number][0])

    for j in AGGREGATED_TABLE:
        if number - j in AGGREGATED_TABLE:
            results.add(BinaryOperation(AGGREGATED_TABLE[j][0], AGGREGATED_TABLE[number-j][0], BinaryOperation.OP_ADD))
        if number + j in AGGREGATED_TABLE:
            results.add(BinaryOperation(AGGREGATED_TABLE[number+j][0], AGGREGATED_TABLE[j][0], BinaryOperation.OP_SUB))
        if j - number in AGGREGATED_TABLE:
            results.add(BinaryOperation(AGGREGATED_TABLE[j][0], AGGREGATED_TABLE[j-number][0], BinaryOperation.OP_SUB))
        
        if j != 0:
            if (number*j) in AGGREGATED_TABLE:
                results.add(BinaryOperation(AGGREGATED_TABLE[number*j][0], AGGREGATED_TABLE[j][0], BinaryOperation.OP_DIV))
            
            res = j / number
            resint = int(res)
            if res == resint and resint in AGGREGATED_TABLE:
                results.add(BinaryOperation(AGGREGATED_TABLE[j][0], AGGREGATED_TABLE[resint][0], BinaryOperation.OP_DIV))
        
            res = number / j
            resint = int(res)
            if res == resint and resint in AGGREGATED_TABLE:
                results.add(BinaryOperation(AGGREGATED_TABLE[number/j][0], AGGREGATED_TABLE[j][0], BinaryOperation.OP_MULT))
    if len(results) == 0:
        return None
    res = 0
    n = math.inf
    for r in results:
        nr = r.number_of_digits()
        if nr < n:
            res = r
            n = nr
    return res





if __name__ == '__main__':
    assert len(sys.argv) >= 3

    number = int(sys.argv[1])

    digit = int(sys.argv[2])
    assert len(str(digit)) == 1 and digit > 0

    i = 1
    res_n = math.inf
    while i <= res_n - 2:
        generate(digit, i)
        res = scan(number, digit)
        if res is not None:
            res_n = res.number_of_digits()
            print("found", res, "with", res.number_of_digits(), "digits, looking if shorter is possible")
        i += 1

    print()
    print("result", res)
    print("digits:", res.number_of_digits())


