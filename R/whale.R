whale <- function(
  move_up = FALSE,
  outstanding_shares = 990010000,
  market_cap = 694000000000,
  whale_total_invested = 39030286000,
  courbe_agrege = function(P) market_cap / P,
  courbe_whale = function(P) whale_total_invested / P
) {
  cat(" Le prix passerait de ", round(market_cap / outstanding_shares, 2), " à ", round(optimise(function(P) (courbe_agrege(P) + ifelse(move_up, 1, -1) * courbe_whale(P) - outstanding_shares) ^ 2, c(0, 1000))$minimum, 2))
}


#TODO faire l'équivalent mais avec les cas comme gamestop où une bande de dégénérés achètent un tas de call option out of the money et que des hedge fund achète.
