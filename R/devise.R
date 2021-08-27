#' devise generator
#' 
#'  Pas besoin de définir le dollar US.
#'
#' @param nom un character : nom de la devise.
#' @param taux_change un numeric : taux de change avec la devise par défaut : le
#'   US.
#'
#' @return objet de classe "devise".
#' @export
#'
#' @examples
#' devise("Yen", 90.3)
devise <- function(
  nom = NA,
  taux_change = NA
) {
  obj <- data.frame(
    nom = nom,
    taux_change = taux_change
  )
  
  attr(obj, "class") <- "devise"
  obj
}

print.devise <- function(obj) {
  cat("Devise: ", obj$nom, "\n", sep = "")
  cat("  taux de change: ", obj$taux_change, "\n", sep = "")
}
