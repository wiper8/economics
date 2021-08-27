#' habitant generator
#'
#' @param id un entier : id de l'habitant
#' @param pays un character : nom du pays de provenance.
#' @param argent un numeric : argent total en US dans le compte de l'habitant.
#' @param credit un numeric : crédit total en US dans le compte de l'habitant.
#' @param dette un numeric : dette totale en US dans le compte de l'habitant.
#' @param bonds une liste de `bonds` possédés par l'habitant.
#' @param bonheur un numeric : niveau de bonheur de l'habitant.
#' @param biens une liste de biens possédés par l'habitant.
#' @param formule_bonheur une formule : formule qui calcule le bonheur de
#'   l'habitant selon les biens qu'il possède.
#'
#' @return objet de classe "habitant".
#' @export
#'
#' @examples
#' habitant(
#'   7,
#'   "Canada",
#'   5000,
#'   20000,
#'   40000,
#'   0,
#'   0,
#'   list(
#'     bond(
#'       1000,
#'       0.04,
#'       30
#'     ),
#'     bond(
#'       2000,
#'       0.03,
#'       15
#'     )
#'   ),
#'   73,
#'   list(
#'     eau = 2,
#'     bouffe = 30
#'   ),
#'   function(biens) {
#'     biens$bouffe * 0.1 + biens$eau * 2
#'   }
#' )
habitant <- function(

  #attributs
  id = NA,
  pays = NA,
  numeraire = NA,
  compte_cheque = NA,
  CPG = NA,
  credit = NA,
  dette = NA,
  bonds = NA,
  bonheur = NA,
  biens = list(),

  #methods
  formule_bonheur = function(biens) {
    NA
  }

) {
  obj <- list(
    id = id,
    pays = pays,
    actifs = numeraire + compte_cheque + CPG,
    numeraire = numeraire,
    compte_cheque = compte_cheque,
    CPG = CPG,
    credit = credit,
    dette = dette,
    bonds = bonds,
    bonheur = formule_bonheur(biens),
    biens = biens,
    formule_bonheur = formule_bonheur
  )
  attr(obj, "class") <- "habitant"
  obj
}

# print method
#' @export
print.habitant <- function(obj) {
  cat("Habitant: \n")
  cat("  ID: ", obj$id, "\n", sep = "")
  cat("  pays: ", obj$pays, "\n", sep = "")
  cat("  actif: ", obj$actifs, "\n", sep = "")
  cat("  crédit: ", obj$credit, "\n", sep = "")
  cat("  dette: ", obj$dette, "\n", sep = "")
  cat("  bonheur_level: ", obj$bonheur, "\n", sep = "")
}


