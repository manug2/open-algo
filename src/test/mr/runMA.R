
#try to read data from 
us <- read.csv ("../../../../../../../../feeds-repo/samples/DAT_NT_USDSGD_T_LAST_201408.csv", 
                header=FALSE, sep=";" , nrows = 10000)
#prepare dummy data

set.seed(993)
x <- 1:300
y <- sin(x/20) + rnorm(300,sd=.1)
y[251:255] <- NA

x <- us[,c(1)]
y <- us[,c(2)]

source ("../../../../../../main/com/open/algo/strat/mr/sma.R")


