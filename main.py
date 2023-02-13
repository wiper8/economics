import random
from math import log as ln, floor
from classes import *
from maximize import solver, optim, marginal_util_optim
from plotnine import ggplot, geom_col, geom_line, geom_text, ggtitle, theme_bw, aes, ylim
import re
import numpy as np
###############

propensity_saving = 0 # peut être >1 ou <1 dépendant de si quelquun préfère conserver son cash ou dépenser

#Créer les recettes des biens
recettes = {
    "pain":[{"Travail":24}],
    "cereales":[{"Travail":20}],
    "eau":[{"Travail":8}],
    "jus":[{"Travail":13}]
}


biens_consommables = ["Travail", "pain", "cereales", "eau", "jus"]

n_people = 10


people = {}
for i in range(n_people):
    c1_pain = max(1.001, 1.7+np.random.normal(scale=0.1))
    c1_cere = max(1.001, 1.6 + np.random.normal(scale=0.1))
    c1_eau = max(1.001, 1.1 + np.random.normal(scale=0.1))
    c1_jus = max(1.001, 1.2 + np.random.normal(scale=0.1))

    people["P"+str(i)] = Person("P"+str(i), random.choice(["pain", "cereales", "eau", "jus"]), money = 5, utility_fun = {
        "temps libre":{"k":max(0.1, 1+np.random.normal(scale=0.1)), "c1":max(1.001, 1.2+np.random.normal(scale=0.1)), "c2":1.00000000001, "consommer":True},
        "pain":{"k":max(0.1, 2.5+np.random.normal(scale=0.1)), "c1":c1_pain, "c2":np.random.uniform(1.001, c1_pain), "consommer":True},
        "cereales":{"k":max(0.1, 2+np.random.normal(scale=0.1)), "c1":c1_cere, "c2":np.random.uniform(1.001, c1_cere), "consommer":True},
        "eau":{"k":max(0.1, 1.8+np.random.normal(scale=0.1)), "c1":c1_eau, "c2":np.random.uniform(1.001, c1_eau), "consommer":True},
        "jus":{"k":max(0.1, 4+np.random.normal(scale=0.1)), "c1":c1_jus, "c2":np.random.uniform(1.001, c1_jus), "consommer":True}},
                                        propensity_saving=propensity_saving)
sorted(people.keys())


exchange = Exchange()
#préparer les personnes et les prix initiaux du marchés pour qu'ils puissent préparer leurs offres
for p in people.values():
    exchange.add_entity(p)

for b in recettes.keys():
    exchange.add_market(b, Market(last_price=1))

def constrs(price, quantities, libre, p, n):
    moneys = [None] * (n+1)
    moneys[0] = p.money
    moneys[1] = moneys[0] - sum([price[j] * quantities[j] for j in seq(0, len(libre)-n, n)])
    if n>1:
        for i in seq(2, n):
            id=seq(i - 1, len(libre) - n, n)
            id.append(i - 1 + len(libre) - n)
            moneys[i] = moneys[i-1] - sum([price[j] * quantities[j] if not libre[j] else -(24-quantities[j]) * price[j] for j in id])
    for i in range(len(libre)):
        if libre[i]:
            if quantities[i] > 24:
                return False

    for money in moneys:
        if money<0:
            return False
    return True


n = 3 #days_to_forcast_utility >=1
days=50

money_distribution = [None] * (days+1)
biens_prix = [None] * (days+1)
utility = [None] * (days+1)

money_distribution[0] = {}
biens_prix[0] = {}
utility[0] = {}

for p in people.values():
    money_distribution[0][p.id] = p.money
    utility[0][p.id] = p.utility
for b in list(exchange.markets.keys()):
    biens_prix[0][b] = exchange.markets[b].last_price


for day in range(days):
    print(f'Day : {day}')
    exchange.execute(True, True)

    #redonner 24h a tout le monde
    for p in people.values():
        p.new_day()

    ###people
    for p in people.values():
        # déterminer la demande des biens et services
        for bien in list(set(p.utility_fun.keys())-set(["temps libre"])):

            if p.money > 0:

                biens = [bien]
                biens.extend(list(set(p.utility_fun.keys()) - set(["temps libre", bien])))

                k = []
                for b in biens:
                    for i in range(n):
                        k.append(p.utility_fun[b]["k"] * propensity_saving ** i)
                if n > 1:
                    for i in range(n - 1):
                        k.append(p.utility_fun["temps libre"]["k"] * propensity_saving ** i)

                c1 = []
                for b in biens:
                    for i in range(n):
                        c1.append(p.utility_fun[b]["c1"])
                if n > 1:
                    for i in range(n - 1):
                        c1.append(p.utility_fun["temps libre"]["c1"])
                c2 = []
                for b in biens:
                    for i in range(n):
                        c2.append(p.utility_fun[b]["c2"])
                if n > 1:
                    for i in range(n - 1):
                        c2.append(p.utility_fun["temps libre"]["c2"])
                consum = []
                for b in biens:
                    for i in range(n):
                        consum.append(p.utility_fun[b]["consommer"])
                if n > 1:
                    for i in range(n - 1):
                        consum.append(p.utility_fun["temps libre"]["consommer"])
                libre = [False] * (n * len(biens))

                if n > 1:
                    for i in range(n - 1):
                        libre.append(True)

                quantite_avant = 0
                for prix in np.linspace(p.money, 0.01, 50):

                    prices = [prix] * n
                    for b in biens[1:]:
                        for i in range(n):
                            prices.append(exchange.markets[b].last_price)
                    if n > 1:
                        for i in range(n - 1):
                            prices.append(exchange.markets[p.metier].last_price)

                    quantities = marginal_util_optim(prices, k, c1, c2, constrs, libre, p, n, consum)

                    quant = quantities[biens.index(bien) * n] - quantite_avant
                    if quant > 0:
                        exchange.entities[p.id].order(exchange, bien, quant, limit=prix, buy=True)
                    quantite_avant = quant


    #acheter les ressources le matin
    exchange.execute(False, True)


    ### demander ressources
    for p in people.values():
        # commence à Q=0 jusqu'au max de la demande
        cout_total = [0] * (len(exchange.markets[p.metier].buys) + 1)
        # commence à 0
        profit = [0] * len(cout_total)

        if (len(cout_total) > 1):
            for ressource in list(set(recettes[p.metier][0].keys()) - set(["Travail"])):
                if ressource in list(p.biens.keys()):
                    for Q in seq(1, len(cout_total) - 1):
                        cout_total[Q] += max(0, Q * recettes[p.metier][0][ressource] - p.biens[ressource]) * \
                                         exchange.markets[ressource].last_price
                else:
                    cout_par_unit = recettes[p.metier][0][ressource] * exchange.markets[
                        ressource].last_price
                    # maximiser le profit
                    for Q in seq(1, len(cout_total) - 1):
                        cout_total[Q] += Q * cout_par_unit

            for Q in seq(1, len(cout_total) - 1):
                profit[Q] = exchange.markets[p.metier].buys[Q - 1][1] * Q - cout_total[Q]

            Q = profit.index(max(profit))

            if profit[Q] > 0 and Q > 0:
                if p.money > 0:
                    for ress in list(set(recettes[p.metier][0].keys()) - set(["Travail"])):
                        if ress in list(p.biens.keys()):
                            if p.biens[ress] < math.ceil(Q * recettes[p.metier][0][ress]):
                                for Q_ress in seq(1,
                                                  math.ceil(Q * recettes[p.metier][0][ress]) - p.biens[ress]):
                                    # TODO probablement pas optimal car est la limite pour un profit de 0
                                    demande = min(p.money,
                                                  (profit[Q] + exchange.markets[ress].last_price *
                                                   Q_ress)) / Q_ress
                                    if demande > 0:
                                        exchange.entities[inc.id].order(exchange, ress, 1, limit=demande, buy=True)
                                    else:
                                        break

                        else:
                            for Q_ress in seq(1, math.ceil(Q * recettes[p.metier][0][ress])):
                                # TODO probablement pas optimal car est la limite pour un profit de 0
                                demande = min(p.money,
                                              (profit[Q] + exchange.markets[ress].last_price *
                                                            Q_ress)) / Q_ress
                                if demande > 0:
                                    exchange.entities[p.id].order(exchange, ress, 1, limit=demande, buy=True)
                                else:
                                    break

    # acheter les ressources le matin
    exchange.execute(False, True)

    #créer les biens
    for p in people.values():
        prod=math.inf
        for ingredient in list(recettes[p.metier][0].keys()):
            if ingredient not in list(p.biens.keys()):
                prod = 0
            else:
                prod = min(prod, floor(p.biens[ingredient] / recettes[p.metier][0][ingredient]))
        if prod > 0:
            for ingredient in list(recettes[p.metier][0].keys()):
                if ingredient in biens_consommables:
                    p.biens[ingredient] -= prod * recettes[p.metier][0][ingredient]

            p.biens[p.metier] += prod

            #mettre en vente
            exchange.entities[p.id].order(exchange, p.metier, prod,
                                          limit=exchange.markets[p.metier].buys[prod - 1][1], buy=False)


    #transiger
    exchange.execute(False, True)

    #consommer (faire disparaitre une partie des biens
    for p in people.values():
        p.consume()

    money_distribution[day + 1] = {}
    biens_prix[day + 1] = {}
    utility[day + 1] = {}
    for p in people.values():
        money_distribution[day+1][p.id] = p.money
        utility[day+1][p.id] = p.utility
    for b in list(exchange.markets.keys()):
        biens_prix[day+1][b] = exchange.markets[b].last_price



graph_money = ggplot()+ggtitle("Argent des individus selon le temps")
max_y = 0
for p in people.values():
    max_y = max(max_y, max([money_distribution[i][p.id] for i in seq(0, days)]))
    graph_money += geom_line(aes(x=seq(0, days), y=[money_distribution[i][p.id] for i in seq(0, days)]), color="green", alpha=0.5)
    graph_money += geom_text(aes(x=days, y=p.money, label=[p.id]))

print(graph_money)

graph_utility = ggplot()+ggtitle("Utilité des individus selon le temps")
for p in people.values():
    graph_utility += geom_line(aes(x=seq(0, days), y=[utility[i][p.id] for i in seq(0, days)]), color="red",
                       alpha=0.5)
    graph_utility += geom_text(aes(x=days, y=p.utility, label=[p.id]))

graph_utility += theme_bw()
print(graph_utility)


graph_prix = ggplot()+ggtitle("Prix des biens selon le temps")
for market in exchange.markets.keys():
    graph_prix += geom_line(aes(x=seq(0, days), y=[biens_prix[i][market] for i in seq(0, days)]), color="red",
                       alpha=0.5)
    graph_prix += geom_text(aes(x=days, y=biens_prix[days][market], label=[market]))

graph_prix += theme_bw()
print(graph_prix)



