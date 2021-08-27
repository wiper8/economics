#' bond generator
#'
#' @param face_value un numeric : valeur nominale du bond.
#' @param interest un numeric : taux d'intérêt du bond.
#' @param expiration un numeric : durée totale du bond.
#' @param time_left un numeric : durée restante du bond.
#' @param cash_flow un numeric : montant qui sera versé à la fin de l'année.
#'
#' @return objet de classe "bond".
#' @export
#'
#' @examples
#' bond(
#'   1000,
#'   0.03,
#'   30,
#'   18
#' )
bond <- function(
  
  #attributs
  face_value = 0,
  interest = 0,
  expiration = 0,
  time_left = 0,
  cash_flow = NA
  
) {
  obj <- list(
    face_value = face_value,
    interest = interest,
    expiration = expiration,
    time_left = time_left,
    cash_flow = ifelse(time_left == 1, (1 + interest) * face_value, interest * face_value)
  )
  attr(obj, "class") <- "bond"
  obj
}

# print method
print.bond <- function(obj) {
  cat("Bond: \n")
  cat("  face value: ", obj$face_value, "\n", sep = "")
  cat("  interest: ", obj$interest, "\n", sep = "")
  cat("  expiration: ", obj$expiration, "\n", sep = "")
  cat("  time left: ", obj$time_left, "\n", sep = "")
  cat("  cash flow: ", obj$cash_flow, "\n", sep = "")
}


#' CPG generator
#'
#' @param face_value un numeric : valeur nominale du CPG.
#' @param interest un numeric : taux d'intérêt du CPG.
#' @param expiration un numeric : durée totale du CPG.
#' @param time_left un numeric : durée restante du CPG.
#' @param cash_flow un numeric : montant qui sera versé à la fin de l'année.
#'
#' @return objet de classe "CPG".
#' @export
#'
#' @examples
#' CPG(
#'   1000,
#'   0.03,
#'   30,
#'   18
#' )
CPG <- function(
  
  #attributs
  face_value = 0,
  interest = 0,
  expiration = 0,
  time_left = 0,
  cash_flow = NA
  
) {
  obj <- list(
    face_value = face_value,
    interest = interest,
    expiration = expiration,
    time_left = time_left,
    cash_flow = ifelse(time_left == 1, (1 + interest) * face_value, interest * face_value)
  )
  attr(obj, "class") <- "bond"
  obj
}

# print method
print.CPG <- function(obj) {
  cat("CPG: \n")
  cat("  face value: ", obj$face_value, "\n", sep = "")
  cat("  interest: ", obj$interest, "\n", sep = "")
  cat("  expiration: ", obj$expiration, "\n", sep = "")
  cat("  time left: ", obj$time_left, "\n", sep = "")
  cat("  cash flow: ", obj$cash_flow, "\n", sep = "")
}

#' dette generator
#'
#' @param face_value un numeric : valeur nominale du dette.
#' @param interest un numeric : taux d'intérêt du dette.
#' @param expiration un numeric : durée totale du dette.
#' @param time_left un numeric : durée restante du dette.
#' @param cash_flow un numeric : montant qui sera versé à la fin de l'année.
#'
#' @return objet de classe "dette".
#' @export
#'
#' @examples
#' dette(
#'   1000,
#'   0.03,
#'   30,
#'   18
#' )
dette <- function(
  
  #attributs
  face_value = 0,
  interest = 0,
  expiration = 0,
  time_left = 0,
  cash_flow = NA
  
) {
  obj <- list(
    face_value = face_value,
    interest = interest,
    expiration = expiration,
    time_left = time_left,
    cash_flow = ifelse(time_left == 1, (1 + interest) * face_value, interest * face_value)
  )
  attr(obj, "class") <- "bond"
  obj
}

# print method
print.dette <- function(obj) {
  cat("dette: \n")
  cat("  face value: ", obj$face_value, "\n", sep = "")
  cat("  interest: ", obj$interest, "\n", sep = "")
  cat("  expiration: ", obj$expiration, "\n", sep = "")
  cat("  time left: ", obj$time_left, "\n", sep = "")
  cat("  cash flow: ", obj$cash_flow, "\n", sep = "")
}
