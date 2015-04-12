
#prepare dummy data

set.seed(993)
x <- 1:300
y <- sin(x/20) + rnorm(300,sd=.1)
y[251:255] <- NA

#assuming you have a filter function, plot graphs
# Plot the unsmoothed data (gray)
plot(x, y, type="l", col=grey(.5))
# Draw gridlines
grid()

# Smoothed with lag:
# average of current sample and 19 previous samples (red)
f20 <- rep(1/20, 20)
# [1] 0.05 0.05 0.05 0.05 0.05 0.05 0.05 0.05 0.05 0.05 0.05 0.05 0.05 0.05 0.05
#[16] 0.05 0.05 0.05 0.05 0.05
y_lag <- filter(y, f20, sides=1)
lines(x, y_lag, col="red")

# Smoothed symmetrically:
# average of current sample, 10 future samples, and 10 past samples (blue)
f21 <- rep(1/21,21)
# [1] 0.048 0.048 0.048 0.048 0.048 0.048 0.048 0.048 0.048 0.048 0.048 0.048
#[13] 0.048 0.048 0.048 0.048 0.048 0.048 0.048 0.048 0.048
y_sym <- filter(y, f21, sides=2)
lines(x, y_sym, col="blue")



