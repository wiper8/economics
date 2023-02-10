from math import log as ln, floor
from classes import *
from maximize import solver, optim, marginal_util_optim
from plotnine import ggplot, geom_col, geom_line, geom_text, ggtitle, theme_bw, aes, ylim
import re
import numpy as np
###############

alpha = 0.9 #decrease_in_utility_over_time  peut être >1 ou <1 dépendent de si quelquun préfère conserver son cash ou dépenser

#Créer les recettes des biens
recettes = {
    #ressources
    "terrain.pied^2":[{"Travail_manuel":0.1}],
    "bois.planche":[{"Travail_manuel":1}],
    "maison":[{"Travail_manuel":240, "Travail_intelligence":90, "terrain.pied^2":10000, "bois.planche":15000}],#très temporatire!
    "fer.kg":[{"Travail_manuel":72, "Travail_intelligence":20, "pelle":True}],
    "cuivre.kg":[{"Travail_manuel":168, "Travail_intelligence":30, "pelle":True}],
    "petrole.L":[{"Travail_manuel":1000, "Travail_intelligence":50, "pelle":True, "pompe":True}],
    "blé.kg":[{"Travail_manuel":0.15, "terrain.pied^2":1090}],
    "pelle": [{"Travail_manuel": 8, "bois":1}],
    "pompe":[{"Travail_manuel":72, "fer.kg":1, "cuivre.kg":0.01}],
    #biens
    "pain":[{"Travail_manuel":1, "Travail_intelligence":0.05, "blé.kg":0.02}],
    "céréales.box":[{"Travail_manuel":1, "Travail_intelligence":0.08, "blé.kg":0.4}]
}


#ajouter les produits : auto, maison, divertissement

biens_consommables = ["temps libre", "Travail_manuel", "Travail_intelligence", "Travail_relationnel", "Travail_surface", "pain", "céréales.box", "blé.kg"]

n_people = 10

rng = np.random.default_rng().normal(0, 1, size=(n_people, 4))

rng2 = np.array(["manuel", "intelligence", "relationnel", "surface"])[rng.argmax(axis=1)]
rng = rng.max(axis=1)


people = {}
for i in range(n_people):
    people["P"+str(i)] = Person("P"+str(i), rng[i], rng2[i], money = 5, utility_fun = {"temps libre":{"k":max(0.1, 1+np.random.normal(scale=0.1)), "c":max(1.001, 1.2+np.random.normal(scale=0.1)), "consommer":True},
                                                                                 "pain":{"k":max(0.1, 2.5+np.random.normal(scale=0.1)), "c":max(1.001, 1.7+np.random.normal(scale=0.1)), "consommer":True},
                                                                                 "céréales.box":{"k":max(0.1, 2+np.random.normal(scale=0.1)), "c":max(1.001, 1.6+np.random.normal(scale=0.1)), "consommer":True},
                                                                                 "maison":{"k":max(0.1, 10+np.random.normal(scale=0.1)), "c":max(1.001, 4.5+np.random.normal(scale=0.1)), "consommer":False}},
                                alpha=alpha)
sorted(people.keys())

compagnies = [
    Compagnie("C1", "terrain.pied^2", "TERR", 100, shareholders={"P1" : 1000000}),
    Compagnie("C2", "blé.kg", "BLE", 100, shareholders={"P2" : 300000, "P3" : 200000, "P4" : 500000}),
    Compagnie("C3", "pain", "PIN", 100, shareholders={"P3" : 1000000}),
    Compagnie("C4", "céréales.box", "CER", 100, shareholders={"P1":100000, "P2":200000, "P3":100000, "P4" : 600000}),
    Compagnie("C5", "maison", "HOM", 100, shareholders={"P4":1000000}),
    Compagnie("C6", "bois.planche", "PLAN", 100, shareholders={"P2":1000000})
]

for inc in compagnies:
    for investor, nshares in inc.shareholders.items():
        people[investor].stocks[inc.id] = nshares

exchange = Exchange()
#préparer les personnes et les prix initiaux du marchés pour qu'ils puissent préparer leurs offres
for p in people.values():
    exchange.add_entity(p)
for inc in compagnies:
    exchange.add_entity(inc)
    exchange.add_market(inc.production, Market(last_price = 1))

exchange.add_market("Travail_manuel", Market(last_price=1))
exchange.add_market("Travail_intelligence", Market(last_price=1))
exchange.add_market("Travail_relationnel", Market(last_price=1))
exchange.add_market("Travail_surface", Market(last_price=1))

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


n = 3 #days_to_forcast_utility >=2
days=20

money_distribution = [None] * (days+1)
biens_prix = [None] * (days+1)
utility = [None] * (days+1)

money_distribution[0] = {}
biens_prix[0] = {}
utility[0] = {}

for p in people.values():
    money_distribution[0][p.id] = p.money
    utility[0][p.id] = p.utility
for inc in compagnies:
    money_distribution[0][inc.id] = inc.money
for b in list(exchange.markets.keys()):
    biens_prix[0][b] = exchange.markets[b].last_price


for day in range(days):
    print(f'Day : {day}')
    exchange.execute(True, True)

    #donner 24 heures a chq personne
    for p in people.values():
        p.new_day()

    for inc in compagnies:
        inc.new_day()

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
                        k.append(p.utility_fun[b]["k"] * alpha ** i)
                if n > 1:
                    for i in range(n - 1):
                        k.append(p.utility_fun["temps libre"]["k"] * alpha ** i)
                c = []
                for b in biens:
                    for i in range(n):
                        c.append(p.utility_fun[b]["c"])
                if n > 1:
                    for i in range(n - 1):
                        c.append(p.utility_fun["temps libre"]["c"])
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

                # quantite_avant = 0
                # at_least_one_demande = False
                # expo = -5
                # while not at_least_one_demande:
                #
                #         prix = exchange.markets[bien].last_price * (1.15 ** (-expo)) #offres de prix
                #
                #         prices = [prix]*n
                #         for b in biens[1:]:
                #             for i in range(n):
                #                 prices.append(exchange.markets[b].last_price)
                #         if n>1:
                #             for i in range(n-1):
                #                 prices.append(exchange.markets["Travail_"+p.best].last_price)
                #
                #         quantities = marginal_util_optim(prices, k, c, constrs, libre, p, n, consum)
                #
                #         quant = quantities[biens.index(bien) * n] - quantite_avant
                #         if quant > 0:
                #             at_least_one_demande = True
                #             for q in seq(1, quant):
                #                 exchange.entities[p.id].order(exchange, bien, 1, limit=prix, buy=True)
                #         quantite_avant = quant
                #         if expo < 5:
                #             at_least_one_demande = False
                #         if expo > 30:
                #             at_least_one_demande = True
                #         expo += 1

                quantite_avant = 0
                for expo in range(-5, 6):

                    prix = exchange.markets[bien].last_price * (1.15 ** (-expo))  # offres de prix

                    prices = [prix] * n
                    for b in biens[1:]:
                        for i in range(n):
                            prices.append(exchange.markets[b].last_price)
                    if n > 1:
                        for i in range(n - 1):
                            prices.append(exchange.markets["Travail_" + p.best].last_price)

                    quantities = marginal_util_optim(prices, k, c, constrs, libre, p, n, consum)

                    quant = quantities[biens.index(bien) * n] - quantite_avant
                    if quant > 0:
                        exchange.entities[p.id].order(exchange, bien, quant, limit=prix, buy=True)
                    quantite_avant = quant


        if n > 1:
            #déterminer l'offre du travail
            biens = list(set(p.utility_fun.keys()) - set(["temps libre"]))

            k = []
            for b in biens:
                for i in range(n):
                    k.append(p.utility_fun[b]["k"] * alpha ** i)

            for i in range(n - 1):
                k.append(p.utility_fun["temps libre"]["k"] * alpha ** i)
            c = []
            for b in biens:
                for i in range(n):
                    c.append(p.utility_fun[b]["c"])
            for i in range(n - 1):
                c.append(p.utility_fun["temps libre"]["c"])

            consum = []
            for b in biens:
                for i in range(n):
                    consum.append(p.utility_fun[b]["consommer"])
            for i in range(n - 1):
                consum.append(p.utility_fun["temps libre"]["consommer"])

            libre = [False] * (n * len(biens))

            for i in range(n - 1):
                libre.append(True)


            # quantite_avant = 0
            # at_least_one_demande = False
            # expo = -5
            # while not at_least_one_demande:
            #     prix = exchange.markets["Travail_"+p.best].last_price * (1.15 ** expo)
            #
            #     prices = []
            #     for b in biens:
            #         for i in range(n):
            #             prices.append(exchange.markets[b].last_price)
            #
            #     for i in range(n - 1):
            #         prices.append(prix)
            #
            #     quantities = marginal_util_optim(prices, k, c, constrs, libre, p, n, consum)
            #
            #     quant = 24 - quantities[n*len(biens)] - quantite_avant
            #     if quant * np.exp(p.travail_level) >= 1:
            #         for q in seq(1, quant * np.exp(p.travail_level)):
            #             exchange.entities[p.id].order(exchange, "Travail_"+p.best, 1, limit=prix,
            #                                           buy=False)
            #     quantite_avant = quant
            #     if expo < 5:
            #         at_least_one_demande = False
            #     if expo > 30:
            #         at_least_one_demande = True
            #     expo += 1

            quantite_avant = 0
            for expo in range(-5, 6):

                prix = exchange.markets["Travail_" + p.best].last_price * (1.15 ** expo)

                prices = []
                for b in biens:
                    for i in range(n):
                        prices.append(exchange.markets[b].last_price)

                for i in range(n - 1):
                    prices.append(prix)

                quantities = marginal_util_optim(prices, k, c, constrs, libre, p, n, consum)

                quant = 24 - quantities[n * len(biens)] - quantite_avant
                if quant * np.exp(p.travail_level) >= 1:
                    exchange.entities[p.id].order(exchange, "Travail_" + p.best, math.floor(quant * np.exp(p.travail_level)), limit=prix, buy=False)
                quantite_avant = quant

    #print(f'demande pain : {[round(ordre[1], ndigits=2) for ordre in exchange.markets["pain"].buys]}')
    #print(f'demande céréales.box : {[round(ordre[1], ndigits=2) for ordre in exchange.markets["céréales.box"].buys]}')
    #print(f'demande maison : {[round(ordre[1], ndigits=2) for ordre in exchange.markets["maison"].buys]}')
    #print(f'offre Travail : {[round(ordre[1], ndigits=2) for ordre in exchange.markets["Travail_manuel"].sells]}')
    print("after people")
    ###compagnies demandent ressources
    for inc in compagnies:
        #commence à Q=0 jusqu'au max de la demande
        cout_total = [0] * (len(exchange.markets[inc.production].buys)+1)
        # commence à 0
        profit = [0] * len(cout_total)

        if(len(cout_total) > 1):
            for ressource in list(set(recettes[inc.production][0].keys())):
                if ressource in list(inc.biens.keys()):
                    for Q in seq(1, len(cout_total) - 1):
                        cout_total[Q] += max(0, Q * recettes[inc.production][0][ressource] - inc.biens[ressource]) * exchange.markets[
                            ressource].last_price
                        profit[Q] = exchange.markets[inc.production].buys[Q - 1][1] * Q - cout_total[Q]
                        if profit[Q] <= 0:
                            break
                else:
                    cout_par_unit = recettes[inc.production][0][ressource] * exchange.markets[
                            ressource].last_price
                    #maximiser le profit
                    for Q in seq(1, len(cout_total) - 1):
                        cout_total[Q] += Q * cout_par_unit
                        profit[Q] = exchange.markets[inc.production].buys[Q - 1][1] * Q - cout_total[Q]
                        if profit[Q] <= 0:
                            break

            Q = profit.index(max(profit))

            if profit[Q] > 0 and Q > 0:
                if inc.money > 0:
                    for ress in recettes[inc.production][0].keys():
                        if ress in list(inc.biens.keys()):
                            if inc.biens[ress] < math.ceil(Q * recettes[inc.production][0][ress]):
                                for Q_ress in seq(1, math.ceil(Q * recettes[inc.production][0][ress]) - inc.biens[ress]):
                                    demande = min(inc.money, (profit[Q] - (cout_total[Q] - exchange.markets[ress].last_price *
                                            Q_ress))) / Q_ress
                                    # TODO probablement pas optimal car est la limite pour un profit de 0

                                    if demande > 0:
                                        exchange.entities[inc.id].order(exchange, ress, 1, limit=demande, buy=True)
                                    else:
                                        break

                        else:
                            for Q_ress in seq(1, math.ceil(Q * recettes[inc.production][0][ress])):
                                # TODO probablement pas optimal car est la limite pour un profit de 0
                                demande = min(inc.money, (profit[Q] - (cout_total[Q] - exchange.markets[ress].last_price *
                                            Q_ress))) / Q_ress
                                if demande > 0:
                                    exchange.entities[inc.id].order(exchange, ress, 1, limit=demande, buy=True)
                                else:
                                    break

    print("after comp")
    #print(f'demande blé.kg : {[round(ordre[1], ndigits=2) for ordre in exchange.markets["blé.kg"].buys]}')
    #print(f'demande terrain.pied^2 : {[round(ordre[1], ndigits=2) for ordre in exchange.markets["terrain.pied^2"].buys]}')
    #print(f'demande bois.planche : {[round(ordre[1], ndigits=2) for ordre in exchange.markets["bois.planche"].buys]}')

    #acheter les ressources le matin
    exchange.execute(False, True)

    #demande de main doeuvre
    for inc in compagnies:

        max_production = math.inf
        r = re.compile("Travail.*")
        for ressource in list(set(recettes[inc.production][0].keys()) - set(list(filter(r.match, list(set(recettes[inc.production][0].keys())))))):
            if ressource in list(inc.biens.keys()):
                max_production = min(max_production, math.floor(inc.biens[ressource] / recettes[inc.production][0][ressource]))
            else:
                max_production = 0


        # commence à Q=0
        cout_total = [0] * (min(len(exchange.markets[inc.production].buys), max_production) + 1)
        # commence à 0
        profit = [0] * len(cout_total)

        if (len(cout_total) > 1):

            for ressource in list(set(recettes[inc.production][0].keys())):
                if ressource in list(inc.biens.keys()):
                    for Q in seq(1, len(cout_total) - 1):
                        cout_total[Q] += max(0, Q * recettes[inc.production][0][ressource] - inc.biens[ressource]) * \
                                         exchange.markets[
                                             ressource].last_price
                        profit[Q] = exchange.markets[inc.production].buys[Q - 1][1] * Q - cout_total[Q]
                        if profit[Q] <= 0:
                            break
                else:
                    for Q in seq(1, len(cout_total) - 1):
                        cout_total[Q] += Q * recettes[inc.production][0][ressource] * exchange.markets[
                                ressource].last_price
                        profit[Q] = exchange.markets[inc.production].buys[Q - 1][1] * Q - cout_total[Q]
                        if profit[Q] <= 0:
                            break

            Q = profit.index(max(profit))

            if profit[Q] > 0 and Q > 0:
                if inc.money > 0:
                    r = re.compile("Travail.*")

                    for ress in list(filter(r.match, list(set(recettes[inc.production][0].keys())))):
                        for Q_ress in seq(1, math.ceil(Q * recettes[inc.production][0][ress])):
                            if ress in list(inc.biens.keys()):
                                if inc.biens[ress] >= Q_ress:
                                    demande = 0
                                else:
                                    demande = (profit[Q] - (cout_total[Q] - exchange.markets[ress].last_price * (
                                                Q_ress - inc.biens[ress]))) / (Q_ress - inc.biens[ress])
                                    # TODO probablement pas optimal car est la limite pour un profit de 0
                            else:
                                # TODO probablement pas optimal car est la limite pour un profit de 0
                                demande = (profit[Q] - (cout_total[Q] - exchange.markets[ress].last_price *
                                                        Q_ress)) / Q_ress

                            if demande > 0:
                                exchange.entities[inc.id].order(exchange, ress, 1, limit=demande, buy=True)
                            else:
                                break


            #les compagnies décides du prix car monopole
            prix_offert = exchange.markets[inc.production].find_price(Q)

            if Q>0:
                for i in seq(1, Q):
                    exchange.entities[inc.id].order(exchange, inc.production, 1, limit=prix_offert, buy=False)

    #print(f'offre Travail : {[round(ordre[1], ndigits=2) for ordre in exchange.markets["Travail"].buys]}')

    exchange.execute(False, True)

    #print(f'demande pain : {[round(ordre[1], ndigits=2) for ordre in exchange.markets["pain"].buys]}')
    #print(f'demande céréales.box : {[round(ordre[1], ndigits=2) for ordre in exchange.markets["céréales.box"].buys]}')
    #print(f'demande maison : {[round(ordre[1], ndigits=2) for ordre in exchange.markets["maison"].buys]}')
    #print(f'demande blé.kg : {[round(ordre[1], ndigits=2) for ordre in exchange.markets["blé.kg"].buys]}')
    #print(f'demande terrain.pied^2 : {[round(ordre[1], ndigits=2) for ordre in exchange.markets["terrain.pied^2"].buys]}')
    #print(f'demande bois.planche : {[round(ordre[1], ndigits=2) for ordre in exchange.markets["bois.planche"].buys]}')
    #print(f'offre Travail : {[round(ordre[1], ndigits=2) for ordre in exchange.markets["Travail"].buys]}')

    #créer les biens des compagnies
    for inc in compagnies:
        prod=math.inf
        for ingredient in list(recettes[inc.production][0].keys()):
            if ingredient not in list(inc.biens.keys()):
                prod = 0
            else:
                prod = min(prod, floor(inc.biens[ingredient] / recettes[inc.production][0][ingredient]))
        if prod > 0:
            for ingredient in list(recettes[inc.production][0].keys()):
                if ingredient in biens_consommables:
                    inc.biens[ingredient] -= prod * recettes[inc.production][0][ingredient]

            inc.biens[inc.production] += prod

    for p in people.values():
        p.consume()

    #verser dividendes quotidiens
    for inc in compagnies:
        dividende = (inc.money - inc.money_debut_jour) * 0.5
        for investor in inc.shareholders.keys():
            people[investor].money += dividende * inc.shareholders[investor] / inc.nshares
        inc.money -= dividende

    money_distribution[day + 1] = {}
    biens_prix[day + 1] = {}
    utility[day + 1] = {}
    for p in people.values():
        money_distribution[day+1][p.id] = p.money
        utility[day+1][p.id] = p.utility
    for inc in compagnies:
        money_distribution[day + 1][inc.id] = inc.money
    for b in list(exchange.markets.keys()):
        biens_prix[day+1][b] = exchange.markets[b].last_price

    #exchange.markets["pain"].plot()


graph_money = ggplot()+ggtitle("Argent des individus selon le temps")
max_y = 0
for p in people.values():
    max_y = max(max_y, max([money_distribution[i][p.id] for i in seq(0, days)]))
    graph_money += geom_line(aes(x=seq(0, days), y=[money_distribution[i][p.id] for i in seq(0, days)]), color="green", alpha=0.5)
    graph_money += geom_text(aes(x=days, y=p.money, label=[p.id]))
for inc in compagnies:
    max_y = max(max_y, max([money_distribution[i][inc.id] for i in seq(0, days)]))
    graph_money += geom_line(aes(x=seq(0, days), y=[money_distribution[i][inc.id] for i in seq(0, days)]), color="green", alpha=0.5)
    graph_money += geom_text(aes(x=days, y=inc.money, label=[inc.id]))

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



