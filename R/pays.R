#' pays generator
#'
#' @param nom un character : nom du pays.
#' @param population un integer : nombre d'habitants du pays.
#' @param devise un character : devise du pays.
#' @param GDP un numeric : GDP du pays.
#' @param unemployment un numeric : taux de chomage du pays.
#' @param inflation un numeric : inflation du pays.
#' @param central_bank un objet de classe "central_bank".
#' @param government un objet de classe "government".
#'
#' @return
#' @export
#'
#' @examples
pays <- function(
  nom = NA,
  population = NA,
  devise = NA,
  GDP = NA,
  unemployment = NA,
  inflation = NA,
  central_bank = NA,
  government = NA
) {
  obj <- data.frame(
    nom = nom,
    population = population,
    devise = devise,
    GDP = GDP,
    unemployment = unemployment,
    inflation = inflation,
    central_bank = central_bank,
    government = government
  )
  
  attr(obj, "class") <- "pays"
  obj
}

print.pays <- function(obj) {
  cat("Pays: ", obj$nom, "\n", sep = "")
  cat("  population: ", obj$population, "\n", sep = "")
  cat("  devise: ", obj$devise, "\n", sep = "")
  cat("  GDP: ", obj$GDP, "\n", sep = "")
  cat("  unemployment: ", obj$unemployment, "\n", sep = "")
  cat("  inflation: ", obj$inflation, "\n", sep = "")
}
