#' government generator
#' 
#' @param pays un character : nom du pays associé.
#' @param taxes un numeric : taxes de ventes.
#' @param impot une fonction : impot selon les revenus.
#' @param bonds une liste : tous les bonds émis par le gouvernement.
#' @param dette un numeric : dette publique.
#' @param min_payment un numeric : intérêt minimal à rembourser à chaque année.
#'
#' @return objet de classe "government".
#' @export
#'
#' @examples
#' government("Canada", 0.15, function(revenu) 0.3 * revenu, list())
#' government("Canada", 0.15, function(revenu) 0.3 * revenu, list(bond(1000, 0.03, 30, 18), bond(10000, 0.02, 15, 1)))
government <- function(
  pays = NA,
  taxes = NA,
  impot = NA,
  bonds = NA,
  dette = NA,
  min_payment = NA
) {
  obj <- list(
    pays = pays,
    taxes = taxes,
    impot = impot,
    bonds = bonds,
    dette = if(length(bonds) != 0L) {
      sum(
        sapply(bonds, function(b) {
          b$face_value
        })
      )} else {
        0
      },
    min_payment = if(length(bonds) != 0L) {
      sum(
        sapply(bonds, function(b) {
          b$cash_flow
        })
      )} else {
        0
      }
  )
  
  attr(obj, "class") <- "government"
  obj
}

print.government <- function(obj) {
  cat("Gouvernement: ", obj$pays, "\n", sep = "")
  cat("  dette: ", obj$dette, "\n", sep = "")
  cat("  paiement minimal d'intérêt sur la dette: ", obj$min_payment, "\n", sep = "")
  cat("  taux de change: ", obj$taxes, "\n", sep = "")
}
