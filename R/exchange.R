#' Exchange goods without money
#'
#' @param acheteur habitant 1.
#' @param vendeur habitant 2.
#' @param bien_achete un character : nom du bien acheté.
#' @param bien_vendu un character : nom du bien vendu.
#' @param quantite_achetee un numeric : quantité du bien acheté.
#' @param quantite_vendue un numeric : quantité du bien vendu.
#'
#' @return
#' @export
#'
#' @examples
#' producteur_eau <- habitant(1, "Canada")
#' producteur_pain <- habitant(2, "Canada")
#'
#' producteur_eau$biens$eau <- 6
#' producteur_pain$biens$pain <- 1.5
#'
#' exchange(producteur_eau, producteur_pain, "pain", "eau", 0.5, 2)
#'
exchange <- function(acheteur, vendeur, bien_achete, bien_vendu, quantite_achetee, quantite_vendue) {
  if (
    acheteur$biens[[bien_vendu]] < quantite_vendue |
    vendeur$biens[[bien_achete]] < quantite_achetee
  ) stop("biens insuffisants")

  acheteur$biens[[bien_achete]] <<- acheteur$biens[[bien_achete]] + quantite_achetee
  acheteur$biens[[bien_vendu]] <<- acheteur$biens[[bien_vendu]] - quantite_vendue

  vendeur$biens[[bien_achete]] <<- vendeur$biens[[bien_achete]] - quantite_achetee
  vendeur$biens[[bien_vendu]] <<- vendeur$biens[[bien_vendu]] + quantite_vendue

}
