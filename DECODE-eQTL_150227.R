# Detect eQTL by dynamic slicing.
# Songpeng Zu
# 2015-02-27

# Gene Expression Data by Zhirui Hu.

#-- load the libraries
library(Rcpp) # used for DECODE
library(dynslicing) # used for DECODE
library(data.table) # used for loading big data
library(stringr) # used for getSampleIds
#-- Get the input parameters.
args <- commandArgs(trailingOnly = TRUE)

startpoint <- strtoi(args[2]) # gene lable start 
startpoint <- strtoi(args[3]) # gene lable end
gene_residual <- fread(args[1],header=TRUE) # Read gene residuals' matrix

#-- Get the genes' name, samples' name and gene_residual_matrix
gene_samplenm <- colnames(gene_residual)[2:ncol(gene_residual)]
genenm <- gene_residual[,1,with=FALSE]
gene_residual_matrix <- as.matrix(gene_residual[1:nrow(gene_residual),2:ncol(gene_residual),with=FALSE])




