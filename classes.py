import math

from plotnine import ggplot, geom_col, theme_bw, aes
from math import log

def seq(from_, to, step=1):
    assert to >= from_
    sequence = []
    sequence.append(from_)

    while sequence[-1] + step <= to:
        sequence.append(sequence[-1] + step)

    return sequence

def mean(x):
    assert len(x)>0
    y=0
    for u in x:
        y += u
    return y/len(x)


##################
class Stock:
    def __init__(self, ticker, quantity):
        self.ticker = ticker
        self.quantity = quantity

    def __repr__(self):
        return f'{self.quantity}'

class Bond:
    def __init__(self, duration, rate, quantity):
        self.duration = duration
        self.rate = rate
        self.quantity = quantity

class Exchange:
    def __init__(self):
        self.markets = dict()
        self.entities = dict()

    def add_market(self, ticker, book):
        self.markets[ticker] = book

    def add_entity(self, entity):
        self.entities[entity.id] = entity

    def execute(self, expire=False, flush=False):
        #les ordres durent 2 jours
        for biens in list(self.markets.keys()):

            p, Q = self.markets[biens].equilibrium()

            if Q > 0:
                for i in range(Q):
                    if biens in self.entities[self.markets[biens].sells[i][0]].biens.keys():

                        if self.entities[self.markets[biens].buys[i][0]].money >= p and self.entities[self.markets[biens].sells[i][0]].biens[biens] >= 1:
                            #la transaction peut avoir lieu
                            self.entities[self.markets[biens].buys[i][0]].money -= p
                            self.entities[self.markets[biens].sells[i][0]].biens[biens] -= 1

                            if biens not in self.entities[self.markets[biens].buys[i][0]].biens.keys():
                                self.entities[self.markets[biens].buys[i][0]].biens[biens] = 1
                            else:
                                self.entities[self.markets[biens].buys[i][0]].biens[biens] += 1

                            self.entities[self.markets[biens].sells[i][0]].money += p

                            self.markets[biens].buys[i][2] = True
                            self.markets[biens].sells[i][2] = True

        #effacer les ordres sur le marché
        if flush:
            self.flush_orders()
        if expire:
            self.expire_orders()


    def expire_orders(self):
        for bien in list(self.markets.keys()):
            for ordre in self.markets[bien].buys:
                ordre[3] = True

            for ordre in self.markets[bien].sells:
                ordre[3] = True

    def flush_orders(self):
        for bien in list(self.markets.keys()):
            self.markets[bien].buys = [ordre for ordre in self.markets[bien].buys if not ordre[2] and not ordre[3]]
            self.markets[bien].sells = [ordre for ordre in self.markets[bien].sells if not ordre[2] and not ordre[3]]

    def __str__(self):
        return f'{list(self.markets.keys())}\nParticipants : {len(self.entities)}'


class Person:
    def __init__(self, id, travail_level=0, best="manuel", money = 0, biens = {}, utility_fun = {}, alpha=1):
        self.id = id
        self.money = money
        self.travail_level = travail_level
        self.best = best
        self.stocks = {}
        self.biens = biens.copy()
        self.utility_fun = utility_fun.copy()
        self.alpha = alpha
        self.utility = 0
        self.biens[str("Travail")] = 24

    def order(self, exchange, ticker, quantity, limit="at market", buy=True):
        exchange.markets[ticker].add_order(self.id, quantity, limit, buy)

    def consume(self):
        self.utility = 0
        for k in list(set(self.utility_fun.keys())-set("Travail")):
            if k in self.biens.keys():
                self.utility += self.utility_fun[k]["k"] * (1 - self.utility_fun[k]["c"] ** (-self.biens[k]))
                if self.utility_fun[k]["consommer"]:
                    self.biens[k] = 0
        self.utility += self.utility_fun["temps libre"]["k"] * (1 - self.utility_fun["temps libre"]["c"] ** (-self.biens["Travail"]))
        if self.utility_fun["temps libre"]["consommer"]:
            self.biens["Travail"] = 0


    def new_day(self):
        self.biens["Travail"] = 24

    def __str__(self):
        return f'ID : {self.id}\nMoney : {self.money:.2f}\nStocks : {self.stocks}'

class Compagnie:
    def __init__(self, id, production, ticker, money=100, shareholders={}):
        self.id = id
        self.production = production
        self.biens = {production : 0}
        self.ticker = ticker
        self.shareholders = shareholders.copy()
        self.nshares = sum(self.shareholders.values())
        self.money = money
        self.money_debut_jour  = self.money

    def order(self, exchange, ticker, quantity, limit="at market", buy=True):
        exchange.markets[ticker].add_order(self.id, quantity, limit, buy)

    def new_day(self):
        self.money_debut_jour = self.money

    def __str__(self):
        return f'ID : {self.id}\nProduit : {self.biens}\nTicker : {self.ticker}\nMoney : {self.money:.2f}'


class Gov:
    def __init__(self):
        self.money=0
        self.bonds=[]

class Fed:
    def __init__(self):
        self.bonds = []
        self.rate = 0

class Market:
    def __init__(self, last_price=None):
        self.buys = []
        self.sells = []
        self.last_price = last_price

    def equilibrium(self):

        nbuys = len(self.buys)
        nsells = len(self.sells)

        buy_prices = [self.buys[i][1] for i in range(nbuys)]
        sell_prices = [self.sells[i][1] for i in range(nsells)]
        buy_prices.sort(reverse=True)
        sell_prices.sort()

        if nbuys == 0 and nsells == 0:
            return self.last_price, 0

        elif nbuys > 0 and nsells > 0:
            Q = 0
            while Q <= nbuys - 1 and Q <= nsells - 1 and buy_prices[Q] >= sell_prices[Q]:
                Q += 1

            if Q != 0:
                self.last_price = max(0.01, round((buy_prices[Q-1] + sell_prices[Q-1])/2, ndigits=2))
            else:
                self.last_price = max(0.01, round((buy_prices[0] + sell_prices[0]) / 2, ndigits=2))
            return self.last_price, Q

        elif nsells == 0:
            self.last_price = max(0.01, round(max(buy_prices), ndigits=2))
            return None, 0
        else:
            self.last_price = max(0.01, round(min(sell_prices), ndigits=2))
            return None, 0



    def add_order(self, id, quantity, limit, buy):
        if limit == "at market":
            limit, Q = self.equilibrium()

        if buy:
            #id, prix limite, exécuté, expiré
            self.buys += [[id, limit, False, False]] * quantity
            self.buys.sort(key=lambda tup: tup[1], reverse=True)
        else:
            self.sells += [[id, limit, False, False]] * quantity
            self.sells.sort(key=lambda tup: tup[1])

    def deriv(self, liste): #liste commence à Q=1 et le return commence à Q=2
        if len(liste) < 2:
            raise(ValueError("l'argument liste doit être au moins 2 de long"))
        return [liste[i+1]-liste[i] for i in range(len(liste)-1)]

    def find_price(self, Q):
        if Q == 0:
            return math.inf
        else:
            return self.buys[Q-1][1]

    def recettes(self): #débute à Q=1
        return [self.buys[i][1] * (i+1) for i in range(len(self.buys))]

    def recettes_marginales(self): #débute à Q=1
        recet = self.recettes()
        ret=[]
        if len(recet) >= 2:
            ret.extend(self.deriv(self.recettes()))
        ret.append(0)
        return ret

    def elasticity(self, demand=True):
        if demand:
            if len(self.buys) > 1:
                elas = mean([(self.buys[i][1] + self.buys[i+1][1])/(self.buys[i][1] - self.buys[i+1][1])/((2*i+3)/2) for i in range(len(self.buys)-1)])
                if elas < 0.1:
                    return f'perfectly inelastic demand'
                elif elas < 0.5:
                    return f'very inelastic demand'
                elif elas < 1/1.1:
                    return f'Inelastic demand'
                elif elas < 1.1:
                    return f'unit elastic demand'
                elif elas < 2:
                    return f'elastic demand'
                elif elas < 10:
                    return f'very elastic demand'
                else:
                    return f'perfectly elastic demand'
            else:
                return None
        else:
            if len(self.sells) > 1:
                elas = mean([(self.sells[i][1] + self.sells[i+1][1])/(self.sells[i+1][1] - self.sells[i][1])/((2*i+3)/2) for i in range(len(self.sells)-1)])
                if elas < 0.1:
                    return f'perfectly inelastic supply'
                elif elas < 0.5:
                    return f'very inelastic supply'
                elif elas < 1/1.1:
                    return f'Inelastic supply'
                elif elas < 1.1:
                    return f'unit elastic supply'
                elif elas > 5:
                    return f'elastic supply'
                elif elas > 10:
                    return f'very elastic supply'
                else:
                    return f'perfectly elastic supply'
            else:
                return None

    def plot(self):
        self.equilibrium()
        graph = ggplot()
        buy_price_tuples = [buy_price_tuple[1] for buy_price_tuple in self.buys]
        sell_price_tuples = [sell_price_tuple[1] for sell_price_tuple in self.sells]

        if len(buy_price_tuples) >= 1:
            graph += geom_col(aes(x=seq(1, len(buy_price_tuples)), y=buy_price_tuples), fill="green", alpha=0.5)

        if len(sell_price_tuples) >= 1:
            graph += geom_col(aes(x=seq(1, len(sell_price_tuples)), y=sell_price_tuples), fill="red", alpha=0.5)

        graph += theme_bw()
        print(graph)

    def __str__(self):
        return f'buys orders : {len(self.buys)}\nsells orders : {len(self.sells)}'
