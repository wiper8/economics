% Generated by roxygen2: do not edit by hand
% Please edit documentation in R/bank.R
\name{client}
\alias{client}
\title{client generator}
\usage{
client(id = NA, compte_cheque = NA, CPG = NA, dette = NA)
}
\arguments{
\item{id}{un entier : id de l'habitant.}

\item{compte_cheque}{un numeric : montant d'argent liquide déposée dans le
compte chèque.}

\item{CPG}{une liste : tous les CPG détenus.}

\item{dette}{une liste : toutes les dettes détenues.}
}
\value{
objet de classe "client".
}
\description{
client generator
}
\examples{
client(
  7,
  800,
  list(
    CPG(1000, 0.03, 5, 3),
    CPG(2000, 0.035, 6, 2)
  ),
  list(
    dette(1000, 0.03, 5, 3),
    dette(2000, 0.035, 6, 2)
  )
)
}
