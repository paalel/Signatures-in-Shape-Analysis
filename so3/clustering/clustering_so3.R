library(data.table)
library("ggplot2")
library("ggdendro")

library(wesanderson)
color <- as.array(wes_palettes$Darjeeling1)
map_color <- function(word) {
  if(grepl("run",word)) {
    return (color[1])
  }
  if(grepl("walk",word)) {
    return (color[2])
  }
  if(grepl("jump",word)) {
    return (color[3])
  }
  return (color[5])
}
map_names <- function(word) {
  if(grepl("run",word)) {
    return ("run")
  }
  if(grepl("walk",word)) {
    return ("walk")
  }
  if(grepl("jump",word)) {
    return ("jump")
  }
  return ("nan")
}


path <- "PATH"
setwd(path)
system("./fetch_csv.sh")
data <- read.csv("data/similarity.csv", header = TRUE)
names <- read.csv("data/names.csv", header = TRUE)[,2]
distance_matrix <- as.matrix(dcast(data, animation_id1 ~ animation_id2))[,-1]
row.names(distance_matrix) <- as.array(names)
distribution <- as.dist(distance_matrix)

title <- ""
mds.coor <- cmdscale(distribution, k=2)
plot(mds.coor[,1], mds.coor[,2], type="n", xlab="", ylab="", main=title, yaxt='n',xaxt='n')
grid(5, 5, lwd = 2, lty=1, col="grey95")
par(mar=c(0.1,0.1,0.1,0.1))
rect(par("usr")[1], par("usr")[3], par("usr")[2], par("usr")[4], col = "transparent")
text(jitter(mds.coor[,1]), jitter(mds.coor[,2]), unlist(Map(map_names, names)),cex=0.8, col=unlist(Map(map_color, names)))
theme(text=element_text(family = "serif"))


hc <- hclust(distribution, method = "single")
ggdendrogram(hc, rotate = TRUE, theme_dendro = FALSE) + theme(
  text = element_text(family = "serif"),
  panel.background = element_rect(fill = "white", colour = "grey95",
                                  size = 2, linetype = "solid"),
  panel.grid.major = element_line( size = 0.8, linetype = 'solid',
                                  colour = "grey95"), 
  panel.grid.minor = element_line(size = 0.8, linetype = 'solid',
                                  colour = "grey95")
  )

