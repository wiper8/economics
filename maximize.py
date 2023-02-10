import math
from math import log
from classes import seq
#j'ai une fonction du style F(a,b,c)=f(a)+g(b)+h(c) que je veux maximiser

#exemple
#f(a)=5ln(a-h)
#g(b)=1ln(b-h)
#h(c)=0.8ln(c-h)
#i(d)=0.2ln(d-h)
#...

#avec 24h, 0<=b<=24/12, 0<=c<=24/8, 0<=d<=24/4, 0 <= 12b+8c+4d <= 24

#a b c et d sont les keys de bonheur dans Person
# b c et d sont les keys de bonheur sauf "temps"

#on utilise toujours tout notre 24h
#a=24-b*12-c*8-4d

#point initial a=24, b=0, c=0, d=0

#F=5ln(24-12b-8c-4d + 1) + 1ln(b + 1) + 0.8ln(c + 1) + 0.2ln(d+1)

#maximiser d'abord sur les frontières

#0=12b+8c+4d
#b=0, c=0, d=0
#F=5ln(24.01) + 1ln(1) + 0.8ln(1) + 0.2ln(1)
#F=

#ensuite 2e frontière
#24=12b+8c+4d
#12b=24-8c-4d
#F=5ln(1) + 1ln((24-8c-4d)/12 + 1) + 0.8ln(c + 1) + 0.2ln(d+1)
#dF/dc=1/((24-8c-4d)/12 + 1)*-8/12 + 0.8/(c+1)
#dF/dd...

#ensuite aucune frontière
#F=5ln(24-12b-8c-4d + 1) + 1ln(b + 1) + 0.8ln(c + 1) + 0.2ln(d+1)
#dF/db
#dF/dc
#dF/dd



def marginal_util_optim(prices, k, c, constrs, libre, p, n, consum):
    quantities = [0] * len(prices)
    marginal_util = [None] * len(prices)
    keep_considering = [True] * len(prices)

    if not constrs(prices, quantities, libre, p, n):
        raise(ValueError("Les inputs ne satisfont pas les contraintes"))
    while True:
        for i in range(len(prices)):
            if keep_considering[i]:
                if consum[i]:
                    marginal_util[i] = k[i] * math.log(c[i]) / c[i] ** quantities[i] / prices[i]
                else:
                    marginal_util[i] = k[i] * math.log(c[i]) / c[i] ** sum(quantities[(math.floor(i/n) * n):((math.floor(i/n)+1) * n)]) / prices[i]

        which=marginal_util.index(max(marginal_util))
        quantities[which] += 1

        if not constrs(prices, quantities, libre, p, n):
            quantities[which] -= 1
            marginal_util[which] = 0
            keep_considering[which] = False
        if not any(keep_considering):
            break

    return quantities


def optim(fun, x=0, min_it=100, max_it=10000):
    s=0
    r=0
    d=0
    i=1
    fact = 0.01
    sign = True
    while abs(d) > 0.01 or i <= min_it:
        if i > max_it:
            return None
        deriv = (fun(x+0.01) - fun(x))/0.01
        deriv_next = (fun(x - fact*deriv + 0.01) - fun(x - fact*deriv)) / 0.01
        if (deriv > 0) == (deriv_next>0):
            fact *= 1.2
        else:
            fact *= 0.5
        sign = (deriv>0)
        #s = 0.9 * s + fact * deriv
        d = fact * deriv
        x -= d
        x=max(x, 0.01)
        #s = 0.9 * s + 0.5 * deriv
        #r = 0.99 * r + 0.01 * deriv ** 2
        #s_hat = s/(1 - 0.999 ** i)
        #r_hat = r/(1 - 0.999 ** i)
        #d = 0.2 * s_hat / (r_hat ** 0.5 + 0.02)
        #x -= d
        i += 1

    return x


def solver(fun, vars, conditions=None, min_it=100, max_it=10000):
    if conditions is None:
        {"vars_low": [float("-inf")] * len(vars), "vars_up": [float("inf")] * len(vars), "other": None}
    keys = list(set(vars.keys()))
    s=dict.fromkeys(keys, 0)
    r = dict.fromkeys(keys, 0)
    d = dict.fromkeys(keys, 0)
    deriv = dict.fromkeys(keys, None)
    fact = dict.fromkeys(keys, 0.01)
    sign = dict.fromkeys(keys, True)
    restricted = dict.fromkeys(keys, False)
    i = 1
    #check initial si on commence avec les restrictions satisfaites
    for k in keys:
            if vars[k] < conditions["vars_low"][k] or vars[k] > conditions["vars_up"][k]:
                raise("out of domain for optimisation solver")
            conditions_ratees = [not cond(vars) for cond in conditions["other"]]
            if any(conditions_ratees):
                raise("out of domain for optimisation solver")


    while max([abs(d[k]) for k in keys]) > 0.001 or i <= min_it:
        if i > max_it:
            return None
        for k in keys:
            tmp_vars = vars.copy()
            if conditions["type"][k] == "int":
                tmp_vars[k] += 1
                deriv[k] = (fun(tmp_vars) - fun(vars))
                if (deriv[k] > 0) == sign[k]:
                    fact[k] = 1/deriv[k]
                else:
                    fact[k] = -1/deriv[k]
            else:
                tmp_vars[k] += 0.01
                deriv[k] = (fun(tmp_vars) - fun(vars))/0.01
                if (deriv[k] >= 0) == sign[k]:
                    fact[k] *= 1.2
                else:
                    fact[k] *= 0.5
                sign[k] = (deriv[k]>=0)
                d[k] = fact[k] * deriv[k]

        for k in keys:
            if not restricted[k]:
                vars[k] += d[k]
                if vars[k] < conditions["vars_low"][k] or vars[k] > conditions["vars_up"][k]:
                    vars[k] -= d[k]
                    continue
                conditions_ratees = [not cond(vars) for cond in conditions["other"]]
                if any(conditions_ratees):
                    vars[k] -= d[k]

        i += 1
    return vars



