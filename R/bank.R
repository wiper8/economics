#' client generator
#'
#' @param id un entier : id de l'habitant.
#' @param compte_cheque un numeric : montant d'argent liquide déposée dans le
#'   compte chèque.
#' @param CPG une liste : tous les CPG détenus.
#' @param dette une liste : toutes les dettes détenues.
#'
#' @return objet de classe "client".
#' @export
#'
#' @examples
#' client(
#'   7,
#'   800,
#'   list(
#'     CPG(1000, 0.03, 5, 3),
#'     CPG(2000, 0.035, 6, 2)
#'   ),
#'   list(
#'     dette(1000, 0.03, 5, 3),
#'     dette(2000, 0.035, 6, 2)
#'   )
#' )
client <- function(
  id = NA,
  compte_cheque = NA,
  CPG = NA,
  dette = NA
) {
  obj <- list(
    id = id,
    compte_cheque = compte_cheque,
    CPG = CPG,
    dette = dette
  )

  attr(obj, "class") <- "client"
  obj
}

print.client <- function(obj) {
  cat("Client: \n")
  cat("  compte_cheque: ", obj$compte_cheque, "\n", sep = "")
}

bank <- function(
  pays = NA,
  devise = NA,
  clients = NA,
  reserve = NA,
  actifs_liquides = NA,
  bonds = NA,
  credit = NA
) {
  obj <- list(
    pays = pays,
    devise = devise,
    clients = clients,
    reserve = sum(sapply(clients, function(client) {
      client$compte_cheque * 0.1 #à vérifier si inclure les CPG, et les prêts, blabla
    })
    )
  )

  attr(obj, "class") <- "bank"
  obj
}
