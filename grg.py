import inspect
import numpy as np
import math
#à améliorer car peut prendre X1 dans 2X1+X2-10=0 et puis X2 dans 20-2X1-3X2+0.5X3+X4-S1=0 alors que X1 et X2 ne peuvent pas être en même temps Y.

class GRG:
    def __init__(self, f, X_init, gs, bounds):
        self.Xi = X_init
        self.XPREV = X_init
        self.bounds = bounds
        if (not all(self.is_inside_bounds(X_init, list(X_init.keys())).values())):
            raise ValueError("erreur : point initial n'est pas dans le domaine de possibilitées")
        self.f=f

        self.gs=gs

        self.i=0
        self.CONSFLG=0
        self.x=None
        self.y=None
        self.n=len(self.Xi)
        self.m=len(self.gs)
        self.percent_change=1
        self.consecutive=0
        self.epsilon = 10**(-4)

    def main_program(self):
        self.partition_y_x()
        self.entry5()
        if self.has_hit_bound():
            self.updateH()
            self.entry2()
        else:
            self.estim_deriv()
            self.compute_gradients()
            self.DFP_H()
            self.entry4()

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

        return None

    def entry5(self):
        self.H = np.identity(self.n - self.m)

        on_bounds = self.is_on_bounds(self.x)

        for i in range(len(on_bounds)):
            if list(on_bounds.values())[i]:
                self.H[i, i] = 0

        if self.CONSFLG==1:
            self.CONSLG=0
        else:
            self.entry2()
        return None

    def entry2(self):
        self.compute_gradients()
        self.compute_nabla()
        self.entry4()
        return None

    def entry4(self):
        self.release()
        self.compute_alphaBAR()
        self.optimality_test()
        self.one_dim_search()
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
        return X, True

    def y_from_x(self, X):
        new_x = X.copy()
        for i in range(len(self.gs)):
            new_X = self.solve(self.gs[i], new_x, list(self.y)[i], min_it = 20)

        return None

    def is_on_bounds(self, keys):
        ret = dict()
        for k in keys:
            ret[k] = (self.Xi[k] == self.bounds["up"][k] or self.Xi[k] == self.bounds["low"][k])
        return ret

    def is_inside_bounds(self, XBAR, keys):
        ret = XBAR.copy()
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
        self.d = np.matmul(self.H, self.dF_dx)
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
        alphas = [float("inf")] * len(self.x)
        for i in range(len(self.x)):
            if self.d[i, 0] > 0:
                if self.bounds["up"][self.x[i]] != float("inf"):
                    alphas[i] = (self.bounds["up"][self.x[i]] - self.Xi[self.x[i]]) / self.d[i, 0]
            elif self.d[i, 0] < 0:
                if self.bounds["low"][self.x[i]] != float("-inf"):
                    alphas[i] = (self.bounds["low"][self.x[i]] - self.Xi[self.x[i]]) / self.d[i, 0]
        self.alphaBAR = min(alphas)
        return None

    def optimality_test(self):
        if self.percent_change < 0.01:
            self.consecutive += 1
        else:
            self.consecutive = 0

        if self.consecutive >= 10:
            return "END"
        return None

    def one_dim_search(self):
        self.alpha0 = 0.1
        self.A=0
        self.R=0
        self.CFLG=0
        self.KL=-10**30
        self.FA=self.f(self.Xi)
        self.CTR=0
        self.B=min(self.alpha0, self.alphaBAR)
        while True:
            self.alpha = self.B
            self.FB = self.evaluate_F()
            if self.FB >= self.FA and self.SLPFLG != 1:
                break
            self.B=self.B/2
            self.KL=self.FB
        self.C = 2*self.B
        self.CFLG = 1
        while True:
            if self.KL >= self.FA:
                self.entry2B()
            else:
                if self.KL<-10**31:
                    self.block9B()
                else:
                    self.FC=self.KL
                    self.entry4B()
        return None
    def block9B(self):
        self.C = self.B + (self.C - self.B) / 3
        self.R = 1
        self.entry2B()
        return None

    def entry2B(self):
        self.alpha=self.C
        self.FC = self.evaluate_F()
        if self.SLPFLG==1 or self.FC < -10**31:
            self.bock9B()
        else:
            if self.FC < self.FB:
                self.entry4B()

            else:
                if self.C > self.alphaBAR:
                    self.alpha = self.alphaBAR
                    return None
                else:
                    self.A = self.B
                    self.B=self.C
                    self.FA = self.FB
                    self.FB=self.FC
                    self.C = 2*self.B - self.R * self.A
                    if self.R==1:
                        self.CTR += 1
                        if self.CTR == 3:
                            self.R=0
                            self.CTR=0
                            self.entry2B()
                        else:
                            self.entry2B()
                    else:
                        self.entry2B()
        return None

    def entry4B(self):
        self.quad_interpol()
        self.entry3B()
        return None


    def quad_interpol(self):
        a3 = (self.FA-self.FB-(self.A-self.B)/(self.B-self.C)*(self.FB-self.FC))/((self.A**2-self.B**2) - (self.A-self.B)/(self.B-self.C)*(self.B**2-self.C**2))
        a2 = (self.FA-self.FB-a3*(self.A**2-self.B**2))/(self.A-self.B)
        self.D = -a2/(2*a3)
        return None

    def cubic_interpol(self):
        tmp_mult = (self.A**2-self.B**2-(self.B**2-self.C**2)*(self.A-self.B)/(self.B-self.C))/(self.B**2-self.C**2-(self.C**2-self.D**2)*(self.B-self.C)/(self.C-self.D))
        a4 = (self.FA-self.FB-(self.FB-self.FC)*(self.A-self.B)/(self.B-self.C)-(self.FB-self.FC-(self.FC-self.FM)*(self.B-self.C)/(self.C-self.D))*tmp_mult) / (self.A**3-self.B**3-(self.B**3-self.C**3)*(self.A-self.B)/(self.B-self.C) - (self.B**3-self.C**3-(self.C**3-self.D**3)*(self.B-self.C)/(self.C-self.D))*tmp_mult)
        a3 = ((self.FA-self.FB-(self.FB-self.FC)*(self.A-self.B)/(self.B-self.C))-(self.A**3-self.B**3-(self.B**3-self.C**3)*(self.A-self.B)/(self.B-self.C))*a4)/(self.A**2-self.B**2-(self.B**2-self.C**2)*(self.A-self.B)/(self.B-self.C))
        a2 = ((self.FA-self.FB)-(self.A**3-self.B**3)*a4-(self.A**2-self.B**2)*a3)/(self.A-self.B)
        self.E = (-2*a3-math.sqrt(4*a3**2-4*a2*3*a4))/(2*3*a4) #ou l'autre racine
        return None
    def entry3B(self):
        self.alpha = self.D
        self.FM = self.evaluate_F()
        while True:
            self.block19B()
            if abs((self.FE-self.FM)/self.FE) < self.epsilon and abs((self.FE-self.FQ)/self.FE) < self.epsilon:
                break
            else:
                pass
                self.FM=self.FE
        if self.E > self.alphaBAR:
            self.C = self.alphaBAR
            self.FC = self.evaluate_F()
            if self.FC < self.f(self.XBAR):
                self.alpha = self.alphaBAR
                return None
            else:
                if self.FC > self.FB:
                    self.entry4B()
                else:
                    raise(ValueError("Error stop!"))
        else:
            self.alpha = self.E
            return None
        return None

    def block19B(self):
        self.cubic_interpol()
        self.FQ = self.evaluate_F()
        self.alpha = self.E
        self.FE = self.evaluate_F()
        return None

    def evaluate_F(self):
        self.XPREV = self.Xi.copy()
        for j in range(len(self.x)):
            self.Xi[self.x[j]] = self.Xi[self.x[j]] + self.alpha * self.d[j, 0]
        self.REDOBJ()
        self.NEWG()
        return self.f(self.Xi)

    def REDOBJ(self):
        self.v = np.matmul(np.linalg.inv(self.dg_dy), np.matmul(self.dg_dx, self.d))
        self.y_from_x(self.XPREV)
        #self.block1C()
        return None

    def NEWG(self):
        self.SLPFLG=0
        return None

    def block1C(self):
        self.Xi, self.newton_converge = self.solve()
        if self.newton_converge:
            #jamais de nonbinding consraints car déjà converti avec slack variables
            self.BSCHNG()
            self.XPREV = self.Xi
            return None
        else:
            if self.alternative1:
                if self.alternative2:
                    pass
                else:
                    pass
            else:
                pass

    def BSCHNG(self):
        if any(self.is_inside_bounds(self.Xi, self.y)):
            self.entry1D()
        else:
            return None
        return None

    def entry1D(self):
        alphas = [float("inf")] * len(self.y)
        for i in range(len(self.y)):
            if self.d[i, 0] > 0:
                if self.bounds["up"][self.x[i]] != float("inf"):
                    alphas[i] = (self.bounds["up"][self.x[i]] - self.Xi[self.x[i]]) / self.d[i, 0]
            elif self.d[i, 0] < 0:
                if self.bounds["low"][self.x[i]] != float("-inf"):
                    alphas[i] = (self.bounds["low"][self.x[i]] - self.Xi[self.x[i]]) / self.d[i, 0]
        self.alphaBAR = min(alphas)
        return None