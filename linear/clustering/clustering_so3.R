

setwd("/home/paalel/dev/master/code/so3/clustering/")
data <- read.csv("data/similarity.csv", header = TRUE)
names <- read.csv("data/names.csv", header = TRUE)[,2]
library(data.table)
distance_matrix <- as.matrix(dcast(data, animation_id1 ~ animation_id2))
distance_matrix <- distance_matrix[,-1]
distribution <- as.dist(distance_matrix)
mds.coor <- cmdscale(distribution)
plot(mds.coor[,1], mds.coor[,2], type="n", xlab="", ylab="")
text(jitter(mds.coor[,1]), jitter(mds.coor[,2]),
       names, cex=0.8)
abline(h=0,v=0,col="gray75")
library(cluster)
pamy <- pam(distance_matrix, 2)
(kmcol <- pamy$clustering)