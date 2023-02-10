
import inspect
import numpy as np
import math
#à améliorer car peut prendre X1 dans 2X1+X2-10=0 et puis X2 dans 20-2X1-3X2+0.5X3+X4-S1=0 alors que X1 et X2 ne peuvent pas être en même temps Y.

class GRGW:
    def __init__(self, f, X_init, gs, bounds):
        self.Xi = X_init
        self.XNEXT = X_init
        self.bounds = bounds
        if (not all(self.is_inside_bounds(X_init, list(X_init.keys())).values())):
            raise ValueError("erreur : point initial n'est pas dans le domaine de possibilitées")
        self.f=f

        self.gs=gs

        self.i=0
        self.x=None
        self.y=None
        self.n=len(self.Xi)
        self.m=len(self.gs)
        self.percent_change=1
        self.max_it = 1000
        self.epsilon = 0.1

    def main_program(self):
        self.partition_y_x()
        self.y_from_x(self.Xi)
        while True:
            self.i += 1
            print(self.x)
            print(self.y)
            print(self.Xi)
            self.compute_gradients()
            self.compute_nabla()

            self.H = np.identity(self.n - self.m)
            on_bounds = self.is_on_bounds(self.x)

            for i in range(len(on_bounds)):
                if list(on_bounds.values())[i] == "up" and self.dF_dx[i, 0] > 0:
                    self.H[i, i] = 0
                if list(on_bounds.values())[i] == "low" and self.dF_dx[i, 0] < 0:
                    self.H[i, i] = 0

            self.d = np.matmul(self.H, self.dF_dx)
            print(self.H)
            print(self.d)
            for i in range(len(self.x)):
                self.XNEXT[self.x[i]] = self.Xi[self.x[i]] + self.d[i, 0] * self.epsilon

            if any([v == False for k, v in self.is_inside_bounds(self.XNEXT, self.x)]):
                alphas = [float("inf")] * len(self.x)
                for i in range(len(self.x)):
                    if self.d[i, 0] > 0:
                        if self.bounds["up"][self.x[i]] != float("inf"):
                            alphas[i] = (self.bounds["up"][self.x[i]] - self.Xi[self.x[i]]) / self.d[i, 0]
                    elif self.d[i, 0] < 0:
                        if self.bounds["low"][self.x[i]] != float("-inf"):
                            alphas[i] = (self.bounds["low"][self.x[i]] - self.Xi[self.x[i]]) / self.d[i, 0]
                self.epsilon = min(alphas)

            self.y_from_x(self.XNEXT)
            self.change_basis(self.XNEXT)
            self.fNEXT = self.f(self.XNEXT)
            print(self.f(self.Xi))
            print(self.fNEXT)

            self.percent_change = self.fNEXT / self.f(self.Xi) - 1
            self.Xi = self.XNEXT

            if self.i >= self.max_it:
                break
            if self.percent_change < 0.001:
                break

        return None

    def partition_y_x(self, y=[], x=[]):
        self.y=y
        self.x=x
        gs_params = [None] * len(self.gs)

        for i in range(len(self.gs)):
            signature = inspect.signature(self.gs[i])
            gs_params[i] = [{
                k: v.default
                for k, v in signature.parameters.items()
                if v.default is not inspect.Parameter.empty
            }]
            gs_params[i][0] = gs_params[i][0]["vars"]
            if len(x) > 0:
                for xi in x:
                    if xi in gs_params[i][0]:
                        gs_params[i][0].remove(xi)
            if len(y) > 0:
                for yi in y:
                    if yi in gs_params[i][0]:
                        gs_params[i][0].remove(yi)

            gs_params[i].append(len(gs_params[i][0]))

        order = [params[1] for params in gs_params]
        order = sorted(range(len(order)), key=lambda k: order[k])
        gs_params = [gs_params[i] for i in order]
        self.gs.sort(key=lambda x: len(inspect.signature(x).parameters.values()))

        for eq in gs_params:
            new_set = eq[0].copy()
            if len(y) > 0:
                for yi in y:
                    if yi in new_set:
                        new_set.remove(yi)
            if len(x) > 0:
                for xi in x:
                    if xi in new_set:
                        new_set.remove(xi)
            self.y.append(new_set[0])
            new_set.remove(new_set[0])
            self.x.extend(new_set)
        print(self.y)
        print(self.x)
        return None


    def solve(self, g, X, y, min_it=100, max_it=10000):
        fact = 0.01
        sign = True
        i = 1
        d = 0

        while abs(d) > 0.01 or i <= min_it:
            if i > max_it:
                return None, False

            deriv = self.estim_deriv(lambda x: abs(g(x)), X, y)
            if (deriv > 0) == sign:
                fact *= 1.15
            else:
                fact *= 0.5
            sign = (deriv > 0)
            d = fact * deriv
            X[y] -= d
            i += 1
        return X[y], True

    def y_from_x(self, X):
        new_x = X.copy()
        converges=[None]*len(self.gs)
        for i in range(len(self.gs)):
            new_x[self.y[i]], converges[i] = self.solve(self.gs[i], new_x, list(self.y)[i], min_it = 20)
        if any([conv==False for conv in converges]):
            raise (ValueError("non convergence"))
        else:
            conditions = self.is_inside_bounds(new_x, self.y)
            if any([cond==False for cond in conditions.values()]):
                for yi in self.y:
                    if conditions[yi]==False:
                        self.partition_y_x(y=[], x=[yi])
                        self.y_from_x(self.Xi)
            else:
                for yi in self.y:
                    self.Xi[yi] = new_x[yi]
                print(self.Xi)
        return None

    def is_on_bounds(self, keys):
        ret = dict()
        for k in keys:
            if self.Xi[k] == self.bounds["up"][k]:
                ret[k] = "up"
            elif self.Xi[k] == self.bounds["low"][k]:
                ret[k] = "low"
            else:
                ret[k] = False
        return ret

    def is_inside_bounds(self, XBAR, keys):
        ret = XBAR.copy()
        for k in ret.keys():
            ret[k] = None
        for k in keys:
            ret[k] = XBAR[k] <= self.bounds["up"][k] and XBAR[k] >= self.bounds["low"][k]
        return ret

    def estim_deriv(self, f, X, k):
        new_X = X.copy()
        new_X[k] += 0.01
        return (f(new_X) - f(X)) / 0.01

    def compute_gradients(self):
        self.dF_dx = np.zeros((self.n - self.m, 1))
        self.df_dx = np.zeros((self.n - self.m, 1))
        self.df_dy = np.zeros((self.m, 1))
        self.dg_dy = np.zeros((self.m, self.m))
        self.dg_dx = np.zeros((self.m, self.n - self.m))

        for i in range((self.n - self.m)):
            self.df_dx[i, 0] = self.estim_deriv(self.f, self.Xi, list(self.x)[i])
        for i in range(self.m):
            self.df_dy[i, 0] = self.estim_deriv(self.f, self.Xi, list(self.y)[i])
            for j in range(self.m):
                self.dg_dy[i, j] = self.estim_deriv(self.gs[i], self.Xi, list(self.y)[j])
            for j in range(self.n - self.m):
                self.dg_dx[i, j] = self.estim_deriv(self.gs[i], self.Xi, list(self.x)[j])

        self.B_1 = -np.linalg.inv(self.dg_dy)
        self.pi = np.matmul(np.transpose(self.df_dy), self.B_1)
        return None

    def compute_nabla(self):
        for i in range((self.n - self.m)):
            self.dF_dx[i, 0] = self.df_dx[i, 0] + np.matmul(self.pi, self.dg_dx[:, [i]])
        return None

    def norm(self):
        return math.sqrt(sum([y ** 2 for y in self.x]))

    def release(self):
        self.kuhn_tucker_mult = [None] * len(self.x)
        for j in range(len(self.x)):
            if list(self.is_on_bounds([list(self.x)[j]]).values())[0]:
                if self.Xi[list(self.x)[j]] == self.bounds["up"][list(self.x)[j]]:
                    if -self.dF_dx[j, 0] > 0:
                        self.kuhn_tucker_mult[j] = self.dF_dx[j, 0]
                    elif self.dF_dx[j, 0] > 0:
                        self.kuhn_tucker_mult[j] = self.dF_dx[j, 0]
        if any([kuhn is not None for kuhn in self.kuhn_tucker_mult]):
            if max(self.kuhn_tucker_mult) > 2 * self.norm(self.d):
                j = self.kuhn_tucker_mult.index(max(self.kuhn_tucker_mult))
                self.H[j, j] = 1

    def compute_alphaBAR(self):

        return None

    def optimality_test(self):
        if self.percent_change < 0.01:
            self.consecutive += 1
        else:
            self.consecutive = 0

        if self.consecutive >= 10:
            return "END"
        return None

