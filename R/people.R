#' people generator
#'
#' @param n un integer : nombre d'habitants à générer aléatoirement.
#' @param pays un vecteur de character : noms des pays existants.
#'
#' @return liste d'habitants.
#' @export
#'
#' @examples
#' people(3)
#' 
#' peuple <- people(3)
#' numeraire(peuple)
#' M1(peuple)
#' M2(peuple)
people <- function(n = 1, pays = NA) {
  obj <- list()
  
  for (i in 1:n) {
    
    obj[[i]] <- habitant(i, sample(pays, 1), sample(10000, 1), sample(10000, 1), sample(10000, 1), sample(10000, 1), sample(10000, 1), list(bouffe = sample(20, 1), eau = sample(10, 1)), function(biens) biens$bouffe * sample(7, 1) + biens$eau * sample(4, 1))
    
  }
  
  attr(obj, "class") <- "people"
  obj
  
}

# print method
print.people <- function(obj) {
  value <- sapply(obj, function(x) {
    data.frame(
      id = x$id,
      pays = x$pays,
      actifs = x$actifs,
      credit = x$credit,
      dette = x$dette,
      bonds = x$bonds,
      bonheur = x$bonheur
    )
  })
  print(t(value))
}

numeraire <- function(people) {
  UseMethod("numeraire")
}

numeraire.people <- function(people) {
  sum(sapply(people, function(habitant) habitant$numeraire))
}

M1 <- function(people) {
  UseMethod("M1")
}

M1.people <- function(people) {
  # M = N + D
  sum(sapply(people, function(habitant) habitant$numeraire + habitant$compte_cheque))
}

M2 <- function(people) {
  UseMethod("M2")
}

M2.people <- function(people) {
  # M = N + D
  sum(sapply(people, function(habitant) habitant$numeraire + habitant$compte_cheque + habitant$CPG))
}
