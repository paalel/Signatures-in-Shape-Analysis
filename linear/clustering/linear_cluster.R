library(data.table)

#signature
data1 <- c(0.0, 0.023321340360317293, 1.5345184882440883, 1.5344882248242326, 0.023321340360317293, 0.0, 1.546379130236141, 1.5463482499299932, 1.5345184882440883, 1.546379130236141, 0.0, 0.009637356416431181, 1.5344882248242326, 1.5463482499299932, 0.009637356416431181, 0.0)

#dynamic distance
data2 <- c(0.0, 0.10755307388160833, 1.9046167180188565, 1.8639943234207124, 0.10755307388160833, 0.0, 1.9211288775361128, 1.891135954151157, 1.9046167180188565, 1.9211288775361128, 0.0, 0.06614667554278691, 1.8639943234207124, 1.891135954151157, 0.06614667554278691, 0.0)

distance_matrix1 <- matrix(data1, nrow = 4, ncol = 4)
row.names(distance_matrix1) <- c("a","b","c", "d")
distribution1 <- as.dist(distance_matrix1)

distance_matrix2 <- matrix(data2, nrow = 4, ncol = 4)
row.names(distance_matrix2) <- c("a","b","c", "d")
distribution2 <- as.dist(distance_matrix2)

hc1 <- hclust(distribution1, method = "single")
hc2 <- hclust(distribution2, method = "single")

library("ggplot2")
library("ggdendro")
p1 <- ggdendrogram(hc1, rotate = TRUE, theme_dendro = FALSE)
p1 <- p1 + labs(title="log_signature distance", x ="", y = "")
p2 <- ggdendrogram(hc2, rotate = TRUE, theme_dendro = FALSE)
p2 <- p2 + labs(title="dynamic distance", x ="", y = "")

library(gridExtra)

grid.arrange(p1, p2, ncol=2)

