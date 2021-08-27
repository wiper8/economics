#' central_bank generator
#'
#' @param pays un character : pays.
#' @param bonds une liste : bonds possédés par la banque centrale (actif).
#' @param numeraire un numeric : quantité d'argent en circulation hors banques
#'   (passif).
#' @param depot_banque_centrale un numeric : réserves que les banques à charte
#'   prêtent à la banque centrale au taux du financement à un jour (passif si
#'   positif).
#' @param inflation_cible un numeric : taux d'inflation ciblé.
#' @param overnight_rate_cible un numeric : taux d'intérêt à un jour ciblé pour 
#'   atteindre la cible d'inflation.
#' @param fourchette une fonction : équation de la fourchette opérationelle
#'   pour le taux de financement à un jour.
#' @param base_monetaire un numeric : base monétaire (passif).
#'   
#' Si le canada veut atteindre 2% d'inflation (taux constant) et que le taux
#'   d'inflation courant est à 5%, il faut monter les taux d'intérêt. La banque
#'   centrale va augmenter le taux cible du financement à un jour à supposons,
#'   10%. Elle va donc se mettre à échanger davantage avec les banques à charte
#'   avec des opérations d'open market changeant la quantité d'argent disponible
#'   sur le marché.
#'
#' @return objet de classe "central_bank".
#' @export
#'
#' @examples
#' central_bank(
#'   "Canada",
#'   list(
#'     bond(1000, 0.03, 30, 18),
#'     bond(2000, 0.04, 15, 4)
#'   ),
#'   100000,
#'   20000,
#'   0.02
#' )
central_bank <- function(
  pays = NA,
  bonds = NA,
  numeraire = NA,
  depot_banque_centrale = NA,
  inflation_cible = NA,
  overnight_rate_cible = inflation_cible * 2,
  fourchette = function(overnight_cible, depot_banque_centrale) 
    overnight_cible + max(-0.0025, min(0.0025, 0.0025 - depot_banque_centrale * 0.005 / 100)),
  base_monetaire = NA
) {
  obj <- list(
    pays = pays,
    bonds = bonds,
    numeraire = numeraire,
    depot_banque_centrale = depot_banque_centrale,
    inflation_cible = inflation_cible,
    overnight_rate_cible = overnight_rate_cible,
    overnight_rate = fourchette(overnight_rate_cible, depot_banque_centrale),
    base_monetaire = numeraire + depot_banque_centrale
  )
  
  attr(obj, "class") <- "central_bank"
  obj
}

print.central_bank <- function(obj) {
  cat("Central bank: ", obj$pays, "\n", sep = "")
  cat("  taux d'inflation ciblé: ", obj$inflation_cible, "\n", sep = "")
  cat("  taux cible du financement à un jour: ", obj$overnight_rate_cible, "\n", sep = "")
  cat("  taux du financement à un jour: ", obj$overnight_rate, "\n", sep = "")
  cat("  numéraire: ", obj$numeraire, "\n", sep = "")
  cat("  depot_banque_centrale: ", obj$depot_banque_centrale, "\n", sep = "")
  cat("  base monétaire: ", obj$base_monetaire, "\n", sep = "")
}
